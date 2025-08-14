# 🚀 N8N-DevHub

**Sistema Avançado de Gerenciamento de Workflows N8N com Sincronização Assíncrona**

[![N8N](https://img.shields.io/badge/N8N-Compatible-FF6D5A?style=flat-square&logo=n8n)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://docker.com/)

## 🎯 O que é o N8N-DevHub?

O N8N-DevHub é um sistema completo que transforma o gerenciamento de workflows N8N em uma experiência profissional e eficiente, oferecendo:

- 🔄 **Sincronização Assíncrona** em tempo real (Local ↔ N8N)
- 🎯 **Operações Específicas** por ID ou nome exato
- 🏗️ **Arquitetura MVC** profissional e organizada
- 🌍 **Multi-ambiente** com troca simples (dev ↔ prod)
- ⚡ **Interface CLI** moderna com cores e ícones
- 🐳 **Docker Ready** para desenvolvimento

## ⚡ Início Rápido

### **1. Inicializar Ambiente Completo**
```bash
# Configura Python venv + N8N Docker + dependências
./devhub init
```
*O comando `init` faz tudo automaticamente:*
- ✅ Cria ambiente virtual Python (`venv/` na raiz)
- ✅ Instala dependências (`requirements.txt`)
- ✅ Cria pasta `workflows/` se não existir
- ✅ Sobe ambiente N8N Docker
- ✅ Testa conectividade

### **2. Instalação Global (Opcional)**
Para usar `devhub` sem `./` de qualquer diretório:
```bash
# Instalar globalmente
./devhub install-global

# Agora use de qualquer lugar:
devhub list
devhub download "Demo RAG"
devhub sync-start "Demo RAG"
```

### **3. Comandos Básicos**
```bash
# Listar workflows
./devhub list          # ou apenas: devhub list

# Baixar workflow específico
./devhub download "Demo RAG"

# Iniciar sincronização em tempo real  
./devhub sync-start "Demo RAG"
```

### **3. Acessar N8N**
- 🌐 **URL**: http://localhost:5678
- 👤 **Login**: admin / admin123

## 📋 Funcionalidades Principais

### 🔄 **Sincronização Assíncrona**
Sistema que monitora mudanças em tempo real nos dois sentidos:

```bash
# Inicia monitoramento bidirecional
./devhub sync-start "Meu Workflow"

# Sistema detecta automaticamente:
# • Mudanças em arquivos locais → Envia para N8N
# • Mudanças no N8N web → Baixa para local
# • Resolve conflitos inteligentemente
```

**Como funciona:**
- 📁 **File Watcher**: Detecta mudanças em `.json` instantaneamente
- 📡 **Remote Polling**: Verifica N8N a cada X segundos
- 🚨 **Conflict Resolution**: 4 estratégias (ask/local/remote/latest)

### 🎯 **Operações Específicas**

**Por Nome (busca inteligente):**
```bash
./devhub download "Demo RAG"           # Busca fuzzy
./devhub find "email"                  # Encontra workflows
./devhub activate "Process Email"      # Gerenciar workflow
```

**Por ID Específico:**
```bash
./devhub download-id 8loOlT9y6XM4gB0D  # Download direto
./devhub sync-start --by-id 8loOlT9y6XM4gB0D
./devhub upload-id 8loOlT9y6XM4gB0D    # Upload específico
```

**Parsing Automático:** Arquivos salvos como `Nome_ID.json` permitem operações por ambos.

### 🌍 **Multi-Ambiente**

Troque entre desenvolvimento e produção mudando **apenas 1 linha** no `.env`:

```bash
# Desenvolvimento
N8N_URL=http://localhost:5678

# Produção (mude apenas esta linha!)
N8N_URL=https://n8n.empresa.com
```

## 📖 Comandos Completos

### **📋 Listagem e Status**
```bash
./devhub list                    # Workflows remotos
./devhub list-local             # Workflows locais
./devhub status                 # Comparação local vs remoto
./devhub find "termo"           # Buscar workflows
```

### **📥 Download**
```bash
./devhub download-all           # Todos os workflows
./devhub download-active        # Apenas ativos
./devhub download "Nome"        # Por nome específico  
./devhub download-id 8loOlT9y6XM4gB0D  # Por ID exato
```

### **📤 Upload**
```bash
./devhub upload-all             # Todos os workflows locais
./devhub upload workflow.json   # Arquivo específico
./devhub upload-id 8loOlT9y6XM4gB0D   # Por ID específico
```

### **🔄 Sincronização Assíncrona**
```bash
# Iniciar sync em tempo real
./devhub sync-start "Demo RAG"
./devhub sync-start --by-id 8loOlT9y6XM4gB0D
./devhub sync-start "Demo,Email,Process"  # Múltiplos

# Configurações avançadas
./devhub sync-start "Demo" --poll-interval 5 --conflict-resolution latest

# Gerenciar sincronização
./devhub sync-status            # Ver status
./devhub sync-stop              # Parar
./devhub sync-add "Novo"        # Adicionar workflow
./devhub sync-remove "Antigo"   # Remover workflow
```

### **⚙️ Gerenciamento**
```bash
./devhub activate "workflow"    # Ativar
./devhub deactivate "workflow"  # Desativar
./devhub delete "workflow"      # Remover (com confirmação)
./devhub details "workflow"     # Ver detalhes
```

### **🐳 Controle Docker**
```bash
./devhub docker start          # Iniciar ambiente
./devhub docker stop           # Parar ambiente
./devhub docker logs           # Ver logs
./devhub docker restart        # Reiniciar
./devhub docker clean          # Reset completo
```

## 🏗️ Arquitetura

### **Estrutura Organizada**
```
N8N-DevHub/
├── python/
│   └── devhub.py                # Aplicação principal Python
├── scripts/
│   ├── init-dev                # Inicializador de ambiente
│   └── dev-control             # Controle Docker
├── models/workflow_model.py     # Dados e API N8N
├── controllers/workflow_controller.py  # Lógica de negócios
├── views/cli_view.py           # Interface CLI colorida
├── utils/sync_manager.py       # Sistema assíncrono
└── docker-compose.yml          # Ambiente de desenvolvimento
```

### **Scripts Principais**
```
devhub             # Script principal (comandos unificados)
├── devhub init    # Inicializar ambiente
├── devhub docker  # Controle Docker
└── devhub ...     # Todos os comandos normais
```

## ⚙️ Configuração

### **Arquivo .env**
```bash
# ========================================
# N8N SERVER - Mude aqui para trocar ambiente
# ========================================
N8N_URL=http://localhost:5678

# Para produção:
# N8N_URL=https://n8n.empresa.com

# ========================================
# AUTHENTICATION
# ========================================
# Opção 1: API Key (recomendado)
API_N8N=sua_api_key_aqui

# Opção 2: Basic Auth (fallback)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
```

### **Instalação Manual** (opcional)
Se preferir instalar manualmente em vez de usar `./devhub init`:

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar pasta workflows
mkdir -p workflows

# 4. Subir N8N
./devhub docker start

# Dependências principais:
# - requests (API calls)
# - python-dotenv (configuração)  
# - watchdog (file watcher)
```

## 🔄 Casos de Uso

### **1. Desenvolvimento Local → Produção**
```bash
# Desenvolvimento
./devhub sync-start "API Workflow"
# Desenvolver, testar...

# Deploy para produção (mude N8N_URL no .env)
./devhub upload "API_Workflow_123.json"
```

### **2. Sincronização em Tempo Real**
```bash
# Equipe colaborativa
./devhub sync-start "Shared Workflow"

# Desenvolvedor A edita localmente → Sync automático
# Desenvolvedor B vê mudanças no N8N → Sync automático
# Conflitos são detectados e resolvidos
```

### **3. Scripts/IA Externa**
```python
# Script Python modifica workflow
import json

with open('workflows/Demo_RAG_in_n8n_8loOlT9y6XM4gB0D.json', 'r+') as f:
    workflow = json.load(f)
    workflow['nodes'][0]['parameters']['newConfig'] = 'value'
    f.seek(0)
    json.dump(workflow, f, indent=2)

# N8N-DevHub detecta mudança → Sync automático! 🚀
```

### **4. Backup e Versionamento**
```bash
# Backup contínuo
./devhub sync-start "Critical,Production,Main"

# Versionamento com Git
git add workflows/
git commit -m "Updated workflows"
git push
```

## 🚨 Resolução de Conflitos

Quando o mesmo workflow é modificado localmente E remotamente:

### **Modo Interativo** (padrão)
```
🚨 CONFLITO DETECTADO: Demo RAG
   Local atualizado: 2025-08-14 15:45:32
   Remoto atualizado: 2025-08-14 15:46:15

Estratégias de resolução:
  1. local  - Usar versão local
  2. remote - Usar versão remota
  3. latest - Usar versão mais recente
  4. skip   - Pular este conflito

Escolha uma opção (1-4):
```

### **Modo Automático**
```bash
# Estratégias automáticas
--conflict-resolution local    # Sempre usar local
--conflict-resolution remote   # Sempre usar remoto  
--conflict-resolution latest   # Sempre usar mais recente
```

## 📊 Monitoramento

### **Status da Sincronização**
```bash
./devhub sync-status
```

**Saída:**
```
🔄 Status: Rodando
📊 Workflows Monitorados: 3
⚠️ Conflitos Ativos: 1
🔄 Sincronizando: 0

Detalhes dos Workflows:
✅ Demo RAG (8loOlT9y6XM4gB0D)
    Última Sync: 14/08/2025 15:45:32

⚠️ Email Process (abc123def456)
    🚨 CONFLITO DETECTADO

🔄 API Handler (xyz789abc012)
    Última Sync: Nunca
```

### **Comparação Local vs Remoto**
```bash
./devhub status
```

Mostra workflows:
- ☁️ **Apenas Remotos**: No N8N mas não localmente
- 📁 **Apenas Locais**: Arquivos não sincronizados
- 🔄 **Em Ambos**: Sincronizados ou com diferenças

## 🎨 Interface Visual

A CLI usa cores para melhor experiência:
- 🟢 **Verde**: Sucesso, workflows ativos
- 🟡 **Amarelo**: Avisos, workflows inativos
- 🔴 **Vermelho**: Erros
- 🔵 **Azul**: Informações
- 🟦 **Ciano**: URLs, IDs

## 🌍 Instalação Global

### **Automática (Recomendada)**
```bash
# Instalar globalmente com um comando
./devhub install-global
```

O script automático:
- ✅ Cria `~/.local/bin/devhub` com caminhos absolutos
- ✅ Adiciona `~/.local/bin` ao PATH em `~/.bashrc`
- ✅ Configura PATH para sessão atual
- ✅ Testa instalação e conectividade
- ✅ Funciona de qualquer diretório do sistema

### **Manual** (se necessário)
```bash
# 1. Copiar script
cp devhub ~/.local/bin/devhub
chmod +x ~/.local/bin/devhub

# 2. Editar caminhos no script
nano ~/.local/bin/devhub
# Alterar PROJECT_DIR para caminho absoluto

# 3. Adicionar ao PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### **Verificação**
```bash
# Testar se funciona
which devhub                    # Deve mostrar ~/.local/bin/devhub
devhub help                     # Interface deve aparecer
devhub list                     # Deve listar workflows

# Se não funcionar em novo terminal:
source ~/.bashrc
```

### **Uso Global**
Após instalação, use de qualquer diretório:
```bash
cd ~
devhub list                     # Funciona!

cd /tmp  
devhub sync-start "Demo"        # Funciona!

cd /var/www
devhub download "API"           # Funciona!
```

### **Reinstalação**
Se mover o projeto ou ter problemas:
```bash
# Reinstalar automaticamente
devhub install-global           # ou
./path/to/projeto/devhub install-global
```

## 🔧 Configurações Avançadas

### **Sincronização**
```bash
# Intervalo de verificação (padrão: 10s)
--poll-interval 5

# Estratégias de conflito
--conflict-resolution ask|local|remote|latest

# Filtros
--active          # Apenas workflows ativos
--inactive        # Apenas workflows inativos  
--by-id           # Usar ID em vez de nome
--exact           # Busca exata (não fuzzy)
```

### **Filtros e Busca**
```bash
# Workflows ativos apenas
./devhub list --active
./devhub download-all --active

# Busca específica
./devhub find "email" --exact
./devhub activate --by-id 8loOlT9y6XM4gB0D
```

## 🐳 Ambiente Docker

### **Inicialização Completa**
```bash
./init-dev  # Sobe N8N + configura + testa conectividade
```

### **Controles**
```bash
./dev-control start     # Inicia ambiente
./dev-control stop      # Para ambiente
./dev-control restart   # Reinicia
./dev-control logs      # Logs em tempo real
./dev-control status    # Status containers
./dev-control clean     # Reset completo (cuidado!)
```

### **Configuração Docker**
- **Volume nomeado**: Dados isolados (não cria pasta n8n_data)
- **Workflows compartilhados**: Pasta `workflows/` linkada
- **Ambiente limpo**: Reset fácil com `clean`

## ⚡ Performance e Otimizações

### **Recomendações de Intervalo**
```bash
# Desenvolvimento (resposta rápida)
--poll-interval 5

# Produção (economia de recursos)
--poll-interval 30

# CI/CD (detecção precisa)  
--poll-interval 1
```

### **Otimizações Internas**
- **Hash Comparison**: Apenas mudanças reais são sincronizadas
- **File Watcher**: Detecção instantânea sem polling
- **Thread Pool**: Processamento paralelo
- **Debouncing**: Evita múltiplas notificações

## 🚧 Limitações

- ❌ **Credenciais**: Não sincroniza credenciais (segurança)
- ❌ **Execuções**: Não transfere histórico de execuções  
- ❌ **Binary Data**: Não sincroniza dados binários grandes
- ❌ **Webhooks**: URLs podem precisar reconfiguração

## 🎯 Benefícios

### **Para Desenvolvedores**
- 💻 Edite workflows com ferramentas locais favoritas
- 🔄 Sincronização automática sem comandos manuais
- 🤝 Colaboração em equipe com sync em tempo real
- 📝 Versionamento Git-friendly

### **Para DevOps**
- 🏗️ CI/CD via arquivos JSON
- 📊 Monitoramento em tempo real  
- 🔄 Backup contínuo automático
- 🌍 Deploy multi-ambiente simplificado

### **Para Automação**
- 🤖 Scripts externos podem modificar workflows
- ⚡ Mudanças aplicadas instantaneamente no N8N
- 🎯 Operações específicas por ID/nome
- 🔄 Integração bidirecional perfeita

## 📚 Exemplos Avançados

### **Workflow de Desenvolvimento**
```bash
# 1. Iniciar projeto
./init-dev
./devhub download-all

# 2. Desenvolver com sync
./devhub sync-start "Feature X"
# Editar localmente, ver mudanças no N8N instantaneamente

# 3. Deploy
# Mudar N8N_URL no .env para produção
./devhub upload "Feature_X_123.json"
```

### **Automação com Scripts**
```bash
# Script que roda periodicamente
#!/bin/bash
# 1. Buscar workflows específicos
./devhub find "production" > prod_workflows.txt

# 2. Backup automático
./devhub download-all --active

# 3. Commit automático
git add workflows/
git commit -m "Auto backup $(date)"
```

### **Multi-Ambiente Avançado**
```bash
# .env.dev
N8N_URL=http://localhost:5678

# .env.staging  
N8N_URL=https://staging.empresa.com

# .env.prod
N8N_URL=https://n8n.empresa.com

# Deploy pipeline
cp .env.prod .env && ./devhub upload-all
```

## ❓ Troubleshooting

### **Erro de Conexão**
```bash
# Verificar se N8N está rodando
curl http://localhost:5678

# Ver logs do Docker
./dev-control logs

# Testar conectividade
./devhub list
```

### **Problemas de Autenticação**
```bash
# Verificar .env
cat .env | grep -E "(API_N8N|N8N_BASIC_AUTH)"

# Testar diferentes métodos
# 1. API Key first
# 2. Basic Auth fallback
```

### **Sincronização não Funciona**
```bash
# Ver status detalhado
./devhub sync-status

# Verificar logs
./dev-control logs

# Reiniciar ambiente
./dev-control restart
```

## 🤝 Contribuindo

### **Estrutura para Extensões**
- **Models**: Adicionar novos tipos de dados
- **Controllers**: Nova lógica de negócios
- **Views**: Interfaces alternativas (web?)
- **Utils**: Utilitários compartilhados

### **Próximas Funcionalidades**
- 🌐 Interface Web opcional
- 🔄 Sync incremental/diferencial
- 📊 Métricas e relatórios
- 🔌 Plugin system
- 📡 API REST própria

## 📄 Licença

Este projeto é open source e está disponível sob licença MIT.

---

## 🎉 **N8N-DevHub: Workflows N8N como nunca antes!**

**Transforme seu desenvolvimento N8N em uma experiência profissional, colaborativa e eficiente.**

🚀 **Comece agora**: `./init-dev && ./devhub sync-start "Meu Workflow"`