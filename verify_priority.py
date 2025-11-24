import sqlite3
import os

def verify():
    db_path = 'todo.db'
    db_path = 'todo.db'
    
    # Always try to initialize/migrate the DB
    try:
        from app import init_db
        print("Initializing database (running migration)...")
        init_db()
    except ImportError:
        print("Could not import app. Make sure you are in the correct directory.")
        return
    except Exception as e:
        print(f"Error initializing DB: {e}")
        # Continue anyway to see what happens


    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check columns
    c.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in c.fetchall()]
    print(f"Columns: {columns}")
    
    if 'priority' in columns:
        print("SUCCESS: 'priority' column exists.")
    else:
        print("FAILURE: 'priority' column missing.")
        return

    # Try adding a task with priority
    try:
        c.execute("INSERT INTO tasks (name, done, priority) VALUES (?, ?, ?)", ("Test Task", 0, "High"))
        conn.commit()
        print("SUCCESS: Added task with priority.")
    except Exception as e:
        print(f"FAILURE: Could not add task. Error: {e}")

    # Verify data
    c.execute("SELECT name, priority FROM tasks WHERE name='Test Task'")
    row = c.fetchone()
    if row and row[1] == 'High':
        print(f"SUCCESS: Retrieved task '{row[0]}' with priority '{row[1]}'.")
    else:
        print("FAILURE: Could not retrieve task or priority mismatch.")

    # Clean up
    c.execute("DELETE FROM tasks WHERE name='Test Task'")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    verify()
