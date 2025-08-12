#!/usr/bin/env python3
import os
import json
import sqlite3
import time
import asyncio
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib

class N8NSync:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.workflows_dir = self.base_dir / "workflows"
        self.n8n_data_dir = self.base_dir / "n8n_data"
        self.db_path = self.n8n_data_dir / "database.sqlite"
        
        # Criar diretórios necessários
        self.workflows_dir.mkdir(exist_ok=True)
        self.n8n_data_dir.mkdir(exist_ok=True)
        
        self.file_hashes = {}
        self.last_sync = {}

    def get_file_hash(self, filepath):
        """Gera hash MD5 do arquivo para detectar mudanças"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None

    def wait_for_db(self):
        """Aguarda banco de dados estar disponível"""
        print("Aguardando banco de dados...")
        max_attempts = 30
        for i in range(max_attempts):
            if self.db_path.exists():
                try:
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workflow_entity';")
                    if cursor.fetchone():
                        conn.close()
                        print("✅ Banco de dados pronto!")
                        return True
                    conn.close()
                except:
                    pass
            print(f"Tentativa {i+1}/{max_attempts}...")
            time.sleep(2)
        return False

    def get_workflows_from_db(self):
        """Busca workflows diretamente do banco SQLite"""
        try:
            if not self.db_path.exists():
                return []
                
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Verificar se coluna tags existe
            cursor.execute("PRAGMA table_info(workflow_entity)")
            columns = [col[1] for col in cursor.fetchall()]
            has_tags = 'tags' in columns
            
            if has_tags:
                cursor.execute("""
                    SELECT id, name, active, nodes, connections, settings, 
                           createdAt, updatedAt, tags
                    FROM workflow_entity
                    ORDER BY updatedAt DESC
                """)
            else:
                cursor.execute("""
                    SELECT id, name, active, nodes, connections, settings, 
                           createdAt, updatedAt
                    FROM workflow_entity
                    ORDER BY updatedAt DESC
                """)
            
            workflows = []
            for row in cursor.fetchall():
                workflow = {
                    'id': row[0],
                    'name': row[1],
                    'active': bool(row[2]),
                    'nodes': json.loads(row[3]) if row[3] else [],
                    'connections': json.loads(row[4]) if row[4] else {},
                    'settings': json.loads(row[5]) if row[5] else {},
                    'createdAt': row[6],
                    'updatedAt': row[7],
                    'tags': json.loads(row[8]) if has_tags and row[8] else []
                }
                workflows.append(workflow)
            
            conn.close()
            return workflows
            
        except Exception as e:
            print(f"Erro ao acessar banco: {e}")
            return []

    def save_workflow_to_file(self, workflow):
        """Salva workflow em arquivo JSON"""
        filename = f"{workflow['name'].replace(' ', '_').replace('/', '_')}.json"
        filepath = self.workflows_dir / filename
        
        # Preparar dados do workflow para salvar
        workflow_data = {
            'id': workflow.get('id'),
            'name': workflow['name'],
            'active': workflow.get('active', False),
            'nodes': workflow.get('nodes', []),
            'connections': workflow.get('connections', {}),
            'settings': workflow.get('settings', {}),
            'staticData': workflow.get('staticData', {}),
            'tags': workflow.get('tags', []),
            'meta': {
                'lastModified': datetime.now().isoformat(),
                'syncedFromDB': True
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        
        # Atualizar hash
        self.file_hashes[str(filepath)] = self.get_file_hash(filepath)
        print(f"📥 Workflow salvo: {filename}")

    def load_workflow_from_file(self, filepath):
        """Carrega workflow de arquivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar workflow {filepath}: {e}")
            return None

    def save_workflow_to_db(self, workflow_data):
        """Salva workflow diretamente no banco SQLite"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Verificar colunas disponíveis
            cursor.execute("PRAGMA table_info(workflow_entity)")
            columns = [col[1] for col in cursor.fetchall()]
            has_tags = 'tags' in columns
            
            # Verificar se workflow já existe
            cursor.execute("SELECT id FROM workflow_entity WHERE name = ?", (workflow_data['name'],))
            existing = cursor.fetchone()
            
            nodes_json = json.dumps(workflow_data.get('nodes', []))
            connections_json = json.dumps(workflow_data.get('connections', {}))
            settings_json = json.dumps(workflow_data.get('settings', {}))
            
            if existing:
                # Atualizar workflow existente
                if has_tags:
                    tags_json = json.dumps(workflow_data.get('tags', []))
                    cursor.execute("""
                        UPDATE workflow_entity 
                        SET nodes = ?, connections = ?, settings = ?, 
                            active = ?, tags = ?, updatedAt = ?
                        WHERE id = ?
                    """, (nodes_json, connections_json, settings_json, 
                          workflow_data.get('active', False), tags_json, 
                          datetime.now().isoformat(), existing[0]))
                else:
                    cursor.execute("""
                        UPDATE workflow_entity 
                        SET nodes = ?, connections = ?, settings = ?, 
                            active = ?, updatedAt = ?
                        WHERE id = ?
                    """, (nodes_json, connections_json, settings_json, 
                          workflow_data.get('active', False), 
                          datetime.now().isoformat(), existing[0]))
                print(f"📤 Workflow atualizado no banco: {workflow_data['name']}")
            else:
                # Criar novo workflow
                if has_tags:
                    tags_json = json.dumps(workflow_data.get('tags', []))
                    cursor.execute("""
                        INSERT INTO workflow_entity 
                        (name, nodes, connections, settings, active, tags, createdAt, updatedAt)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (workflow_data['name'], nodes_json, connections_json, 
                          settings_json, workflow_data.get('active', False), 
                          tags_json, datetime.now().isoformat(), datetime.now().isoformat()))
                else:
                    cursor.execute("""
                        INSERT INTO workflow_entity 
                        (name, nodes, connections, settings, active, createdAt, updatedAt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (workflow_data['name'], nodes_json, connections_json, 
                          settings_json, workflow_data.get('active', False), 
                          datetime.now().isoformat(), datetime.now().isoformat()))
                print(f"📤 Workflow criado no banco: {workflow_data['name']}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            return False

    def sync_from_db_to_files(self):
        """Sincroniza workflows do banco para arquivos locais"""
        print("🔄 Sincronizando do banco para arquivos...")
        workflows = self.get_workflows_from_db()
        
        # Obter workflows ativos do banco
        active_workflow_names = set()
        for workflow in workflows:
            self.save_workflow_to_file(workflow)
            active_workflow_names.add(workflow['name'])
        
        # Verificar arquivos locais que não existem mais no banco
        self.cleanup_deleted_workflows(active_workflow_names)

    def sync_from_files_to_db(self):
        """Sincroniza arquivos locais para banco"""
        print("🔄 Sincronizando arquivos para banco...")
        
        if not self.workflows_dir.exists():
            return
        
        for json_file in self.workflows_dir.glob("*.json"):
            current_hash = self.get_file_hash(json_file)
            stored_hash = self.file_hashes.get(str(json_file))
            
            # Verificar se arquivo foi modificado
            if current_hash != stored_hash:
                workflow_data = self.load_workflow_from_file(json_file)
                if workflow_data and not workflow_data.get('meta', {}).get('syncedFromDB'):
                    if self.save_workflow_to_db(workflow_data):
                        self.file_hashes[str(json_file)] = current_hash

    def cleanup_deleted_workflows(self, active_workflow_names):
        """Remove arquivos locais de workflows que foram deletados/arquivados no n8n"""
        if not self.workflows_dir.exists():
            return
            
        for json_file in self.workflows_dir.glob("*.json"):
            # Extrair nome do workflow do arquivo
            workflow_name = self.extract_workflow_name_from_file(json_file)
            
            if workflow_name and workflow_name not in active_workflow_names:
                try:
                    # Criar backup antes de deletar
                    backup_name = f"{json_file.stem}_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    backup_path = self.workflows_dir / f"_archived/{backup_name}"
                    backup_path.parent.mkdir(exist_ok=True)
                    
                    # Mover para pasta de arquivados
                    json_file.rename(backup_path)
                    print(f"🗃️  Workflow arquivado: {workflow_name} → _archived/{backup_name}")
                    
                    # Remover do cache de hashes
                    if str(json_file) in self.file_hashes:
                        del self.file_hashes[str(json_file)]
                        
                except Exception as e:
                    print(f"Erro ao arquivar workflow {workflow_name}: {e}")

    def extract_workflow_name_from_file(self, json_file):
        """Extrai nome do workflow do arquivo JSON"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
                return workflow_data.get('name')
        except Exception as e:
            print(f"Erro ao ler workflow {json_file}: {e}")
            # Fallback: tentar extrair do nome do arquivo
            filename = json_file.stem
            return filename.replace('_', ' ') if filename != 'exemplo_workflow' else None

class WorkflowFileHandler(FileSystemEventHandler):
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager
        
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
            
        # Aguarda um pouco para garantir que o arquivo foi completamente escrito
        time.sleep(1)
        
        print(f"📝 Arquivo modificado: {event.src_path}")
        workflow_data = self.sync_manager.load_workflow_from_file(event.src_path)
        if workflow_data and not workflow_data.get('meta', {}).get('syncedFromDB'):
            self.sync_manager.save_workflow_to_db(workflow_data)

async def periodic_sync(sync_manager):
    """Sincronização periódica a cada 30 segundos"""
    while True:
        try:
            sync_manager.sync_from_db_to_files()
        except Exception as e:
            print(f"Erro na sincronização periódica: {e}")
        await asyncio.sleep(30)

def main():
    sync_manager = N8NSync()
    
    # Aguardar banco estar disponível
    if not sync_manager.wait_for_db():
        print("❌ Banco de dados não conseguiu inicializar. Verifique o n8n.")
        return
    
    # Sincronização inicial
    sync_manager.sync_from_db_to_files()
    
    # Configurar monitoramento de arquivos
    event_handler = WorkflowFileHandler(sync_manager)
    observer = Observer()
    observer.schedule(event_handler, str(sync_manager.workflows_dir), recursive=False)
    observer.start()
    
    print("🚀 Sincronização bidirecional iniciada!")
    print(f"📁 Monitorando: {sync_manager.workflows_dir}")
    print(f"💾 Banco: {sync_manager.db_path}")
    print("Press Ctrl+C to stop")
    
    try:
        # Iniciar sincronização periódica
        asyncio.run(periodic_sync(sync_manager))
    except KeyboardInterrupt:
        print("\n🛑 Parando sincronização...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()