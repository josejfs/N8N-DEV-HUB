# Ambiente de Desenvolvimento n8n 🚀

Ambiente de desenvolvimento profissional para n8n com sincronização bidirecional entre workflows visuais e arquivos JSON locais.

## 📋 Características

- ✅ **Sincronização Bidirecional**: Edite workflows via interface ou código
- ✅ **Detecção Automática**: Encontra versão compatível do n8n automaticamente  
- ✅ **Acesso Direto ao Banco**: SQLite acessível para consultas avançadas
- ✅ **Monitoramento em Tempo Real**: Mudanças sincronizadas instantaneamente
- ✅ **Scripts de Gerenciamento**: Comandos simples para todas as operações
- ✅ **Docker Otimizado**: Configuração limpa e eficiente

## 🛠️ Instalação

### Pré-requisitos
- Docker e Docker Compose
- Python 3.8+
- Git

### Configuração Rápida
```bash
# Clone ou acesse o diretório
cd N8N

# Dar permissões aos scripts
chmod +x *.sh

# PRONTO! O script start faz todo o resto automaticamente
./n8n-dev.sh start
```

### Configuração Automática
O script `./n8n-dev.sh start` faz **TUDO** automaticamente:
- ✅ Cria ambiente virtual Python (`venv/`)
- ✅ Ativa ambiente virtual automaticamente
- ✅ Atualiza pip para versão mais recente
- ✅ Instala todas as dependências do `requirements.txt`
- ✅ Detecta versão compatível do n8n
- ✅ Configura Docker e inicia containers
- ✅ Corrige permissões das pastas
- ✅ Inicia sincronização bidirecional

## 🐍 Ambiente Virtual Python

**IMPORTANTE**: Este projeto usa ambiente virtual Python. **SEMPRE** ative antes de usar qualquer script Python.

### Primeira Configuração
```bash
# Criar ambiente virtual (apenas uma vez)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Uso Diário
```bash
# Opção 1: Usar script auxiliar (recomendado)
source activate.sh

# Opção 2: Ativar manualmente
source venv/bin/activate

# Seu prompt deve mostrar: (venv) user@host:~/N8N$
# Agora pode usar os scripts Python
```

### 🚀 Início Automático
**NOVO**: Agora é ainda mais fácil! Um único comando faz tudo:
```bash
./n8n-dev.sh start
```
**Não precisa mais**:
- ❌ Criar venv manualmente
- ❌ Ativar ambiente virtual
- ❌ Instalar dependências
- ❌ Configurar permissões

**Tudo é automático!** 🎉

### Desativar (opcional)
```bash
# Para sair do ambiente virtual
deactivate
```

## 🚀 Como Usar

### Inicialização Completa
```bash
# Ativar ambiente virtual (sempre necessário)
source venv/bin/activate

# Iniciar ambiente completo
./n8n-dev.sh start
```
Este comando faz TUDO automaticamente:
- Detecta versão compatível do n8n
- Corrige permissões das pastas
- Inicia containers Docker
- Aguarda n8n estar funcionando
- Inicia sincronização bidirecional

### Outros Comandos
```bash
# Todos os comandos ativam ambiente virtual automaticamente!

# Ver status do ambiente
./n8n-dev.sh status

# Parar ambiente
./n8n-dev.sh stop

# Reiniciar ambiente
./n8n-dev.sh restart

# Ver logs
./n8n-dev.sh logs

# Criar backup
./n8n-dev.sh backup

# Limpar dados (CUIDADO!)
./n8n-dev.sh clean

# Acessar banco de dados (ativa venv automaticamente)
./n8n-dev.sh db

# Ativar apenas ambiente virtual
source activate.sh
```

### 🎯 Comandos Manuais (apenas se necessário)
```bash
# Ativar ambiente primeiro
source activate.sh

# Executar scripts Python diretamente
python n8n_sync.py
python db_access.py
```

## 🔄 Sincronização Bidirecional

### Interface → Arquivos
1. Crie/edite workflows na interface do n8n
2. Arquivos JSON são automaticamente criados em `./workflows/`
3. Use estes arquivos para versionamento no Git

### Arquivos → Interface
1. Edite arquivos JSON na pasta `./workflows/`
2. Mudanças aparecem automaticamente na interface do n8n
3. Ideal para desenvolvimento programático

### Exemplo de Workflow JSON
```json
{
  "name": "Meu_Workflow",
  "active": true,
  "nodes": [
    {
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "position": [250, 300],
      "parameters": {}
    }
  ],
  "connections": {},
  "settings": {},
  "tags": []
}
```

## 🌐 Acesso

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **n8n Interface** | http://localhost:5678 | admin / admin123 |
| **Banco SQLite** | `./n8n_data/database.sqlite` | Via script db_access.py |

## 📁 Estrutura do Projeto

```
N8N/
├── docker-compose.yml          # Configuração Docker
├── n8n-dev.sh                 # Script principal de gerenciamento
├── n8n_sync.py                # Sincronização bidirecional
├── db_access.py               # Interface para banco SQLite
├── detect_n8n_version.sh      # Detecção automática de versão
├── requirements.txt           # Dependências Python
├── n8n_data/                  # Dados do n8n (banco, configs)
│   └── database.sqlite        # Banco de dados SQLite
├── workflows/                 # Workflows como arquivos JSON
└── README.md                  # Este arquivo
```

## 🔧 Scripts Utilitários

### n8n_sync.py
Sincronização em tempo real entre banco SQLite e arquivos JSON.
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Execução manual
python3 n8n_sync.py
```

### db_access.py
Interface para acessar diretamente o banco SQLite do n8n.
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Abrir interface interativa
python3 db_access.py

# Opções disponíveis:
# 1. Listar workflows
# 2. Ver execuções recentes
# 3. Exportar workflow
# 4. Criar backup
# 5. Consulta SQL interativa
```

### detect_n8n_version.sh
Detecta automaticamente a versão compatível do n8n.
```bash
# Execução manual
./detect_n8n_version.sh
```

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente
Edite `docker-compose.yml` para personalizar:

```yaml
environment:
  - N8N_BASIC_AUTH_USER=admin          # Usuário de login
  - N8N_BASIC_AUTH_PASSWORD=admin123   # Senha de login
  - N8N_HOST=0.0.0.0                   # Host de binding
  - N8N_PORT=5678                      # Porta interna
  - GENERIC_TIMEZONE=America/Sao_Paulo # Fuso horário
  - DB_TYPE=sqlite                     # Tipo do banco
  - N8N_LOG_LEVEL=info                 # Nível de log
```

### Personalização da Sincronização
Edite `n8n_sync.py` para ajustar:
- Intervalo de sincronização (linha 261: `await asyncio.sleep(30)`)
- Padrões de arquivos monitorados
- Tratamento de erros personalizados

## 🐳 Docker

### Comandos Docker Diretos
```bash
# Ver containers
docker ps

# Logs do n8n
docker logs n8n-n8n-1

# Restart manual
docker restart n8n-n8n-1

# Acessar container
docker exec -it n8n-n8n-1 sh
```

## 📊 Monitoramento

### Status do Sistema
```bash
./n8n-dev.sh status
```
Mostra:
- Status dos containers Docker
- Estado da sincronização
- Conectividade do n8n
- Informações do banco SQLite
- Contador de workflows locais

### Logs em Tempo Real
```bash
# Todos os logs
./n8n-dev.sh logs

# Apenas n8n
./n8n-dev.sh logs n8n

# Apenas sincronização
./n8n-dev.sh logs sync
```

## 🔍 Solução de Problemas

### n8n não inicia
1. Verificar se Docker está rodando
2. Testar detecção de versão: `./detect_n8n_version.sh`
3. Ver logs: `./n8n-dev.sh logs`

### Sincronização não funciona
1. Verificar se banco existe: `ls -la n8n_data/database.sqlite`
2. Ativar venv e testar: `source venv/bin/activate && python3 n8n_sync.py`
3. Verificar permissões: `ls -la workflows/`

### Erro de permissões
```bash
# Corrigir manualmente
sudo chown -R $USER:$USER n8n_data workflows
chmod -R 755 n8n_data workflows
```

## 🚨 Backup e Restauração

### Criar Backup
```bash
./n8n-dev.sh backup
```
Cria backup em `./backups/TIMESTAMP/` contendo:
- Todos os workflows JSON
- Banco de dados SQLite
- Configurações do Docker

### Restaurar Backup
```bash
# Parar ambiente
./n8n-dev.sh stop

# Restaurar arquivos manualmente
cp -r backups/TIMESTAMP/* ./

# Reiniciar
./n8n-dev.sh start
```

## 📝 Desenvolvimento

### Criando Novos Workflows
1. **Via Interface**: Acesse http://localhost:5678 e crie visualmente
2. **Via Código**: Crie arquivo JSON em `./workflows/` seguindo o padrão

### Versionamento Git
```bash
# Adicionar workflows ao Git
git add workflows/
git commit -m "Add novo workflow de processamento"

# Workflows são sincronizados automaticamente!
```

### Debug
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Verificar banco diretamente
python3 db_access.py

# Monitorar sincronização
tail -f sync.log

# Testar conectividade
curl http://localhost:5678
```

## 🎯 Casos de Uso

### 1. Desenvolvimento Colaborativo
- Cada desenvolvedor trabalha com workflows localmente
- Versionamento via Git dos arquivos JSON
- Sincronização automática para testes

### 2. CI/CD
- Deploy automático de workflows
- Testes automatizados via arquivos JSON
- Backup automático antes de updates

### 3. Ambiente de Produção
- Monitoramento via logs
- Backup regular automático
- Sincronização para disaster recovery

## 📈 Performance

### Otimizações Incluídas
- ✅ Sincronização assíncrona
- ✅ Detecção de mudanças por hash MD5
- ✅ Conexões SQLite otimizadas
- ✅ Containers Docker leves
- ✅ Logs rotativos automáticos

### Métricas Típicas
- **Tempo de inicialização**: ~30-60 segundos
- **Sincronização**: Instantânea (<1 segundo)
- **Uso de memória**: ~200-500MB
- **Uso de disco**: ~50-100MB base + workflows

## 🤝 Contribuição

Melhorias bem-vindas! Areas de foco:
- Suporte a PostgreSQL
- Interface web para monitoramento
- Integração com webhooks
- Testes automatizados
- Documentação adicional

## 📄 Licença

Este projeto é de uso livre para desenvolvimento e aprendizado.

---

## 🔗 Links Úteis

- [Documentação oficial n8n](https://docs.n8n.io/)
- [Docker Hub - n8n](https://hub.docker.com/r/n8nio/n8n)
- [SQLite Documentation](https://sqlite.org/docs.html)

---

**Desenvolvido com ❤️ para automatização eficiente!**