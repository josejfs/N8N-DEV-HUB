#!/usr/bin/env python3
"""
N8N-DevHub - Sistema Avançado de Gerenciamento de Workflows N8N
Script principal de linha de comando
"""

import sys
import argparse
import time
from datetime import datetime
from pathlib import Path

# Adicionar o diretório N8N-DevHub ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.workflow_model import WorkflowModel
from controllers.workflow_controller import WorkflowController
from views.cli_view import CLIView
from utils.sync_manager import AsyncSyncManager


class DevHub:
    """Aplicação principal do N8N-DevHub"""
    
    def __init__(self):
        self.model = WorkflowModel()
        self.controller = WorkflowController(self.model)
        self.view = CLIView()
        self.sync_manager = AsyncSyncManager(self.controller, self.model)
        
    def run(self, args):
        """Executa comando baseado nos argumentos"""
        try:
            # Mostrar informações de conexão
            auth_type = "API Key" if 'X-N8N-API-KEY' in self.model.headers else \
                       "Basic Auth" if 'Authorization' in self.model.headers else \
                       "Nenhuma"
            self.view.print_connection_info(self.model.base_url, auth_type)
            
            # Executar comando
            command = args.command.replace('-', '_')
            method_name = f"cmd_{command}"
            
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                method(args)
            else:
                self.view.print_error(f"Comando '{args.command}' não encontrado")
                self.cmd_help(args)
                
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
            sys.exit(1)
        except Exception as e:
            self.view.print_error(f"Erro inesperado: {e}")
            sys.exit(1)
    
    # Comandos de listagem
    def cmd_list(self, args):
        """Lista workflows remotos"""
        try:
            workflows = self.controller.list_remote_workflows(
                active_only=args.active,
                inactive_only=args.inactive
            )
            
            title = "Workflows Remotos"
            if args.active:
                title += " (Ativos)"
            elif args.inactive:
                title += " (Inativos)"
                
            self.view.print_workflow_list(workflows, title)
            
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_ls(self, args):
        """Alias para list"""
        self.cmd_list(args)
    
    def cmd_list_local(self, args):
        """Lista workflows locais"""
        workflows = self.controller.list_local_workflows()
        self.view.print_local_workflow_list(workflows)
    
    def cmd_ll(self, args):
        """Alias para list-local"""
        self.cmd_list_local(args)
    
    def cmd_status(self, args):
        """Mostra comparação local vs remoto"""
        try:
            comparison = self.controller.compare_local_remote()
            self.view.print_comparison_result(comparison)
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_st(self, args):
        """Alias para status"""
        self.cmd_status(args)
    
    # Comandos de download
    def cmd_download_all(self, args):
        """Baixa todos os workflows"""
        try:
            success_count, total_count, errors = self.controller.download_all_workflows(
                active_only=args.active,
                inactive_only=args.inactive
            )
            
            operation = "Download"
            if args.active:
                operation += " (Ativos)"
            elif args.inactive:
                operation += " (Inativos)"
                
            self.view.print_operation_summary(success_count, total_count, operation, errors)
            
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_da(self, args):
        """Alias para download-all"""
        self.cmd_download_all(args)
    
    def cmd_download_active(self, args):
        """Baixa apenas workflows ativos"""
        args.active = True
        args.inactive = False
        self.cmd_download_all(args)
    
    def cmd_download_inactive(self, args):
        """Baixa apenas workflows inativos"""
        args.active = False
        args.inactive = True
        self.cmd_download_all(args)
    
    def cmd_download(self, args):
        """Baixa workflow específico por nome"""
        if not args.identifier:
            self.view.print_error("Nome do workflow é obrigatório")
            return
            
        try:
            success, message, filepath = self.controller.download_workflow(
                args.identifier, by_id=False
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_download_id(self, args):
        """Baixa workflow específico por ID"""
        if not args.identifier:
            self.view.print_error("ID do workflow é obrigatório")
            return
            
        try:
            success, message, filepath = self.controller.download_workflow(
                args.identifier, by_id=True
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    # Comandos de upload
    def cmd_upload_all(self, args):
        """Envia todos os workflows locais"""
        try:
            success_count, total_count, errors = self.controller.upload_all_workflows()
            self.view.print_operation_summary(success_count, total_count, "Upload", errors)
            
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_ua(self, args):
        """Alias para upload-all"""
        self.cmd_upload_all(args)
    
    def cmd_upload(self, args):
        """Envia workflow específico por arquivo"""
        if not args.identifier:
            self.view.print_error("Nome do arquivo é obrigatório")
            return
            
        try:
            success, message = self.controller.upload_workflow(
                args.identifier, by_filename=True
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_upload_id(self, args):
        """Envia workflow específico por ID"""
        if not args.identifier:
            self.view.print_error("ID do workflow é obrigatório")
            return
            
        try:
            success, message = self.controller.upload_workflow(
                args.identifier, by_filename=False
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    # Comandos de gerenciamento
    def cmd_activate(self, args):
        """Ativa workflow"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
            
        try:
            success, message = self.controller.activate_workflow(
                args.identifier, by_id=args.by_id
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_deactivate(self, args):
        """Desativa workflow"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
            
        try:
            success, message = self.controller.deactivate_workflow(
                args.identifier, by_id=args.by_id
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_delete(self, args):
        """Remove workflow do n8n"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
        
        # Confirmação
        if not args.force:
            if not self.view.prompt_confirmation(f"Tem certeza que deseja remover o workflow '{args.identifier}'?"):
                self.view.print_info("Operação cancelada")
                return
        
        try:
            success, message = self.controller.delete_remote_workflow(
                args.identifier, by_id=args.by_id
            )
            
            if success:
                self.view.print_success(message)
            else:
                self.view.print_error(message)
                
        except Exception as e:
            self.view.print_error(str(e))
    
    # Comandos de busca
    def cmd_find(self, args):
        """Busca workflows por nome"""
        if not args.identifier:
            self.view.print_error("Termo de busca é obrigatório")
            return
            
        try:
            matches = self.controller.find_workflow_by_name(
                args.identifier, fuzzy=not args.exact
            )
            
            if matches:
                search_type = "exata" if args.exact else "aproximada"
                title = f"Resultados da busca {search_type} por '{args.identifier}'"
                self.view.print_workflow_list(matches, title)
            else:
                self.view.print_warning(f"Nenhum workflow encontrado com '{args.identifier}'")
                
        except Exception as e:
            self.view.print_error(str(e))
    
    def cmd_search(self, args):
        """Alias para find"""
        self.cmd_find(args)
    
    def cmd_details(self, args):
        """Mostra detalhes de um workflow"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
            
        try:
            if args.by_id:
                workflow_data = self.model.get_workflow_by_id(args.identifier)
            else:
                matches = self.controller.find_workflow_by_name(args.identifier)
                if not matches:
                    self.view.print_error(f"Workflow '{args.identifier}' não encontrado")
                    return
                elif len(matches) > 1:
                    self.view.print_error("Múltiplos workflows encontrados. Use --by-id ou seja mais específico")
                    return
                
                workflow_data = self.model.get_workflow_by_id(matches[0].id)
            
            if workflow_data:
                self.view.print_workflow_details(workflow_data)
            else:
                self.view.print_error("Workflow não encontrado")
                
        except Exception as e:
            self.view.print_error(str(e))
    
    # Comandos de sincronização assíncrona
    def cmd_sync_start(self, args):
        """Inicia sincronização assíncrona"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
        
        # Configurar callbacks
        self.sync_manager.on_sync_start = lambda: self.view.print_success("🚀 Sincronização assíncrona iniciada")
        self.sync_manager.on_sync_complete = lambda: self.view.print_info("⏸️ Sincronização assíncrona parada")
        self.sync_manager.on_error = lambda msg: self.view.print_error(f"⚠️ {msg}")
        self.sync_manager.on_conflict = self._handle_sync_conflict
        
        # Adicionar workflows para monitoramento
        identifiers = args.identifier.split(',') if ',' in args.identifier else [args.identifier]
        
        for identifier in identifiers:
            identifier = identifier.strip()
            self.sync_manager.add_workflow(identifier, by_id=args.by_id)
            
        # Configurar estratégia de resolução de conflitos
        if args.conflict_resolution:
            self.sync_manager.conflict_resolution = args.conflict_resolution
        
        # Configurar intervalo de polling
        if args.poll_interval:
            self.sync_manager.poll_interval = args.poll_interval
        
        # Iniciar sincronização
        if self.sync_manager.start_sync():
            self.view.print_info(f"🔄 Monitorando workflows: {', '.join(identifiers)}")
            self.view.print_info(f"📊 Intervalo de verificação: {self.sync_manager.poll_interval}s")
            self.view.print_info("🛑 Pressione Ctrl+C para parar")
            
            try:
                # Manter programa rodando
                while self.sync_manager.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.view.print_info("\n🛑 Parando sincronização...")
                self.sync_manager.stop_sync()
        else:
            self.view.print_error("Sincronização já está rodando")
    
    def cmd_sync_stop(self, args):
        """Para sincronização assíncrona"""
        if self.sync_manager.running:
            self.sync_manager.stop_sync()
            self.view.print_success("🛑 Sincronização assíncrona parada")
        else:
            self.view.print_warning("Sincronização não está rodando")
    
    def cmd_sync_status(self, args):
        """Mostra status da sincronização"""
        status = self.sync_manager.get_sync_status()
        
        self.view.print_header("Status da Sincronização Assíncrona")
        
        if status['running']:
            self.view.print_success(f"🔄 Status: Rodando")
        else:
            self.view.print_warning(f"⏸️ Status: Parado")
        
        print(f"📊 Workflows Monitorados: {status['workflows_monitored']}")
        print(f"⚠️ Conflitos Ativos: {status['conflicts']}")
        print(f"🔄 Sincronizando: {status['syncing']}")
        print()
        
        if status['states']:
            print(self.view._colorize("Detalhes dos Workflows:", self.view.Colors.BOLD))
            print("-" * 60)
            
            for wf_id, state in status['states'].items():
                status_icon = "🔄" if state['syncing'] else "⚠️" if state['conflict'] else "✅"
                print(f"{status_icon} {state['name']} ({wf_id})")
                
                if state['last_sync']:
                    last_sync = datetime.fromisoformat(state['last_sync'])
                    print(f"    Última Sync: {last_sync.strftime('%d/%m/%Y %H:%M:%S')}")
                else:
                    print(f"    Última Sync: Nunca")
                
                if state['conflict']:
                    print(f"    🚨 CONFLITO DETECTADO")
                
                print()
    
    def cmd_sync_add(self, args):
        """Adiciona workflow ao monitoramento"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
        
        self.sync_manager.add_workflow(args.identifier, by_id=args.by_id)
        self.view.print_success(f"✅ Workflow '{args.identifier}' adicionado ao monitoramento")
    
    def cmd_sync_remove(self, args):
        """Remove workflow do monitoramento"""
        if not args.identifier:
            self.view.print_error("Nome ou ID do workflow é obrigatório")
            return
        
        self.sync_manager.remove_workflow(args.identifier, by_id=args.by_id)
        self.view.print_success(f"🗑️ Workflow '{args.identifier}' removido do monitoramento")
    
    def _handle_sync_conflict(self, state):
        """Handler para conflitos de sincronização"""
        self.view.print_warning(f"🚨 CONFLITO DETECTADO: {state.name}")
        print(f"   Local atualizado: {state.local_updated}")
        print(f"   Remoto atualizado: {state.remote_updated}")
        print()
        
        if self.sync_manager.conflict_resolution == "ask":
            print("Estratégias de resolução:")
            print("  1. local  - Usar versão local")
            print("  2. remote - Usar versão remota")  
            print("  3. latest - Usar versão mais recente")
            print("  4. skip   - Pular este conflito")
            
            try:
                choice = input("Escolha uma opção (1-4): ").strip()
                
                resolution_map = {
                    '1': 'local',
                    '2': 'remote', 
                    '3': 'latest',
                    '4': 'skip'
                }
                
                return resolution_map.get(choice, 'skip')
                
            except KeyboardInterrupt:
                return 'skip'
        else:
            return self.sync_manager.conflict_resolution

    def cmd_help(self, args):
        """Mostra ajuda"""
        self.view.print_help()


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='N8N-DevHub - Sistema Avançado de Gerenciamento de Workflows N8N',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumento principal (comando)
    parser.add_argument('command', nargs='?', default='help',
                       help='Comando a ser executado')
    
    # Identificador (nome, ID, arquivo)
    parser.add_argument('identifier', nargs='?',
                       help='Identificador do workflow (nome, ID ou arquivo)')
    
    # Filtros
    parser.add_argument('--active', action='store_true',
                       help='Apenas workflows ativos')
    parser.add_argument('--inactive', action='store_true',
                       help='Apenas workflows inativos')
    parser.add_argument('--by-id', action='store_true',
                       help='Usar ID em vez de nome')
    parser.add_argument('--exact', action='store_true',
                       help='Busca exata (padrão é aproximada)')
    parser.add_argument('--force', action='store_true',
                       help='Força operação sem confirmação')
    
    # Opções de sincronização
    parser.add_argument('--poll-interval', type=int, default=10,
                       help='Intervalo de verificação em segundos (padrão: 10)')
    parser.add_argument('--conflict-resolution', 
                       choices=['ask', 'local', 'remote', 'latest'],
                       default='ask',
                       help='Estratégia de resolução de conflitos')
    
    args = parser.parse_args()
    
    # Validar argumentos mutuamente exclusivos
    if args.active and args.inactive:
        print("Erro: --active e --inactive são mutuamente exclusivos")
        sys.exit(1)
    
    # Executar aplicação
    devhub = DevHub()
    devhub.run(args)


if __name__ == "__main__":
    main()