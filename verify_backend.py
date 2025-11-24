import sqlite3
import os
from app import init_db, add_task, get_tasks, edit_task, delete_task

# Setup
if os.path.exists("todo.db"):
    os.remove("todo.db")
init_db()

# Test Add
print("Testing Add Task...")
add_task("Test Task", "High", "2023-12-31", "This is a note", "Work")
tasks = get_tasks()
assert len(tasks) == 1
assert tasks[0]['name'] == "Test Task"
assert tasks[0]['priority'] == "High"
assert tasks[0]['note'] == "This is a note"
assert tasks[0]['category'] == "Work"
print("Add Task Passed!")

# Test Edit
print("Testing Edit Task...")
task_id = tasks[0]['id']
edit_task(task_id, "Updated Task", "Medium", "2024-01-01", "Updated Note", "Personal")
tasks = get_tasks()
assert tasks[0]['name'] == "Updated Task"
assert tasks[0]['priority'] == "Medium"
assert tasks[0]['note'] == "Updated Note"
assert tasks[0]['category'] == "Personal"
print("Edit Task Passed!")

# Test Delete
print("Testing Delete Task...")
delete_task(task_id)
tasks = get_tasks()
assert len(tasks) == 0
print("Delete Task Passed!")

print("All backend tests passed!")
