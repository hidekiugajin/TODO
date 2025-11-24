import sqlite3
import os

def verify_deadline():
    print("Verifying deadline feature...")
    
    # Ensure database exists (app.py creates it, but we might be running this independently)
    # We'll assume app.py's init_db has been run or we can run it here if needed.
    # For now, let's just connect and see if we can add tasks with deadlines.
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    
    # Check if deadline column exists
    try:
        c.execute('SELECT deadline FROM tasks LIMIT 1')
        print("PASS: 'deadline' column exists.")
    except sqlite3.OperationalError:
        print("FAIL: 'deadline' column does not exist.")
        return

    # Add a task with a deadline
    task_name = "Test Task with Deadline"
    priority = "High"
    deadline = "2023-12-31"
    
    try:
        c.execute('INSERT INTO tasks (name, done, priority, deadline) VALUES (?, ?, ?, ?)', (task_name, False, priority, deadline))
        conn.commit()
        print(f"PASS: Added task '{task_name}' with deadline '{deadline}'.")
    except Exception as e:
        print(f"FAIL: Could not add task with deadline. Error: {e}")
        return

    # Add a task without a deadline (None)
    task_name_no_deadline = "Test Task No Deadline"
    priority_no_deadline = "Low"
    deadline_no_deadline = None
    
    try:
        c.execute('INSERT INTO tasks (name, done, priority, deadline) VALUES (?, ?, ?, ?)', (task_name_no_deadline, False, priority_no_deadline, deadline_no_deadline))
        conn.commit()
        print(f"PASS: Added task '{task_name_no_deadline}' with no deadline.")
    except Exception as e:
        print(f"FAIL: Could not add task without deadline. Error: {e}")
        return

    # Verify data retrieval
    c.execute('SELECT name, deadline FROM tasks WHERE name = ?', (task_name,))
    row = c.fetchone()
    if row and row[1] == deadline:
        print(f"PASS: Retrieved task '{task_name}' with correct deadline '{row[1]}'.")
    else:
        print(f"FAIL: Retrieved task '{task_name}' but deadline was '{row[1] if row else 'None'}', expected '{deadline}'.")

    c.execute('SELECT name, deadline FROM tasks WHERE name = ?', (task_name_no_deadline,))
    row = c.fetchone()
    if row and row[1] is None:
        print(f"PASS: Retrieved task '{task_name_no_deadline}' with correct deadline (None).")
    else:
        print(f"FAIL: Retrieved task '{task_name_no_deadline}' but deadline was '{row[1] if row else 'None'}', expected None.")

    # Clean up
    c.execute('DELETE FROM tasks WHERE name IN (?, ?)', (task_name, task_name_no_deadline))
    conn.commit()
    conn.close()
    print("Verification complete.")

if __name__ == "__main__":
    # We need to make sure the DB schema is updated first. 
    # Since we can't easily import init_db from app.py without running the streamlit app,
    # we will rely on the fact that the user (or previous steps) might have run the app, 
    # OR we can manually run the migration here just in case.
    
    # Let's try to run the migration logic here to be safe, mimicking app.py
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN deadline TEXT')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
    
    verify_deadline()
