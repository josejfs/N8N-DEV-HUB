"""
N8N-DevHub - Workflow Model
Gerencia dados e operações relacionadas a workflows do n8n
"""

import requests
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class WorkflowInfo:
    """Informações básicas de um workflow"""
    id: str
    name: str
    active: bool
    created_at: str
    updated_at: str
    is_archived: bool = False


class WorkflowModel:
    """Model para gerenciar workflows do n8n"""
    
    def __init__(self, base_url: str = None, api_key: str = None, basic_auth: Tuple[str, str] = None):
        # Configuração da conexão
        from dotenv import load_dotenv
        load_dotenv()
        
        # URL do n8n - Simples e direto
        if not base_url:
            base_url = os.getenv('N8N_URL', 'http://localhost:5678')
        
        self.base_url = base_url.rstrip('/')
        
        # Diretório de workflows (na raiz do projeto)
        # Se executando de dentro de N8N-DevHub, sobe um nível
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if 'N8N-DevHub' in current_dir:
            self.workflows_dir = os.path.join(current_dir, '../../workflows')
        else:
            self.workflows_dir = "./workflows"
        
        # Normalizar o caminho
        self.workflows_dir = os.path.normpath(self.workflows_dir)
        
        # Headers para requisições
        self.headers = {'Content-Type': 'application/json'}
        
        # Configurar autenticação
        if api_key or os.getenv('API_N8N'):
            self.headers['X-N8N-API-KEY'] = api_key or os.getenv('API_N8N')
        elif basic_auth or (os.getenv('N8N_BASIC_AUTH_USER') and os.getenv('N8N_BASIC_AUTH_PASSWORD')):
            import base64
            if basic_auth:
                user, password = basic_auth
            else:
                user = os.getenv('N8N_BASIC_AUTH_USER')
                password = os.getenv('N8N_BASIC_AUTH_PASSWORD')
            
            credentials = base64.b64encode(f"{user}:{password}".encode()).decode()
            self.headers['Authorization'] = f'Basic {credentials}'
        
        # Garantir que diretório existe
        os.makedirs(self.workflows_dir, exist_ok=True)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Faz requisição HTTP para a API do n8n"""
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('timeout', 10)
        
        return requests.request(method, url, **kwargs)
    
    def get_all_workflows(self) -> Optional[List[WorkflowInfo]]:
        """Busca todos os workflows do n8n"""
        try:
            response = self._make_request('GET', 'workflows')
            
            if response.status_code == 200:
                data = response.json()
                workflows_data = data.get('data', []) if isinstance(data, dict) else data
                
                workflows = []
                for wf in workflows_data:
                    workflows.append(WorkflowInfo(
                        id=wf.get('id'),
                        name=wf.get('name'),
                        active=wf.get('active', False),
                        created_at=wf.get('createdAt'),
                        updated_at=wf.get('updatedAt'),
                        is_archived=wf.get('isArchived', False)
                    ))
                
                return workflows
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception(f"Não foi possível conectar ao n8n em {self.base_url}")
        except requests.exceptions.Timeout:
            raise Exception("Timeout: n8n não respondeu em 10 segundos")
    
    def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict]:
        """Busca um workflow específico por ID"""
        try:
            response = self._make_request('GET', f'workflows/{workflow_id}')
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', data) if isinstance(data, dict) and 'data' in data else data
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"Erro ao buscar workflow {workflow_id}: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão ao buscar workflow {workflow_id}: {e}")
    
    def _clean_workflow_data(self, workflow_data: Dict) -> Dict:
        """Limpa dados do workflow removendo propriedades que causam problemas no upload"""
        import copy
        
        # Criar cópia profunda para não modificar o original
        clean_data = copy.deepcopy(workflow_data)
        
        # Remover campos do workflow principal (read-only ou gerados automaticamente)
        fields_to_remove = [
            'id', 'createdAt', 'updatedAt', 'shared', 'versionId', 'meta', 
            'active', 'tags', 'pinData', 'triggerCount', 'isArchived'
        ]
        for field in fields_to_remove:
            clean_data.pop(field, None)
        
        # Limpar nós individuais
        if 'nodes' in clean_data and isinstance(clean_data['nodes'], list):
            for node in clean_data['nodes']:
                if isinstance(node, dict):
                    # Remover id e webhookId dos nós
                    node.pop('id', None)
                    node.pop('webhookId', None)
                    
                    # Remover IDs de credenciais (serão reassociadas por nome)
                    if 'credentials' in node and isinstance(node['credentials'], dict):
                        for cred_type, cred_data in node['credentials'].items():
                            if isinstance(cred_data, dict):
                                cred_data.pop('id', None)
        
        return clean_data

    def create_workflow(self, workflow_data: Dict) -> Optional[Dict]:
        """Cria um novo workflow"""
        try:
            # Limpar dados do workflow
            clean_data = self._clean_workflow_data(workflow_data)
            
            response = self._make_request('POST', 'workflows', json=clean_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get('data', data) if isinstance(data, dict) and 'data' in data else data
            else:
                raise Exception(f"Erro ao criar workflow: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão ao criar workflow: {e}")
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> Optional[Dict]:
        """Atualiza um workflow existente"""
        try:
            # Limpar dados do workflow
            clean_data = self._clean_workflow_data(workflow_data)
            
            response = self._make_request('PUT', f'workflows/{workflow_id}', json=clean_data)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', data) if isinstance(data, dict) and 'data' in data else data
            else:
                raise Exception(f"Erro ao atualizar workflow {workflow_id}: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão ao atualizar workflow: {e}")
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Remove um workflow"""
        try:
            response = self._make_request('DELETE', f'workflows/{workflow_id}')
            
            if response.status_code in [200, 204]:
                return True
            elif response.status_code == 404:
                return False
            else:
                raise Exception(f"Erro ao deletar workflow {workflow_id}: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão ao deletar workflow: {e}")
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Ativa um workflow"""
        try:
            response = self._make_request('POST', f'workflows/{workflow_id}/activate')
            return response.status_code == 200
        except:
            return False
    
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Desativa um workflow"""
        try:
            response = self._make_request('POST', f'workflows/{workflow_id}/deactivate')
            return response.status_code == 200
        except:
            return False
    
    # Métodos para arquivos locais
    
    def get_local_workflows(self) -> List[Dict]:
        """Lista workflows locais na pasta workflows/"""
        import glob
        
        workflow_files = glob.glob(os.path.join(self.workflows_dir, "*.json"))
        workflows = []
        
        for filepath in workflow_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extrair ID do nome do arquivo se possível
                filename = os.path.basename(filepath)
                workflow_id = self.extract_id_from_filename(filename)
                
                workflows.append({
                    'filepath': filepath,
                    'filename': filename,
                    'id': data.get('id', workflow_id),
                    'name': data.get('name', 'Unknown'),
                    'active': data.get('active', False),
                    'data': data
                })
                
            except Exception as e:
                print(f"Erro ao ler {filepath}: {e}")
                continue
        
        return workflows
    
    def extract_id_from_filename(self, filename: str) -> Optional[str]:
        """Extrai ID do workflow do nome do arquivo (formato: nome_ID.json)"""
        match = re.search(r'_([a-zA-Z0-9]+)\.json$', filename)
        return match.group(1) if match else None
    
    def generate_filename(self, workflow_name: str, workflow_id: str) -> str:
        """Gera nome de arquivo padrão para um workflow"""
        # Sanitizar nome
        safe_name = re.sub(r'[^\w\s-]', '', workflow_name).strip()
        safe_name = re.sub(r'\s+', ' ', safe_name)  # Normalizar espaços
        safe_name = safe_name.replace(' ', '_')
        
        return f"{safe_name}_{workflow_id}.json"
    
    def save_workflow_to_file(self, workflow_data: Dict, custom_filename: str = None) -> str:
        """Salva workflow em arquivo local"""
        workflow_id = workflow_data.get('id', 'unknown')
        workflow_name = workflow_data.get('name', 'Unknown')
        
        if custom_filename:
            filename = custom_filename
        else:
            filename = self.generate_filename(workflow_name, workflow_id)
        
        filepath = os.path.join(self.workflows_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_workflow_from_file(self, filename: str) -> Optional[Dict]:
        """Carrega workflow de arquivo local"""
        filepath = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None