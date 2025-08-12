#!/bin/bash
# Script para ativar ambiente virtual facilmente
# Uso: source activate.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Execute: ./n8n-dev.sh start"
    return 1 2>/dev/null || exit 1
fi

echo "🐍 Ativando ambiente virtual..."
source "$PROJECT_DIR/venv/bin/activate"

if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Ambiente virtual ativo: $(basename $VIRTUAL_ENV)"
    echo ""
    echo "💡 Comandos disponíveis:"
    echo "  ./n8n-dev.sh start    # Iniciar ambiente completo"
    echo "  ./n8n-dev.sh status   # Ver status"
    echo "  python n8n_sync.py    # Sincronização manual" 
    echo "  python db_access.py   # Acessar banco"
    echo "  deactivate            # Sair do ambiente virtual"
else
    echo "❌ Falha ao ativar ambiente virtual"
    return 1 2>/dev/null || exit 1
fi