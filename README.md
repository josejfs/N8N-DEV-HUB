# 🚀 N8N-DevHub

**Sistema Avançado de Gerenciamento de Workflows N8N com Sincronização Assíncrona**

[![N8N](https://img.shields.io/badge/N8N-Compatible-FF6D5A?style=flat-square&logo=n8n)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://docker.com/)

---

**Desenvolvido por: [José Ferreira](https://github.com/jose-ferreira)** 👨‍💻
*Especialista em Automação e Sistemas N8N*

---

## 🎯 O que é o N8N-DevHub?

O N8N-DevHub é um sistema completo que transforma o gerenciamento de workflows N8N em uma experiência profissional e eficiente, oferecendo:

- 🔄 **Sincronização Assíncrona** em tempo real (Local ↔ N8N)
- 🎯 **Operações Específicas** por ID ou nome exato
- 🏗️ **Arquitetura MVC** profissional e organizada
- 🌍 **Multi-ambiente** com troca simples (dev ↔ prod)
- ⚡ **Interface CLI** moderna com cores e ícones
- 🐳 **Docker Ready** para desenvolvimento

## ⚡ Configuração Inicial

### **1. Instalar Dependências Python**

```bash
# 1. Criar ambiente virtual
python3 -m venv venv

# 2. Ativar ambiente virtual  
source venv/bin/activate

# 3. Instalar dependências
pip install -r N8N-DevHub/requirements.txt
```

### **2. Inicializar Ambiente Docker**

```bash
# Sobe ambiente N8N Docker + cria pasta workflows
./devhub init
```

*O comando `init` agora apenas:*

- ✅ Verifica se venv e dependências estão OK
- ✅ Cria pasta `workflows/` se não existir
- ✅ Sobe ambiente N8N Docker
- ✅ Testa conectividade

### **3. Comandos Básicos**

```bash
# Sempre ativar ambiente antes de usar
source venv/bin/activate

# Listar workflows
./devhub list

# Baixar workflow específico
./devhub download "Demo RAG"

# Iniciar sincronização em tempo real  
./devhub sync-start "Demo RAG"
```

**⚠️ Importante**: Use sempre `./devhub` (com `./`) para executar os comandos.

### **4. Acessar N8N**

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

### **🗑️ Limpeza Docker**

```bash
./devhub clear list-containers     # Lista containers com ID e nome
./devhub clear remove-container <id>  # Remove container específico
./devhub clear n8n                 # Remove apenas N8N (seguro)
./devhub clear cache               # Limpa apenas cache
./devhub clear containers          # Remove todos containers
./devhub clear images              # Remove todas imagens  
./devhub clear volumes             # Remove volumes (⚠️ perde dados)
./devhub clear all                 # Limpeza completa (⚠️ remove tudo)
```

## 🏗️ Arquitetura

### **Estrutura do Projeto**

```
N8N-DevHub/                     # Diretório raiz do projeto
├── devhub                      # Script principal (bash)
├── venv/                       # Ambiente virtual Python
├── workflows/                  # Workflows N8N (JSON)
├── README.md                   # Esta documentação
└── N8N-DevHub/                 # Core do sistema
    ├── requirements.txt        # Dependências Python
    ├── docker-compose.yml      # Ambiente N8N
    ├── python/
    │   └── devhub.py          # Aplicação principal Python
    ├── scripts/
    │   ├── init-dev           # Inicializador Docker
    │   ├── dev-control        # Controle Docker
    │   └── clear-docker       # Limpeza Docker
    ├── models/
    │   └── workflow_model.py  # API e dados N8N
    ├── controllers/
    │   └── workflow_controller.py  # Lógica de negócios
    ├── views/
    │   └── cli_view.py        # Interface CLI
    └── utils/
        └── sync_manager.py    # Sincronização assíncrona
```

### **Como o Sistema Funciona**

```
./devhub [comando]                   # Script bash principal
├── init     → scripts/init-dev      # Configurar Docker
├── docker   → scripts/dev-control   # Controlar Docker  
├── clear    → scripts/clear-docker  # Limpar Docker
└── outros   → python/devhub.py      # Comandos Python
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

### **Resolução de Problemas Comuns**

**Erro: "ModuleNotFoundError: No module named 'watchdog'"**

Este erro acontece quando as dependências Python não foram instaladas. Para resolver:

```bash
# 1. Ativar o ambiente virtual (se não estiver ativo)
source venv/bin/activate

# 2. Instalar/reinstalar dependências
pip install -r N8N-DevHub/requirements.txt

# 3. Verificar se foi instalado corretamente
pip list | grep watchdog

# 4. Agora o comando deve funcionar
./devhub help
```

**Comando Completo para Primeira Instalação:**

```bash
# Instalar tudo de uma vez
python3 -m venv venv && source venv/bin/activate && pip install -r N8N-DevHub/requirements.txt && ./devhub init
```

**Dependências Principais:**

- `requests>=2.31.0` - Comunicação com API N8N
- `python-dotenv>=1.0.0` - Gerenciamento de configurações
- `watchdog>=3.0.0` - Monitoramento de arquivos em tempo real

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

### **Inicialização Docker**

```bash
./devhub init  # Sobe N8N + cria workflows/ + testa conectividade
```

### **Controles**

```bash
./devhub docker start     # Inicia ambiente
./devhub docker stop      # Para ambiente
./devhub docker restart   # Reinicia
./devhub docker logs      # Logs em tempo real
./devhub docker status    # Status containers
./devhub docker clean     # Reset completo (cuidado!)

# Limpeza seletiva
./devhub clear list-containers     # Ver containers rodando
./devhub clear remove-container <id>  # Remove container específico  
./devhub clear n8n                 # Remove apenas N8N (recomendado)
./devhub clear all                 # Remove tudo (cuidado!)
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
# 1. Configurar ambiente
python3 -m venv venv && source venv/bin/activate && pip install -r N8N-DevHub/requirements.txt
./devhub init
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
./devhub docker logs

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
./devhub docker logs

# Reiniciar ambiente
./devhub docker restart
```

### **Limpeza de Ambiente**

```bash
# Ver containers rodando primeiro
./devhub clear list-containers

# Remover container específico (seguro)
./devhub clear remove-container abc123

# Reset N8N mantendo outros projetos
./devhub clear n8n

# Reset completo (remove tudo!)
./devhub clear all

# Apenas limpar cache (mais seguro)
./devhub clear cache
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

🚀 **Comece agora**: `python3 -m venv venv && source venv/bin/activate && pip install -r N8N-DevHub/requirements.txt && ./devhub init`
