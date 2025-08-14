"""
N8N-DevHub - CLI View
Interface de linha de comando para o N8N-DevHub
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
try:
    from models.workflow_model import WorkflowInfo
except ImportError:
    # Fallback se não conseguir importar
    WorkflowInfo = None


class Colors:
    """Cores para terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


class CLIView:
    """View para interface CLI"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and os.name != 'nt'  # Desabilitar cores no Windows
    
    def _colorize(self, text: str, color: str) -> str:
        """Aplica cor ao texto se habilitado"""
        if not self.use_colors:
            return text
        return f"{color}{text}{Colors.NC}"
    
    def print_header(self, title: str):
        """Imprime cabeçalho estilizado"""
        border = "=" * (len(title) + 4)
        print(self._colorize(border, Colors.CYAN))
        print(self._colorize(f"  {title}  ", Colors.CYAN))
        print(self._colorize(border, Colors.CYAN))
        print()
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(self._colorize(f"✓ {message}", Colors.GREEN))
    
    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(self._colorize(f"✗ {message}", Colors.RED))
    
    def print_warning(self, message: str):
        """Imprime mensagem de aviso"""
        print(self._colorize(f"⚠ {message}", Colors.YELLOW))
    
    def print_info(self, message: str):
        """Imprime mensagem informativa"""
        print(self._colorize(f"ℹ {message}", Colors.BLUE))
    
    def print_workflow_list(self, workflows: List[WorkflowInfo], title: str = "Workflows"):
        """Imprime lista de workflows formatada"""
        if not workflows:
            print(self._colorize(f"Nenhum workflow encontrado", Colors.YELLOW))
            return
        
        print(self._colorize(f"\n{title} ({len(workflows)}):", Colors.BOLD))
        print("-" * 80)
        
        for i, wf in enumerate(workflows, 1):
            status_icon = self._colorize("✓", Colors.GREEN) if wf.active else self._colorize("○", Colors.YELLOW)
            status_text = self._colorize("Ativo", Colors.GREEN) if wf.active else self._colorize("Inativo", Colors.YELLOW)
            
            # Formatear data
            try:
                updated = datetime.fromisoformat(wf.updated_at.replace('Z', '+00:00'))
                updated_str = updated.strftime("%d/%m/%Y %H:%M")
            except:
                updated_str = wf.updated_at or "Unknown"
            
            print(f"{i:2d}. {status_icon} {self._colorize(wf.name, Colors.WHITE)}")
            print(f"    ID: {self._colorize(wf.id, Colors.CYAN)}")
            print(f"    Status: {status_text}")
            print(f"    Atualizado: {updated_str}")
            print()
    
    def print_local_workflow_list(self, workflows: List[Dict], title: str = "Workflows Locais"):
        """Imprime lista de workflows locais"""
        if not workflows:
            print(self._colorize(f"Nenhum workflow local encontrado", Colors.YELLOW))
            return
        
        print(self._colorize(f"\n{title} ({len(workflows)}):", Colors.BOLD))
        print("-" * 80)
        
        for i, wf in enumerate(workflows, 1):
            data = wf.get('data', {})
            status_icon = self._colorize("✓", Colors.GREEN) if data.get('active') else self._colorize("○", Colors.YELLOW)
            
            # Tamanho do arquivo
            try:
                size = os.path.getsize(wf['filepath'])
                size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
            except:
                size_str = "Unknown"
            
            print(f"{i:2d}. {status_icon} {self._colorize(data.get('name', 'Unknown'), Colors.WHITE)}")
            print(f"    Arquivo: {self._colorize(wf['filename'], Colors.CYAN)}")
            print(f"    ID: {data.get('id', 'N/A')}")
            print(f"    Tamanho: {size_str}")
            print()
    
    def print_comparison_result(self, comparison: Dict):
        """Imprime resultado da comparação local vs remoto"""
        self.print_header("Comparação Local vs Remoto")
        
        print(f"Total Local: {self._colorize(str(comparison['local_count']), Colors.CYAN)}")
        print(f"Total Remoto: {self._colorize(str(comparison['remote_count']), Colors.CYAN)}")
        print()
        
        # Apenas locais
        only_local = comparison['only_local']
        if only_local:
            print(self._colorize(f"📁 Apenas Locais ({len(only_local)}):", Colors.YELLOW))
            for wf in only_local:
                print(f"  • {wf.get('name', 'Unknown')} ({wf.get('filename', 'N/A')})")
            print()
        
        # Apenas remotos
        only_remote = comparison['only_remote']
        if only_remote:
            print(self._colorize(f"☁️  Apenas Remotos ({len(only_remote)}):", Colors.BLUE))
            for wf in only_remote:
                status = "Ativo" if wf.active else "Inativo"
                print(f"  • {wf.name} ({wf.id}) - {status}")
            print()
        
        # Em ambos
        in_both = comparison['in_both']
        if in_both:
            print(self._colorize(f"🔄 Em Ambos ({len(in_both)}):", Colors.GREEN))
            for item in in_both:
                local_wf = item['local']['data']
                remote_wf = item['remote']
                sync_status = "🔄" if local_wf.get('updatedAt') != remote_wf.updated_at else "✅"
                print(f"  {sync_status} {remote_wf.name} ({remote_wf.id})")
            print()
    
    def print_operation_summary(self, success_count: int, total_count: int, 
                              operation: str, error_messages: List[str] = None):
        """Imprime resumo de operação"""
        if success_count == total_count:
            self.print_success(f"{operation} concluído: {success_count}/{total_count} workflows")
        else:
            self.print_warning(f"{operation} parcial: {success_count}/{total_count} workflows")
        
        if error_messages:
            print(self._colorize("\nErros encontrados:", Colors.RED))
            for error in error_messages:
                print(f"  • {error}")
    
    def print_connection_info(self, base_url: str, auth_type: str):
        """Imprime informações de conexão"""
        print(f"Conectando em: {self._colorize(base_url, Colors.CYAN)}")
        print(f"Autenticação: {self._colorize(auth_type, Colors.GREEN)}")
        print()
    
    def _print_section(self, title: str, commands: list, max_width: int = 30):
        """Imprime uma seção com alinhamento automático"""
        print(self._colorize(f"┌─ {title}", Colors.BOLD))
        
        # Calcular largura máxima dos comandos desta seção
        max_cmd_width = 0
        for cmd_info in commands:
            cmd_text = cmd_info[0]  # Texto do comando
            # Remover códigos de cor para calcular largura real
            clean_text = cmd_text.replace('\033[0;32m', '').replace('\033[0m', '')
            max_cmd_width = max(max_cmd_width, len(clean_text))
        
        # Garantir largura mínima
        max_cmd_width = max(max_cmd_width, max_width)
        
        # Imprimir comandos alinhados
        for i, (cmd_text, description) in enumerate(commands):
            prefix = "├─" if i < len(commands) - 1 else "└─"
            
            # Calcular padding necessário
            clean_text = cmd_text.replace('\033[0;32m', '').replace('\033[0m', '').replace('\033[0;35m', '').replace('\033[0;36m', '')
            padding = max_cmd_width - len(clean_text)
            
            print(f"{prefix} {cmd_text}{' ' * padding} → {description}")
        
        print()

    def print_help(self):
        """Imprime ajuda do sistema"""
        # Header principal
        print(self._colorize("╔═══════════════════════════════════════════════════╗", Colors.CYAN))
        print(self._colorize("║           🚀 N8N-DevHub - Sistema de Workflows    ║", Colors.CYAN))
        print(self._colorize("╚═══════════════════════════════════════════════════╝", Colors.CYAN))
        print()
        
        # Seção Setup
        setup_commands = [
            (self._colorize('init', Colors.GREEN), "Inicializar ambiente completo"),
            (f"{self._colorize('docker', Colors.GREEN)} <cmd>", "Controle Docker (start/stop/logs)"),
            (self._colorize('install-global', Colors.GREEN), "Instalar comando 'devhub' globalmente")
        ]
        self._print_section("🛠️  SETUP E AMBIENTE", setup_commands)
        
        # Seção Comandos Básicos
        basic_commands = [
            (f"{self._colorize('list', Colors.GREEN)} | {self._colorize('ls', Colors.GREEN)}", "Lista workflows remotos"),
            (f"{self._colorize('list-local', Colors.GREEN)} | {self._colorize('ll', Colors.GREEN)}", "Lista workflows locais"),
            (f"{self._colorize('status', Colors.GREEN)} | {self._colorize('st', Colors.GREEN)}", "Compara local vs remoto")
        ]
        self._print_section("📋 COMANDOS BÁSICOS", basic_commands)
        
        # Seção Download
        download_commands = [
            (f"{self._colorize('download-all', Colors.GREEN)} | {self._colorize('da', Colors.GREEN)}", "Baixa todos os workflows"),
            (self._colorize('download-active', Colors.GREEN), "Apenas workflows ativos"),
            (f"{self._colorize('download', Colors.GREEN)} <nome>", "Baixa workflow por nome"),
            (f"{self._colorize('download-id', Colors.GREEN)} <id>", "Baixa workflow por ID")
        ]
        self._print_section("⬇️  DOWNLOAD", download_commands)
        
        # Seção Upload
        upload_commands = [
            (f"{self._colorize('upload-all', Colors.GREEN)} | {self._colorize('ua', Colors.GREEN)}", "Envia todos os workflows"),
            (f"{self._colorize('upload', Colors.GREEN)} <arquivo>", "Envia arquivo específico"),
            (f"{self._colorize('upload-id', Colors.GREEN)} <id>", "Envia workflow por ID")
        ]
        self._print_section("⬆️  UPLOAD", upload_commands)
        
        # Seção Gerenciamento
        mgmt_commands = [
            (f"{self._colorize('activate', Colors.GREEN)} <nome/id>", "Ativa workflow"),
            (f"{self._colorize('deactivate', Colors.GREEN)} <nome>", "Desativa workflow"),
            (f"{self._colorize('delete', Colors.GREEN)} <nome/id>", "Remove workflow do n8n")
        ]
        self._print_section("⚙️  GERENCIAMENTO", mgmt_commands)
        
        # Seção Busca
        search_commands = [
            (f"{self._colorize('find', Colors.GREEN)} <termo>", "Busca workflows por nome"),
            (f"{self._colorize('search', Colors.GREEN)} <termo>", "Busca workflows (alias)")
        ]
        self._print_section("🔍 BUSCA", search_commands)
        
        # Seção Sincronização
        sync_commands = [
            (f"{self._colorize('sync-start', Colors.GREEN)} <nome>", "Inicia sync em tempo real"),
            (self._colorize('sync-stop', Colors.GREEN), "Para sincronização"),
            (self._colorize('sync-status', Colors.GREEN), "Status da sincronização"),
            (f"{self._colorize('sync-add', Colors.GREEN)} <nome>", "Adiciona ao monitoramento"),
            (f"{self._colorize('sync-remove', Colors.GREEN)} <nome>", "Remove do monitoramento")
        ]
        self._print_section("🔄 SINCRONIZAÇÃO", sync_commands)
        
        # Seção Filtros
        filter_commands = [
            (self._colorize('--active', Colors.MAGENTA), "Apenas workflows ativos"),
            (self._colorize('--inactive', Colors.MAGENTA), "Apenas workflows inativos"),
            (self._colorize('--by-id', Colors.MAGENTA), "Usar ID em vez de nome"),
            (self._colorize('--fuzzy', Colors.MAGENTA), "Busca aproximada (padrão)"),
            (self._colorize('--exact', Colors.MAGENTA), "Busca exata")
        ]
        self._print_section("🎛️  FILTROS", filter_commands)
        
        # Seção Exemplos
        example_commands = [
            (self._colorize('devhub init', Colors.CYAN), "Setup completo"),
            (self._colorize('devhub list --active', Colors.CYAN), "Lista ativos"),
            (self._colorize('devhub download "Demo"', Colors.CYAN), "Baixa por nome"),
            (self._colorize('devhub upload demo.json', Colors.CYAN), "Envia arquivo"),
            (self._colorize('devhub sync-start "Demo"', Colors.CYAN), "Inicia sync")
        ]
        self._print_section("💡 EXEMPLOS", example_commands)
        
        # Footer
        print(self._colorize("═" * 55, Colors.CYAN))
        print(self._colorize("💡 Use 'devhub <comando> --help' para ajuda específica", Colors.BLUE))
        print(self._colorize("═" * 55, Colors.CYAN))
    
    def prompt_confirmation(self, message: str) -> bool:
        """Solicita confirmação do usuário"""
        try:
            response = input(f"{message} (y/N): ").strip().lower()
            return response in ['y', 'yes', 's', 'sim']
        except KeyboardInterrupt:
            print("\nOperação cancelada.")
            return False
    
    def print_workflow_details(self, workflow_data: Dict):
        """Imprime detalhes de um workflow"""
        print(self._colorize(f"Detalhes do Workflow:", Colors.BOLD))
        print("-" * 40)
        
        print(f"Nome: {self._colorize(workflow_data.get('name', 'Unknown'), Colors.WHITE)}")
        print(f"ID: {self._colorize(workflow_data.get('id', 'N/A'), Colors.CYAN)}")
        
        status = workflow_data.get('active', False)
        status_text = self._colorize("Ativo", Colors.GREEN) if status else self._colorize("Inativo", Colors.YELLOW)
        print(f"Status: {status_text}")
        
        nodes_count = len(workflow_data.get('nodes', []))
        print(f"Nós: {nodes_count}")
        
        if workflow_data.get('createdAt'):
            try:
                created = datetime.fromisoformat(workflow_data['createdAt'].replace('Z', '+00:00'))
                print(f"Criado: {created.strftime('%d/%m/%Y %H:%M')}")
            except:
                print(f"Criado: {workflow_data['createdAt']}")
        
        if workflow_data.get('updatedAt'):
            try:
                updated = datetime.fromisoformat(workflow_data['updatedAt'].replace('Z', '+00:00'))
                print(f"Atualizado: {updated.strftime('%d/%m/%Y %H:%M')}")
            except:
                print(f"Atualizado: {workflow_data['updatedAt']}")
        
        print()
    
    def print_table_header(self, headers: List[str]):
        """Imprime cabeçalho de tabela"""
        header_line = " | ".join(f"{h:15}" for h in headers)
        print(self._colorize(header_line, Colors.BOLD))
        print(self._colorize("-" * len(header_line), Colors.BOLD))
    
    def clear_screen(self):
        """Limpa tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')