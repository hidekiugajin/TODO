import sqlite3
import os

def verify_db():
    if not os.path.exists('todo.db'):
        print("FAIL: todo.db does not exist.")
        return

    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        
        # Check table existence
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if not c.fetchone():
            print("FAIL: Table 'tasks' does not exist.")
            return
            
        # Check schema
        c.execute("PRAGMA table_info(tasks)")
        columns = {row[1]: row[2] for row in c.fetchall()}
        expected_columns = {'id': 'INTEGER', 'name': 'TEXT', 'done': 'BOOLEAN'}
        
        for col, type_ in expected_columns.items():
            if col not in columns:
                print(f"FAIL: Column '{col}' missing.")
                return
                
        print("SUCCESS: Database and schema verified.")
        conn.close()
    except Exception as e:
        print(f"FAIL: Error verifying database: {e}")

if __name__ == "__main__":
    verify_db()
