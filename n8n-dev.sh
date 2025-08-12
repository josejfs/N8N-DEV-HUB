#!/bin/bash

# n8n Development Environment Manager
# Uso: ./n8n-dev.sh [start|stop|restart|sync|status|logs|backup|clean]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
SYNC_SCRIPT="$PROJECT_DIR/n8n_sync.py"
DB_SCRIPT="$PROJECT_DIR/db_access.py"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[n8n-dev]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

check_dependencies() {
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não está instalado"
        exit 1
    fi
}

setup_python_environment() {
    log "Configurando ambiente Python..."
    
    # Verificar se venv existe, se não criar
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        info "Criando ambiente virtual Python..."
        python3 -m venv "$PROJECT_DIR/venv"
        if [ $? -ne 0 ]; then
            error "Falha ao criar ambiente virtual"
            return 1
        fi
        log "✅ Ambiente virtual criado"
    else
        log "Ambiente virtual já existe"
    fi
    
    # Ativar ambiente virtual
    info "Ativando ambiente virtual..."
    source "$PROJECT_DIR/venv/bin/activate"
    
    if [ -z "$VIRTUAL_ENV" ]; then
        error "Falha ao ativar ambiente virtual"
        return 1
    fi
    
    log "✅ Ambiente virtual ativo: $VIRTUAL_ENV"
    
    # Atualizar pip
    info "Atualizando pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Instalar dependências do requirements.txt se existir
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        info "Instalando dependências do requirements.txt..."
        pip install -r "$PROJECT_DIR/requirements.txt"
        if [ $? -eq 0 ]; then
            log "✅ Dependências instaladas com sucesso"
        else
            warn "Algumas dependências falharam, tentando instalação individual..."
            install_python_deps_fallback
        fi
    else
        warn "requirements.txt não encontrado, instalando dependências básicas..."
        install_python_deps_fallback
    fi
}

install_python_deps_fallback() {
    log "Instalando dependências Python individualmente..."
    
    local deps=("requests" "watchdog" "pandas")
    for dep in "${deps[@]}"; do
        if ! python -c "import $dep" 2>/dev/null; then
            info "Instalando $dep..."
            pip install "$dep"
        else
            info "$dep já instalado"
        fi
    done
}

start_n8n() {
    log "Iniciando ambiente n8n..."
    
    check_dependencies
    
    # Configurar ambiente Python automaticamente
    if ! setup_python_environment; then
        error "Falha na configuração do ambiente Python"
        return 1
    fi
    
    # Parar containers antigos se existirem
    docker stop n8n 2>/dev/null || true
    docker rm n8n 2>/dev/null || true
    
    # Criar diretórios necessários
    mkdir -p "$PROJECT_DIR/n8n_data"
    mkdir -p "$PROJECT_DIR/workflows"
    
    # Corrigir permissões
    sudo chown -R $USER:$USER "$PROJECT_DIR/workflows" "$PROJECT_DIR/n8n_data" 2>/dev/null || true
    chmod -R 755 "$PROJECT_DIR/workflows" "$PROJECT_DIR/n8n_data" 2>/dev/null || true
    
    # Parar containers do docker-compose se existirem
    cd "$PROJECT_DIR"
    docker-compose down 2>/dev/null || true
    
    # Detectar versão compatível do n8n
    log "Detectando versão compatível do n8n..."
    if ! "$PROJECT_DIR/detect_n8n_version.sh"; then
        warn "Falha na detecção automática, usando versão padrão 0.234.0"
        sed -i 's/image: n8nio\/n8n:.*/image: n8nio\/n8n:0.234.0/' "$PROJECT_DIR/docker-compose.yml"
    fi
    
    # Iniciar containers
    docker-compose up -d
    
    # Aguardar n8n inicializar
    log "Aguardando n8n inicializar..."
    local max_attempts=60
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:5678 > /dev/null 2>&1; then
            log "✅ n8n está rodando em http://localhost:5678"
            info "Usuário: admin | Senha: admin123"
            break
        fi
        sleep 2
        attempt=$((attempt + 1))
        if [ $((attempt % 10)) -eq 0 ]; then
            info "Ainda aguardando n8n... (${attempt}/${max_attempts})"
        fi
    done
    
    if [ $attempt -eq $max_attempts ]; then
        warn "n8n demorou para inicializar. Verifique os logs com: ./n8n-dev.sh logs"
    fi
    
    # Aguardar banco estar disponível
    log "Aguardando banco de dados..."
    attempt=0
    while [ $attempt -lt 30 ]; do
        if [ -f "$PROJECT_DIR/n8n_data/database.sqlite" ]; then
            break
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    # Iniciar sincronização automaticamente
    log "Iniciando sincronização bidirecional..."
    start_sync
    
    log "🚀 Ambiente pronto!"
    info "n8n: http://localhost:5678 (admin/admin123)"
    info "Sincronização: Ativa"
    info "Workflows: $PROJECT_DIR/workflows"
}

stop_n8n() {
    log "Parando ambiente n8n..."
    
    # Parar sincronização se estiver rodando
    if pgrep -f "n8n_sync.py" > /dev/null; then
        log "Parando sincronização..."
        pkill -f "n8n_sync.py" || true
    fi
    
    # Parar containers
    cd "$PROJECT_DIR"
    docker-compose down
    
    log "✅ Ambiente parado"
}

restart_n8n() {
    log "Reiniciando ambiente n8n..."
    stop_n8n
    sleep 2
    start_n8n
}

start_sync() {
    log "Iniciando sincronização bidirecional..."
    
    if pgrep -f "n8n_sync.py" > /dev/null; then
        warn "Sincronização já está rodando"
        return
    fi
    
    # Garantir que ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        info "Ativando ambiente virtual para sincronização..."
        source "$PROJECT_DIR/venv/bin/activate"
    fi
    
    cd "$PROJECT_DIR"
    nohup python "$SYNC_SCRIPT" > sync.log 2>&1 &
    
    sleep 2
    if pgrep -f "n8n_sync.py" > /dev/null; then
        log "✅ Sincronização iniciada (PID: $(pgrep -f n8n_sync.py))"
        info "Logs em: $PROJECT_DIR/sync.log"
    else
        error "Falha ao iniciar sincronização"
    fi
}

stop_sync() {
    log "Parando sincronização..."
    if pgrep -f "n8n_sync.py" > /dev/null; then
        pkill -f "n8n_sync.py"
        log "✅ Sincronização parada"
    else
        warn "Sincronização não está rodando"
    fi
}

show_status() {
    log "Status do ambiente n8n:"
    echo
    
    # Status Docker
    info "Docker Containers:"
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        docker-compose ps
    else
        warn "Nenhum container rodando"
    fi
    
    # Status banco SQLite
    info "Banco de dados SQLite:"
    if [ -f "$PROJECT_DIR/n8n_data/database.sqlite" ]; then
        SIZE=$(du -h "$PROJECT_DIR/n8n_data/database.sqlite" | cut -f1)
        echo "✅ database.sqlite ($SIZE)"
    else
        echo "❌ database.sqlite não encontrado"
    fi
    
    echo
    
    # Status sincronização
    info "Sincronização:"
    if pgrep -f "n8n_sync.py" > /dev/null; then
        echo "✅ Rodando (PID: $(pgrep -f n8n_sync.py))"
    else
        echo "❌ Parada"
    fi
    
    echo
    
    # Verificar conectividade
    info "Conectividade:"
    if curl -s http://localhost:5678/healthz > /dev/null; then
        echo "✅ n8n acessível em http://localhost:5678"
    else
        echo "❌ n8n não acessível"
    fi
    
    echo
    
    # Estatísticas de arquivos
    info "Workflows locais:"
    WORKFLOW_COUNT=$(find "$PROJECT_DIR/workflows" -name "*.json" -not -path "*/\_archived/*" 2>/dev/null | wc -l)
    ARCHIVED_COUNT=$(find "$PROJECT_DIR/workflows/_archived" -name "*.json" 2>/dev/null | wc -l)
    echo "📁 $WORKFLOW_COUNT workflows ativos"
    if [ $ARCHIVED_COUNT -gt 0 ]; then
        echo "🗃️  $ARCHIVED_COUNT workflows arquivados"
    fi
}

show_logs() {
    log "Exibindo logs..."
    
    case "${2:-all}" in
        "n8n")
            docker-compose logs -f n8n
            ;;
        "postgres")
            docker-compose logs -f postgres
            ;;
        "sync")
            if [ -f "$PROJECT_DIR/sync.log" ]; then
                tail -f "$PROJECT_DIR/sync.log"
            else
                warn "Arquivo de log da sincronização não encontrado"
            fi
            ;;
        "all"|*)
            info "Logs dos containers (Ctrl+C para sair):"
            docker-compose logs -f
            ;;
    esac
}

create_backup() {
    log "Criando backup..."
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_DIR="$PROJECT_DIR/backups/$TIMESTAMP"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup workflows
    if [ -d "$PROJECT_DIR/workflows" ] && [ "$(ls -A $PROJECT_DIR/workflows 2>/dev/null)" ]; then
        cp -r "$PROJECT_DIR/workflows" "$BACKUP_DIR/"
        info "✅ Workflows copiados"
    fi
    
    # Backup banco de dados
    if [ -f "$PROJECT_DIR/n8n_data/database.sqlite" ]; then
        python3 "$DB_SCRIPT" -c "backup" --output "$BACKUP_DIR/database_$TIMESTAMP.sqlite"
        info "✅ Banco de dados copiado"
    fi
    
    # Backup configurações
    cp "$PROJECT_DIR/docker-compose.yml" "$BACKUP_DIR/"
    
    log "✅ Backup criado em: $BACKUP_DIR"
}

clean_environment() {
    log "Limpando ambiente..."
    
    read -p "Isso removerá TODOS os dados do n8n. Continuar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Operação cancelada"
        return
    fi
    
    stop_n8n
    
    # Remover volumes e dados
    docker-compose down -v
    rm -rf "$PROJECT_DIR/n8n_data"
    rm -rf "$PROJECT_DIR/workflows"
    
    # Limpar logs
    rm -f "$PROJECT_DIR/sync.log"
    
    log "✅ Ambiente limpo"
}

manage_archived_workflows() {
    log "Gerenciando workflows arquivados..."
    
    ARCHIVED_DIR="$PROJECT_DIR/workflows/_archived"
    
    if [ ! -d "$ARCHIVED_DIR" ] || [ -z "$(ls -A "$ARCHIVED_DIR" 2>/dev/null)" ]; then
        info "Nenhum workflow arquivado encontrado"
        return
    fi
    
    echo "Workflows arquivados disponíveis:"
    echo
    
    local count=1
    local files=()
    
    for file in "$ARCHIVED_DIR"/*.json; do
        if [ -f "$file" ]; then
            basename_file=$(basename "$file")
            echo "$count. $basename_file"
            files+=("$file")
            ((count++))
        fi
    done
    
    echo
    echo "Opções:"
    echo "r) Restaurar workflow"
    echo "d) Deletar permanentemente"
    echo "l) Listar detalhes"
    echo "q) Voltar"
    
    read -p "Escolha uma opção: " -n 1 -r
    echo
    
    case $REPLY in
        [Rr])
            read -p "Número do workflow para restaurar: " num
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -lt "$count" ]; then
                restore_workflow "${files[$((num-1))]}"
            else
                warn "Número inválido"
            fi
            ;;
        [Dd])
            read -p "Número do workflow para deletar PERMANENTEMENTE: " num
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -lt "$count" ]; then
                read -p "CONFIRMA exclusão permanente? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm "${files[$((num-1))]}"
                    log "Workflow deletado permanentemente"
                fi
            else
                warn "Número inválido"
            fi
            ;;
        [Ll])
            read -p "Número do workflow para ver detalhes: " num
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -lt "$count" ]; then
                show_workflow_details "${files[$((num-1))]}"
            else
                warn "Número inválido"
            fi
            ;;
    esac
}

restore_workflow() {
    local archived_file="$1"
    local filename=$(basename "$archived_file")
    local restored_name="${filename%_deleted_*}.json"
    local restore_path="$PROJECT_DIR/workflows/$restored_name"
    
    if [ -f "$restore_path" ]; then
        warn "Workflow $restored_name já existe. Substituir? (y/N)"
        read -p "" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    cp "$archived_file" "$restore_path"
    rm "$archived_file"
    log "✅ Workflow restaurado: $restored_name"
}

show_workflow_details() {
    local file="$1"
    info "Detalhes do workflow:"
    
    if command -v jq >/dev/null 2>&1; then
        jq -r '.name, .meta.description // "Sem descrição"' "$file" 2>/dev/null || cat "$file"
    else
        cat "$file"
    fi
}

show_help() {
    echo "n8n Development Environment Manager"
    echo
    echo "Uso: $0 [comando] [opções]"
    echo
    echo "Comandos:"
    echo "  start     - Inicia o ambiente n8n"
    echo "  stop      - Para o ambiente n8n"
    echo "  restart   - Reinicia o ambiente n8n"
    echo "  sync      - Gerencia sincronização"
    echo "    start   - Inicia sincronização bidirecional"
    echo "    stop    - Para sincronização"
    echo "  status    - Mostra status do ambiente"
    echo "  logs      - Mostra logs [n8n|postgres|sync|all]"
    echo "  backup    - Cria backup dos dados"
    echo "  clean     - Remove todos os dados (cuidado!)"
    echo "  db        - Abre interface de banco de dados"
    echo "  archived  - Gerenciar workflows arquivados"
    echo "  help      - Mostra esta ajuda"
    echo
    echo "Exemplos:"
    echo "  $0 start              # Inicia ambiente completo"
    echo "  $0 logs n8n           # Mostra apenas logs do n8n"
    echo "  $0 sync start         # Inicia apenas sincronização"
    echo
    echo "URLs:"
    echo "  n8n Interface: http://localhost:5678"
    echo "  PostgreSQL: localhost:5432 (n8n/n8n123)"
}

# Comando principal
case "${1:-help}" in
    "start")
        start_n8n
        ;;
    "stop")
        stop_n8n
        ;;
    "restart")
        restart_n8n
        ;;
    "sync")
        case "${2:-help}" in
            "start")
                start_sync
                ;;
            "stop")
                stop_sync
                ;;
            *)
                echo "Uso: $0 sync [start|stop]"
                ;;
        esac
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$@"
        ;;
    "backup")
        create_backup
        ;;
    "clean")
        clean_environment
        ;;
    "db")
        # Ativar ambiente virtual se necessário
        if [ -z "$VIRTUAL_ENV" ]; then
            info "Ativando ambiente virtual..."
            source "$PROJECT_DIR/venv/bin/activate"
        fi
        python "$DB_SCRIPT"
        ;;
    "archived")
        manage_archived_workflows
        ;;
    "help"|*)
        show_help
        ;;
esac