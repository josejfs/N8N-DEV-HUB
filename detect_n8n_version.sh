#!/bin/bash

# Script para detectar versão compatível do n8n
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

test_n8n_version() {
    local version=$1
    local test_container="n8n-version-test"
    
    echo "Testando n8n:$version..."
    
    # Limpar container de teste se existir
    docker stop "$test_container" 2>/dev/null || true
    docker rm "$test_container" 2>/dev/null || true
    
    # Testar versão
    if docker run --name "$test_container" -d \
        -v "$PROJECT_DIR/n8n_data:/home/node/.n8n" \
        "n8nio/n8n:$version" > /dev/null 2>&1; then
        
        sleep 10
        
        # Verificar logs por erros
        if docker logs "$test_container" 2>&1 | grep -q "Error: Command"; then
            echo "❌ n8n:$version tem problemas de comando"
            docker stop "$test_container" 2>/dev/null || true
            docker rm "$test_container" 2>/dev/null || true
            return 1
        else
            echo "✅ n8n:$version funciona!"
            docker stop "$test_container" 2>/dev/null || true
            docker rm "$test_container" 2>/dev/null || true
            return 0
        fi
    else
        echo "❌ n8n:$version falhou ao iniciar"
        return 1
    fi
}

# Testar versões em ordem de preferência
versions=("latest" "1.19.4" "1.0.0" "0.234.0")

for version in "${versions[@]}"; do
    if test_n8n_version "$version"; then
        echo "🎯 Versão compatível encontrada: n8nio/n8n:$version"
        
        # Atualizar docker-compose.yml
        sed -i "s/image: n8nio\/n8n:.*/image: n8nio\/n8n:$version/" "$PROJECT_DIR/docker-compose.yml"
        echo "✅ docker-compose.yml atualizado"
        
        exit 0
    fi
done

echo "❌ Nenhuma versão compatível encontrada"
exit 1