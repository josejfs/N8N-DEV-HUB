"""
N8N-DevHub - Sync Manager
Sistema de sincronização assíncrona em tempo real
"""

import asyncio
import time
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue

from models.workflow_model import WorkflowModel
from controllers.workflow_controller import WorkflowController


class SyncState:
    """Estado de sincronização de um workflow"""
    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.local_hash: Optional[str] = None
        self.remote_hash: Optional[str] = None
        self.local_updated: Optional[datetime] = None
        self.remote_updated: Optional[datetime] = None
        self.syncing = False
        self.conflict = False
        self.last_sync: Optional[datetime] = None


class WorkflowFileHandler(FileSystemEventHandler):
    """Handler para monitorar mudanças nos arquivos de workflow"""
    
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager
        self.processing = set()  # Evitar loops de processamento
    
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
        
        filename = os.path.basename(event.src_path)
        
        # Evitar processar o mesmo arquivo múltiplas vezes rapidamente
        if filename in self.processing:
            return
            
        self.processing.add(filename)
        
        # Delay para evitar múltiplas notificações
        threading.Timer(1.0, self._process_file_change, args=[event.src_path, filename]).start()
    
    def _process_file_change(self, filepath: str, filename: str):
        try:
            self.sync_manager.queue_local_change(filepath, filename)
        finally:
            self.processing.discard(filename)


class AsyncSyncManager:
    """Gerenciador de sincronização assíncrona"""
    
    def __init__(self, controller: WorkflowController, model: WorkflowModel):
        self.controller = controller
        self.model = model
        
        # Estado de sincronização
        self.sync_states: Dict[str, SyncState] = {}
        self.target_workflows: Set[str] = set()  # IDs dos workflows monitorados
        self.target_names: Set[str] = set()      # Nomes dos workflows monitorados
        
        # Configurações
        self.poll_interval = 10  # segundos
        self.running = False
        self.conflict_resolution = "ask"  # ask, local, remote, latest
        
        # Callbacks para eventos
        self.on_sync_start: Optional[Callable] = None
        self.on_sync_complete: Optional[Callable] = None
        self.on_conflict: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Filas para eventos
        self.local_changes = queue.Queue()
        self.remote_changes = queue.Queue()
        
        # File watcher
        self.observer = Observer()
        self.file_handler = WorkflowFileHandler(self)
        
        # Threads
        self.remote_monitor_thread = None
        self.sync_processor_thread = None
    
    def add_workflow(self, identifier: str, by_id: bool = False):
        """Adiciona workflow para monitoramento"""
        if by_id:
            self.target_workflows.add(identifier)
        else:
            self.target_names.add(identifier)
            # Resolver nome para ID
            matches = self.controller.find_workflow_by_name(identifier)
            if matches:
                self.target_workflows.add(matches[0].id)
    
    def remove_workflow(self, identifier: str, by_id: bool = False):
        """Remove workflow do monitoramento"""
        if by_id:
            self.target_workflows.discard(identifier)
            if identifier in self.sync_states:
                del self.sync_states[identifier]
        else:
            self.target_names.discard(identifier)
    
    def start_sync(self):
        """Inicia sincronização assíncrona"""
        if self.running:
            return False
        
        self.running = True
        
        # Inicializar estado dos workflows
        self._initialize_sync_states()
        
        # Iniciar file watcher
        self.observer.schedule(
            self.file_handler, 
            self.model.workflows_dir, 
            recursive=False
        )
        self.observer.start()
        
        # Iniciar threads
        self.remote_monitor_thread = threading.Thread(
            target=self._remote_monitor_loop,
            daemon=True
        )
        self.remote_monitor_thread.start()
        
        self.sync_processor_thread = threading.Thread(
            target=self._sync_processor_loop,
            daemon=True
        )
        self.sync_processor_thread.start()
        
        if self.on_sync_start:
            self.on_sync_start()
        
        return True
    
    def stop_sync(self):
        """Para sincronização assíncrona"""
        self.running = False
        
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        if self.on_sync_complete:
            self.on_sync_complete()
    
    def _initialize_sync_states(self):
        """Inicializa estados de sincronização"""
        try:
            # Workflows remotos
            remote_workflows = self.controller.list_remote_workflows()
            
            # Workflows locais
            local_workflows = self.controller.list_local_workflows()
            
            # Filtrar apenas os workflows alvo
            for wf in remote_workflows:
                if wf.id in self.target_workflows or wf.name in self.target_names:
                    state = SyncState(wf.id, wf.name)
                    state.remote_updated = self._parse_datetime(wf.updated_at)
                    
                    # Calcular hash remoto
                    remote_data = self.model.get_workflow_by_id(wf.id)
                    if remote_data:
                        state.remote_hash = self._calculate_workflow_hash(remote_data)
                    
                    self.sync_states[wf.id] = state
            
            # Verificar workflows locais
            for local_wf in local_workflows:
                wf_id = local_wf.get('id')
                if wf_id and wf_id in self.sync_states:
                    state = self.sync_states[wf_id]
                    
                    # Calcular hash local
                    state.local_hash = self._calculate_workflow_hash(local_wf['data'])
                    
                    # Timestamp local
                    try:
                        stat = os.stat(local_wf['filepath'])
                        state.local_updated = datetime.fromtimestamp(stat.st_mtime)
                    except:
                        pass
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao inicializar estados: {e}")
    
    def _remote_monitor_loop(self):
        """Loop de monitoramento remoto"""
        while self.running:
            try:
                self._check_remote_changes()
                time.sleep(self.poll_interval)
            except Exception as e:
                if self.on_error:
                    self.on_error(f"Erro no monitor remoto: {e}")
                time.sleep(self.poll_interval)
    
    def _sync_processor_loop(self):
        """Loop de processamento de sincronização"""
        while self.running:
            try:
                # Processar mudanças locais
                try:
                    filepath, filename = self.local_changes.get_nowait()
                    self._process_local_change(filepath, filename)
                except queue.Empty:
                    pass
                
                # Processar mudanças remotas
                try:
                    workflow_id = self.remote_changes.get_nowait()
                    self._process_remote_change(workflow_id)
                except queue.Empty:
                    pass
                
                time.sleep(0.5)  # Pequeno delay
                
            except Exception as e:
                if self.on_error:
                    self.on_error(f"Erro no processador de sync: {e}")
    
    def _check_remote_changes(self):
        """Verifica mudanças remotas"""
        try:
            remote_workflows = self.controller.list_remote_workflows()
            
            for wf in remote_workflows:
                if wf.id not in self.sync_states:
                    continue
                
                state = self.sync_states[wf.id]
                if state.syncing:
                    continue
                
                # Verificar se houve mudança
                remote_updated = self._parse_datetime(wf.updated_at)
                if state.remote_updated != remote_updated:
                    # Buscar dados completos
                    remote_data = self.model.get_workflow_by_id(wf.id)
                    if remote_data:
                        new_hash = self._calculate_workflow_hash(remote_data)
                        
                        if new_hash != state.remote_hash:
                            state.remote_hash = new_hash
                            state.remote_updated = remote_updated
                            
                            # Enfileirar mudança remota
                            self.remote_changes.put(wf.id)
                            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao verificar mudanças remotas: {e}")
    
    def queue_local_change(self, filepath: str, filename: str):
        """Enfileira mudança local"""
        self.local_changes.put((filepath, filename))
    
    def _process_local_change(self, filepath: str, filename: str):
        """Processa mudança local"""
        try:
            # Extrair ID do arquivo
            workflow_id = self.model.extract_id_from_filename(filename)
            
            if not workflow_id or workflow_id not in self.sync_states:
                return
            
            state = self.sync_states[workflow_id]
            if state.syncing:
                return
            
            # Carregar dados locais
            local_data = self.model.load_workflow_from_file(filename)
            if not local_data:
                return
            
            new_hash = self._calculate_workflow_hash(local_data)
            
            # Verificar se realmente mudou
            if new_hash == state.local_hash:
                return
            
            state.local_hash = new_hash
            state.local_updated = datetime.now()
            
            # Verificar conflito
            if self._has_conflict(state):
                state.conflict = True
                if self.on_conflict:
                    resolution = self.on_conflict(state)
                    self._resolve_conflict(state, resolution)
            else:
                # Sync para remoto
                self._sync_to_remote(state, local_data)
                
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao processar mudança local: {e}")
    
    def _process_remote_change(self, workflow_id: str):
        """Processa mudança remota"""
        try:
            if workflow_id not in self.sync_states:
                return
                
            state = self.sync_states[workflow_id]
            if state.syncing:
                return
            
            # Buscar dados remotos
            remote_data = self.model.get_workflow_by_id(workflow_id)
            if not remote_data:
                return
            
            # Verificar conflito
            if self._has_conflict(state):
                state.conflict = True
                if self.on_conflict:
                    resolution = self.on_conflict(state)
                    self._resolve_conflict(state, resolution, remote_data)
            else:
                # Sync para local
                self._sync_to_local(state, remote_data)
                
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao processar mudança remota: {e}")
    
    def _sync_to_remote(self, state: SyncState, local_data: Dict):
        """Sincroniza para remoto"""
        state.syncing = True
        try:
            success, message = self.controller.upload_workflow(
                state.workflow_id, by_filename=False
            )
            
            if success:
                state.last_sync = datetime.now()
                state.conflict = False
                print(f"🔄 Sincronizado para remoto: {state.name}")
            else:
                if self.on_error:
                    self.on_error(f"Erro ao sincronizar '{state.name}': {message}")
                    
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao sincronizar para remoto: {e}")
        finally:
            state.syncing = False
    
    def _sync_to_local(self, state: SyncState, remote_data: Dict):
        """Sincroniza para local"""
        state.syncing = True
        try:
            filepath = self.model.save_workflow_to_file(remote_data)
            state.local_hash = state.remote_hash
            state.last_sync = datetime.now()
            state.conflict = False
            
            print(f"🔄 Sincronizado para local: {state.name}")
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao sincronizar para local: {e}")
        finally:
            state.syncing = False
    
    def _has_conflict(self, state: SyncState) -> bool:
        """Verifica se há conflito"""
        return (state.local_hash is not None and 
                state.remote_hash is not None and
                state.local_hash != state.remote_hash and
                state.local_updated is not None and
                state.remote_updated is not None)
    
    def _resolve_conflict(self, state: SyncState, resolution: str, remote_data: Dict = None):
        """Resolve conflito baseado na estratégia"""
        try:
            if resolution == "local":
                # Usar versão local
                local_data = self.model.load_workflow_from_file(
                    self.model.generate_filename(state.name, state.workflow_id)
                )
                if local_data:
                    self._sync_to_remote(state, local_data)
                    
            elif resolution == "remote":
                # Usar versão remota
                if not remote_data:
                    remote_data = self.model.get_workflow_by_id(state.workflow_id)
                if remote_data:
                    self._sync_to_local(state, remote_data)
                    
            elif resolution == "latest":
                # Usar versão mais recente
                if state.local_updated > state.remote_updated:
                    local_data = self.model.load_workflow_from_file(
                        self.model.generate_filename(state.name, state.workflow_id)
                    )
                    if local_data:
                        self._sync_to_remote(state, local_data)
                else:
                    if not remote_data:
                        remote_data = self.model.get_workflow_by_id(state.workflow_id)
                    if remote_data:
                        self._sync_to_local(state, remote_data)
                        
        except Exception as e:
            if self.on_error:
                self.on_error(f"Erro ao resolver conflito: {e}")
    
    def _calculate_workflow_hash(self, workflow_data: Dict) -> str:
        """Calcula hash de um workflow para detectar mudanças"""
        # Remover campos que mudam automaticamente
        clean_data = {k: v for k, v in workflow_data.items() 
                     if k not in ['updatedAt', 'createdAt', 'versionId', 'shared']}
        
        # Converter para JSON ordenado
        json_str = json.dumps(clean_data, sort_keys=True, separators=(',', ':'))
        
        # Calcular SHA256
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Converte string de data para datetime"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def get_sync_status(self) -> Dict:
        """Retorna status de sincronização"""
        return {
            'running': self.running,
            'workflows_monitored': len(self.sync_states),
            'conflicts': len([s for s in self.sync_states.values() if s.conflict]),
            'syncing': len([s for s in self.sync_states.values() if s.syncing]),
            'states': {wf_id: {
                'name': state.name,
                'syncing': state.syncing,
                'conflict': state.conflict,
                'last_sync': state.last_sync.isoformat() if state.last_sync else None,
                'local_updated': state.local_updated.isoformat() if state.local_updated else None,
                'remote_updated': state.remote_updated.isoformat() if state.remote_updated else None
            } for wf_id, state in self.sync_states.items()}
        }