#!/usr/bin/env python3
import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class N8NDatabase:
    def __init__(self):
        self.db_path = Path(__file__).parent / "n8n_data" / "database.sqlite"
        
    def connect(self):
        """Conecta ao banco SQLite do n8n"""
        if not self.db_path.exists():
            print(f"❌ Banco de dados não encontrado: {self.db_path}")
            return None
        return sqlite3.connect(str(self.db_path))

    def list_tables(self):
        """Lista todas as tabelas do banco"""
        conn = self.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def describe_table(self, table_name):
        """Descreve a estrutura de uma tabela"""
        conn = self.connect()
        if not conn:
            return None
            
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        conn.close()
        return columns

    def get_workflows(self):
        """Busca todos os workflows do banco"""
        conn = self.connect()
        if not conn:
            return []
            
        query = """
        SELECT id, name, active, nodes, connections, settings, 
               createdAt, updatedAt, tags
        FROM workflow_entity
        ORDER BY updatedAt DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_executions(self, limit=50):
        """Busca execuções recentes"""
        conn = self.connect()
        if not conn:
            return []
            
        query = """
        SELECT id, workflowId, mode, retryOf, status, 
               startedAt, stoppedAt, finished
        FROM execution_entity 
        ORDER BY startedAt DESC 
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        return df

    def get_workflow_executions(self, workflow_id, limit=20):
        """Busca execuções de um workflow específico"""
        conn = self.connect()
        if not conn:
            return []
            
        query = """
        SELECT id, mode, retryOf, status, startedAt, stoppedAt, finished
        FROM execution_entity 
        WHERE workflowId = ?
        ORDER BY startedAt DESC 
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=[workflow_id, limit])
        conn.close()
        return df

    def export_workflow_json(self, workflow_id):
        """Exporta workflow específico como JSON"""
        conn = self.connect()
        if not conn:
            return None
            
        cursor = conn.cursor()
        cursor.execute("""
        SELECT name, nodes, connections, settings, active, tags
        FROM workflow_entity 
        WHERE id = ?
        """, (workflow_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        workflow = {
            'name': row[0],
            'nodes': json.loads(row[1]) if row[1] else [],
            'connections': json.loads(row[2]) if row[2] else {},
            'settings': json.loads(row[3]) if row[3] else {},
            'active': bool(row[4]),
            'tags': json.loads(row[5]) if row[5] else []
        }
        
        return workflow

    def backup_database(self, backup_path=None):
        """Cria backup do banco de dados"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"n8n_backup_{timestamp}.sqlite"
        
        conn = self.connect()
        if not conn:
            return False
            
        try:
            backup = sqlite3.connect(backup_path)
            conn.backup(backup)
            backup.close()
            conn.close()
            print(f"✅ Backup criado: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return False

    def interactive_query(self):
        """Interface interativa para queries SQL"""
        conn = self.connect()
        if not conn:
            return
            
        print("🗃️  Interface de consulta n8n SQLite")
        print("Digite 'quit' para sair, 'tables' para listar tabelas")
        print("Exemplo: SELECT * FROM workflow_entity LIMIT 5;")
        print("-" * 50)
        
        while True:
            try:
                query = input("SQL> ").strip()
                
                if query.lower() in ['quit', 'exit']:
                    break
                elif query.lower() == 'tables':
                    tables = self.list_tables()
                    print("Tabelas disponíveis:")
                    for table in tables:
                        print(f"  - {table}")
                    continue
                elif not query:
                    continue
                
                cursor = conn.cursor()
                cursor.execute(query)
                
                if query.upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    if results:
                        df = pd.DataFrame(results, columns=columns)
                        print(df.to_string(index=False))
                    else:
                        print("Nenhum resultado encontrado.")
                else:
                    conn.commit()
                    print(f"Query executada. Linhas afetadas: {cursor.rowcount}")
                    
            except Exception as e:
                print(f"Erro: {e}")
        
        conn.close()

def main():
    db = N8NDatabase()
    
    print("🗃️  n8n Database Access Tool")
    print("=" * 40)
    print("1. Listar workflows")
    print("2. Ver execuções recentes")
    print("3. Exportar workflow")
    print("4. Criar backup")
    print("5. Consulta interativa")
    print("0. Sair")
    
    while True:
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            workflows = db.get_workflows()
            print("\n📋 Workflows:")
            print(workflows[['id', 'name', 'active', 'updatedAt']].to_string(index=False))
        elif choice == '2':
            executions = db.get_executions()
            print("\n🏃 Execuções Recentes:")
            print(executions[['id', 'workflowId', 'status', 'startedAt']].to_string(index=False))
        elif choice == '3':
            workflow_id = input("ID do workflow: ")
            workflow = db.export_workflow_json(workflow_id)
            if workflow:
                filename = f"workflow_{workflow_id}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(workflow, f, indent=2, ensure_ascii=False)
                print(f"✅ Workflow exportado: {filename}")
            else:
                print("❌ Workflow não encontrado")
        elif choice == '4':
            db.backup_database()
        elif choice == '5':
            db.interactive_query()

if __name__ == "__main__":
    main()