"""
N8N-DevHub - Workflow Controller
Controla operações e lógica de negócios para workflows
"""

import os
import re
from typing import List, Optional, Dict, Tuple
from models.workflow_model import WorkflowModel, WorkflowInfo


class WorkflowController:
    """Controller para gerenciar operações de workflows"""
    
    def __init__(self, model: WorkflowModel = None):
        self.model = model or WorkflowModel()
    
    def list_remote_workflows(self, active_only: bool = False, inactive_only: bool = False) -> List[WorkflowInfo]:
        """Lista workflows remotos com filtros"""
        try:
            workflows = self.model.get_all_workflows()
            if workflows is None:
                return []
            
            if active_only:
                workflows = [wf for wf in workflows if wf.active]
            elif inactive_only:
                workflows = [wf for wf in workflows if not wf.active]
            
            return workflows
        except Exception as e:
            raise Exception(f"Erro ao listar workflows remotos: {e}")
    
    def list_local_workflows(self) -> List[Dict]:
        """Lista workflows locais"""
        return self.model.get_local_workflows()
    
    def find_workflow_by_name(self, name: str, fuzzy: bool = True) -> List[WorkflowInfo]:
        """Encontra workflows por nome (exato ou aproximado)"""
        try:
            all_workflows = self.model.get_all_workflows()
            if not all_workflows:
                return []
            
            if fuzzy:
                # Busca aproximada (case-insensitive, partial match)
                name_lower = name.lower()
                matches = [wf for wf in all_workflows 
                          if name_lower in wf.name.lower()]
            else:
                # Busca exata
                matches = [wf for wf in all_workflows 
                          if wf.name == name]
            
            return matches
        except Exception as e:
            raise Exception(f"Erro ao buscar workflow por nome: {e}")
    
    def find_workflow_by_id(self, workflow_id: str) -> Optional[WorkflowInfo]:
        """Encontra workflow por ID"""
        try:
            all_workflows = self.model.get_all_workflows()
            if not all_workflows:
                return None
            
            for wf in all_workflows:
                if wf.id == workflow_id:
                    return wf
            
            return None
        except Exception as e:
            raise Exception(f"Erro ao buscar workflow por ID: {e}")
    
    def download_workflow(self, identifier: str, by_id: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Baixa um workflow específico
        Returns: (success, message, filepath)
        """
        try:
            workflow_data = None
            workflow_info = None
            
            if by_id:
                # Buscar por ID
                workflow_data = self.model.get_workflow_by_id(identifier)
                if workflow_data:
                    workflow_info = WorkflowInfo(
                        id=workflow_data.get('id'),
                        name=workflow_data.get('name'),
                        active=workflow_data.get('active', False),
                        created_at=workflow_data.get('createdAt'),
                        updated_at=workflow_data.get('updatedAt')
                    )
            else:
                # Buscar por nome
                matches = self.find_workflow_by_name(identifier, fuzzy=True)
                if len(matches) == 0:
                    return False, f"Nenhum workflow encontrado com nome '{identifier}'", None
                elif len(matches) > 1:
                    names = [f"'{wf.name}' ({wf.id})" for wf in matches]
                    return False, f"Múltiplos workflows encontrados: {', '.join(names)}", None
                
                workflow_info = matches[0]
                workflow_data = self.model.get_workflow_by_id(workflow_info.id)
            
            if not workflow_data:
                return False, f"Workflow '{identifier}' não encontrado", None
            
            # Salvar arquivo
            filepath = self.model.save_workflow_to_file(workflow_data)
            filename = os.path.basename(filepath)
            
            return True, f"Workflow '{workflow_info.name}' baixado como {filename}", filepath
            
        except Exception as e:
            return False, f"Erro ao baixar workflow: {e}", None
    
    def download_all_workflows(self, active_only: bool = False, inactive_only: bool = False) -> Tuple[int, int, List[str]]:
        """
        Baixa todos os workflows
        Returns: (success_count, total_count, error_messages)
        """
        try:
            workflows = self.list_remote_workflows(active_only, inactive_only)
            success_count = 0
            error_messages = []
            
            for workflow_info in workflows:
                try:
                    workflow_data = self.model.get_workflow_by_id(workflow_info.id)
                    if workflow_data:
                        self.model.save_workflow_to_file(workflow_data)
                        success_count += 1
                    else:
                        error_messages.append(f"Erro ao baixar detalhes de '{workflow_info.name}'")
                        
                except Exception as e:
                    error_messages.append(f"Erro ao baixar '{workflow_info.name}': {e}")
            
            return success_count, len(workflows), error_messages
            
        except Exception as e:
            return 0, 0, [f"Erro ao listar workflows: {e}"]
    
    def upload_workflow(self, identifier: str, by_filename: bool = True) -> Tuple[bool, str]:
        """
        Envia um workflow específico
        Returns: (success, message)
        """
        try:
            workflow_data = None
            
            if by_filename:
                # Buscar por nome de arquivo
                if not identifier.endswith('.json'):
                    identifier += '.json'
                
                workflow_data = self.model.load_workflow_from_file(identifier)
                if not workflow_data:
                    return False, f"Arquivo '{identifier}' não encontrado"
            else:
                # Buscar por ID extraído do arquivo
                local_workflows = self.model.get_local_workflows()
                for wf in local_workflows:
                    if wf.get('id') == identifier:
                        workflow_data = wf['data']
                        break
                
                if not workflow_data:
                    return False, f"Workflow com ID '{identifier}' não encontrado localmente"
            
            # Verificar se workflow já existe remotamente
            workflow_id = workflow_data.get('id')
            workflow_name = workflow_data.get('name', 'Unknown')
            
            existing = None
            if workflow_id:
                existing = self.model.get_workflow_by_id(workflow_id)
            
            if existing:
                # Atualizar workflow existente
                result = self.model.update_workflow(workflow_id, workflow_data)
                if result:
                    # Após sucesso: substituir arquivo local pela versão padrão DevHub
                    if by_filename:
                        self._refresh_local_workflow_after_upload(result, identifier)
                    return True, f"Workflow '{workflow_name}' atualizado com sucesso"
                else:
                    return False, f"Erro ao atualizar workflow '{workflow_name}'"
            else:
                # Criar novo workflow
                result = self.model.create_workflow(workflow_data)
                if result:
                    # Após sucesso: substituir arquivo local pela versão padrão DevHub
                    if by_filename:
                        self._refresh_local_workflow_after_upload(result, identifier)
                    return True, f"Workflow '{workflow_name}' criado com sucesso"
                else:
                    return False, f"Erro ao criar workflow '{workflow_name}'"
                    
        except Exception as e:
            return False, f"Erro ao enviar workflow: {e}"
    
    def _refresh_local_workflow_after_upload(self, uploaded_workflow: Dict, original_filename: str):
        """
        Substitui o arquivo local pela versão padrão DevHub após upload bem-sucedido
        """
        try:
            import os
            
            # Obter informações do workflow uploadado
            workflow_id = uploaded_workflow.get('id')
            workflow_name = uploaded_workflow.get('name', 'Unknown')
            
            if not workflow_id:
                return
            
            # Baixar versão atualizada do servidor
            fresh_workflow = self.model.get_workflow_by_id(workflow_id)
            if not fresh_workflow:
                return
            
            # Gerar nome do arquivo no padrão DevHub
            safe_name = re.sub(r'[^\w\s-]', '', workflow_name).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            devhub_filename = f"{safe_name}_{workflow_id}.json"
            
            # Caminhos
            workflows_dir = self.model.workflows_dir
            original_path = os.path.join(workflows_dir, original_filename)
            devhub_path = os.path.join(workflows_dir, devhub_filename)
            
            # Salvar no padrão DevHub
            filepath = self.model.save_workflow_to_file(fresh_workflow, devhub_filename)
            
            if filepath:
                # Se o arquivo original for diferente do padrão DevHub, removê-lo
                if original_path != devhub_path and os.path.exists(original_path):
                    try:
                        os.remove(original_path)
                    except OSError:
                        pass  # Ignorar erro de remoção
                        
        except Exception:
            # Ignorar erros no refresh - o upload já foi bem-sucedido
            pass
    
    def upload_all_workflows(self) -> Tuple[int, int, List[str]]:
        """
        Envia todos os workflows locais
        Returns: (success_count, total_count, error_messages)
        """
        try:
            local_workflows = self.model.get_local_workflows()
            success_count = 0
            error_messages = []
            
            for wf in local_workflows:
                try:
                    workflow_data = wf['data']
                    workflow_id = workflow_data.get('id')
                    workflow_name = workflow_data.get('name', 'Unknown')
                    original_filename = wf.get('filename', '')
                    
                    # Verificar se existe remotamente
                    existing = None
                    if workflow_id:
                        existing = self.model.get_workflow_by_id(workflow_id)
                    
                    if existing:
                        # Atualizar
                        result = self.model.update_workflow(workflow_id, workflow_data)
                        action = "atualizado"
                    else:
                        # Criar
                        result = self.model.create_workflow(workflow_data)
                        action = "criado"
                    
                    if result:
                        success_count += 1
                        # Após sucesso: substituir arquivo local pela versão padrão DevHub
                        self._refresh_local_workflow_after_upload(result, original_filename)
                    else:
                        error_messages.append(f"Erro ao processar '{workflow_name}'")
                        
                except Exception as e:
                    error_messages.append(f"Erro ao processar '{wf.get('filename', 'unknown')}': {e}")
            
            return success_count, len(local_workflows), error_messages
            
        except Exception as e:
            return 0, 0, [f"Erro ao processar workflows locais: {e}"]
    
    def activate_workflow(self, identifier: str, by_id: bool = False) -> Tuple[bool, str]:
        """Ativa um workflow"""
        try:
            workflow_id = identifier
            
            if not by_id:
                # Buscar por nome
                matches = self.find_workflow_by_name(identifier)
                if len(matches) == 0:
                    return False, f"Workflow '{identifier}' não encontrado"
                elif len(matches) > 1:
                    names = [f"'{wf.name}' ({wf.id})" for wf in matches]
                    return False, f"Múltiplos workflows encontrados: {', '.join(names)}"
                
                workflow_id = matches[0].id
            
            success = self.model.activate_workflow(workflow_id)
            if success:
                return True, f"Workflow ativado com sucesso"
            else:
                return False, f"Erro ao ativar workflow"
                
        except Exception as e:
            return False, f"Erro ao ativar workflow: {e}"
    
    def deactivate_workflow(self, identifier: str, by_id: bool = False) -> Tuple[bool, str]:
        """Desativa um workflow"""
        try:
            workflow_id = identifier
            
            if not by_id:
                # Buscar por nome
                matches = self.find_workflow_by_name(identifier)
                if len(matches) == 0:
                    return False, f"Workflow '{identifier}' não encontrado"
                elif len(matches) > 1:
                    names = [f"'{wf.name}' ({wf.id})" for wf in matches]
                    return False, f"Múltiplos workflows encontrados: {', '.join(names)}"
                
                workflow_id = matches[0].id
            
            success = self.model.deactivate_workflow(workflow_id)
            if success:
                return True, f"Workflow desativado com sucesso"
            else:
                return False, f"Erro ao desativar workflow"
                
        except Exception as e:
            return False, f"Erro ao desativar workflow: {e}"
    
    def delete_remote_workflow(self, identifier: str, by_id: bool = False) -> Tuple[bool, str]:
        """Remove um workflow do n8n"""
        try:
            workflow_id = identifier
            workflow_name = identifier
            
            # Auto-detectar se é um ID (16 caracteres alfanuméricos)
            is_likely_id = len(identifier) == 16 and identifier.isalnum()
            
            if not by_id and not is_likely_id:
                # Buscar por nome
                matches = self.find_workflow_by_name(identifier)
                if len(matches) == 0:
                    return False, f"Workflow '{identifier}' não encontrado"
                elif len(matches) > 1:
                    names = [f"'{wf.name}' ({wf.id})" for wf in matches]
                    return False, f"Múltiplos workflows encontrados: {', '.join(names)}"
                
                workflow_id = matches[0].id
                workflow_name = matches[0].name
            elif is_likely_id or by_id:
                # Tentar buscar por ID para obter o nome
                workflow_info = self.find_workflow_by_id(identifier)
                if workflow_info:
                    workflow_name = workflow_info.name
                else:
                    workflow_name = identifier  # Fallback para o ID
            
            success = self.model.delete_workflow(workflow_id)
            if success:
                return True, f"Workflow '{workflow_name}' removido com sucesso"
            else:
                return False, f"Workflow '{workflow_name}' não encontrado para remoção"
                
        except Exception as e:
            return False, f"Erro ao remover workflow: {e}"
    
    def compare_local_remote(self) -> Dict:
        """Compara workflows locais e remotos"""
        try:
            local_workflows = self.model.get_local_workflows()
            remote_workflows = self.model.get_all_workflows() or []
            
            # Criar dicionários para comparação
            local_by_id = {wf.get('id'): wf for wf in local_workflows if wf.get('id')}
            remote_by_id = {wf.id: wf for wf in remote_workflows}
            
            # Análise
            only_local = []
            only_remote = []
            in_both = []
            
            # Workflows apenas locais
            for wf_id, wf in local_by_id.items():
                if wf_id not in remote_by_id:
                    only_local.append(wf)
                else:
                    in_both.append({'local': wf, 'remote': remote_by_id[wf_id]})
            
            # Workflows apenas remotos
            for wf_id, wf in remote_by_id.items():
                if wf_id not in local_by_id:
                    only_remote.append(wf)
            
            return {
                'only_local': only_local,
                'only_remote': only_remote,
                'in_both': in_both,
                'local_count': len(local_workflows),
                'remote_count': len(remote_workflows)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao comparar workflows: {e}")