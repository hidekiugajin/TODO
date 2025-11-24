import streamlit as st
import sqlite3
import csv
import os
import pandas as pd
import plotly.express as px
import datetime
import numpy as np

# Database helper functions
def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            done BOOLEAN NOT NULL CHECK (done IN (0, 1)),
            priority TEXT DEFAULT 'Medium'
        )
    ''')
    
    # Migration: Add priority column if it doesn't exist
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT "Medium"')
    except sqlite3.OperationalError:
        pass

    # Migration: Add deadline column if it doesn't exist
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN deadline TEXT')
    except sqlite3.OperationalError:
        pass

    # Migration: Add note column if it doesn't exist
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN note TEXT')
    except sqlite3.OperationalError:
        pass

    # Migration: Add category column if it doesn't exist
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT "General"')
    except sqlite3.OperationalError:
        pass

    # Migration: Add start_date column if it doesn't exist
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN start_date TEXT')
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('SELECT id, name, done, priority, deadline, note, category, start_date FROM tasks')
    tasks = [
        {
            "id": row[0], 
            "name": row[1], 
            "done": bool(row[2]), 
            "priority": row[3], 
            "deadline": row[4],
            "note": row[5],
            "category": row[6],
            "start_date": row[7]
        } 
        for row in c.fetchall()
    ]
    conn.close()
    return tasks

def add_task(name, priority, deadline, note, category, start_date):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (name, done, priority, deadline, note, category, start_date) VALUES (?, ?, ?, ?, ?, ?, ?)', 
              (name, False, priority, deadline, note, category, start_date))
    conn.commit()
    conn.close()

def edit_task(task_id, name, priority, deadline, note, category, start_date):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''
        UPDATE tasks 
        SET name = ?, priority = ?, deadline = ?, note = ?, category = ?, start_date = ? 
        WHERE id = ?
    ''', (name, priority, deadline, note, category, start_date, task_id))
    conn.commit()
    conn.close()

def update_task_status(task_id, done):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET done = ? WHERE id = ?', (done, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def export_to_csv():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('SELECT id, name, done, priority, deadline, note, category FROM tasks')
    rows = c.fetchall()
    conn.close()

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, "todo_export.csv")

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Task Name", "Done", "Priority", "Deadline", "Note", "Category"])
        writer.writerows(rows)
    
    return file_path

def main():
    st.set_page_config(page_title="Nomad Crab ToDo", layout="wide")
    st.title("🦀 Nomad Crab ToDo")

    # Initialize database
    init_db()

    # --- Sidebar Navigation & Filters ---
    with st.sidebar:
        st.header("Navigation")
        view_mode = st.radio("View Mode", ["List View", "Gantt Chart"])
        
        st.divider()
        
        st.header("🔍 Filters & Actions")
        
        # Search
        search_query = st.text_input("Search tasks", placeholder="Keyword...")
        
        # Priority Filter
        priority_filter = st.multiselect("Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        
        # Category Filter (Dynamic)
        all_tasks = get_tasks()
        all_categories = sorted(list(set([t['category'] for t in all_tasks if t['category']])))
        category_filter = st.multiselect("Category", all_categories, default=all_categories)
        
        # Date Filter
        date_filter = st.selectbox("Deadline", ["All", "Today", "This Week", "Overdue"])

        st.markdown("---")
        st.header("Actions")
        if st.button("Export to CSV"):
            try:
                file_path = export_to_csv()
                st.success(f"Tasks exported to: {file_path}")
            except Exception as e:
                st.error(f"Error exporting tasks: {e}")

    # --- Add New Task ---
    with st.expander("➕ Add New Task", expanded=False):
        with st.form(key='add_task_form', clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                new_task = st.text_input("Task Name", placeholder="What needs to be done?")
                new_note = st.text_area("Note", placeholder="Additional details...", height=68)
            with col2:
                new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
                
                # Date columns
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    new_start_date = st.date_input("Start Date", value=datetime.date.today())
                with d_col2:
                    new_deadline = st.date_input("Deadline", value=None)
                
                # Category Selection Logic
                category_options = ["Create New..."] + all_categories
                selected_category = st.selectbox("Category", category_options, index=1 if "General" in all_categories else 0)
                
                if selected_category == "Create New...":
                    new_category = st.text_input("New Category Name", placeholder="e.g. Work, Personal")
                else:
                    new_category = selected_category
            
            submit_button = st.form_submit_button(label='Add Task', use_container_width=True)

        if submit_button:
            if new_task:
                add_task(new_task, new_priority, new_deadline, new_note, new_category, new_start_date)
                st.success(f"Added task: {new_task}")
                st.rerun()
            else:
                st.warning("Please enter a task name.")

    # --- Logic: Filter & Sort ---
    # import datetime # Already imported at top
    
    filtered_tasks = all_tasks

    # 1. Search
    if search_query:
        filtered_tasks = [t for t in filtered_tasks if search_query.lower() in t['name'].lower() or (t['note'] and search_query.lower() in t['note'].lower())]

    # 2. Priority
    if priority_filter:
        filtered_tasks = [t for t in filtered_tasks if t['priority'] in priority_filter]

    # 3. Category
    if category_filter:
        filtered_tasks = [t for t in filtered_tasks if t['category'] in category_filter]

    # 4. Date
    today = datetime.date.today()
    if date_filter == "Today":
        filtered_tasks = [t for t in filtered_tasks if t['deadline'] == str(today)]
    elif date_filter == "This Week":
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        filtered_tasks = [t for t in filtered_tasks if t['deadline'] and start_of_week <= datetime.datetime.strptime(t['deadline'], '%Y-%m-%d').date() <= end_of_week]
    elif date_filter == "Overdue":
        filtered_tasks = [t for t in filtered_tasks if t['deadline'] and datetime.datetime.strptime(t['deadline'], '%Y-%m-%d').date() < today and not t['done']]

    # Sorting
    # Priority Order: High=3, Medium=2, Low=1
    priority_map = {"High": 3, "Medium": 2, "Low": 1}
    
    filtered_tasks.sort(key=lambda x: (
        x['done'], # Completed last
        -priority_map.get(x['priority'], 0), # High priority first
        x['deadline'] if x['deadline'] else "9999-99-99" # Earliest deadline first
    ))

    # --- Progress Bar ---
    total_tasks_count = len(filtered_tasks)
    completed_tasks_count = len([t for t in filtered_tasks if t['done']])
    if total_tasks_count > 0:
        progress = completed_tasks_count / total_tasks_count
        st.progress(progress, text=f"Progress: {int(progress * 100)}%")
    else:
        st.progress(0, text="No tasks found")

    if view_mode == "List View":
        # --- Task List Rendering ---
        st.subheader(f"Your Tasks ({len(filtered_tasks)})")
        
        if not filtered_tasks:
            st.info("No tasks match your filters.")
        else:
            for task in filtered_tasks:
                # Row Styling
                priority_color = {
                    "High": "rgba(255, 0, 0, 0.1)",
                    "Medium": "rgba(255, 165, 0, 0.1)",
                    "Low": "rgba(0, 128, 0, 0.1)"
                }
                bg_color = priority_color.get(task['priority'], "transparent")
                if task['done']:
                    bg_color = "rgba(200, 200, 200, 0.1)" # Grey out completed

                # Check overdue
                is_overdue = False
                if task['deadline'] and not task['done']:
                    deadline_date = datetime.datetime.strptime(task['deadline'], '%Y-%m-%d').date()
                    if deadline_date < today:
                        is_overdue = True

                with st.container():
                    # Custom CSS for row background is hard in pure Streamlit without unsafe_allow_html
                    # We'll use columns and standard widgets, but add visual cues.
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([0.05, 0.4, 0.15, 0.15, 0.15, 0.1])
                    
                    # Checkbox
                    done = col1.checkbox("", value=task["done"], key=f"done_{task['id']}")
                    if done != task["done"]:
                        update_task_status(task["id"], done)
                        st.rerun()

                    # Task Name & Note
                    with col2:
                        name_html = f"**{task['name']}**"
                        if task['done']:
                            name_html = f"~~{task['name']}~~"
                        
                        if is_overdue:
                            name_html = f"<span style='color:red'>⚠️ {name_html}</span>"
                        
                        st.markdown(name_html, unsafe_allow_html=True)
                        if task['note']:
                            st.caption(task['note'])

                    # Priority
                    priority_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}
                    col3.text(f"{priority_emoji.get(task['priority'], '')} {task['priority']}")

                    # Deadline
                    deadline_str = task['deadline'] if task['deadline'] else "-"
                    if is_overdue:
                        col4.markdown(f":red[{deadline_str}]")
                    else:
                        col4.text(deadline_str)

                    # Category
                    col5.markdown(f"`{task['category']}`")

                    # Actions (Edit/Delete)
                    with col6:
                        # Delete
                        if st.button("🗑️", key=f"delete_{task['id']}", help="Delete Task"):
                            delete_task(task["id"])
                            st.rerun()

                    # Edit Expander (Full width below the row)
                    with st.expander("Edit Details"):
                        with st.form(key=f"edit_form_{task['id']}"):
                            e_name = st.text_input("Task Name", value=task['name'])
                            e_col1, e_col2 = st.columns(2)
                            with e_col1:
                                e_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task['priority']))
                                
                                # Edit Category Logic
                                e_cat_options = ["Create New..."] + all_categories
                                # Ensure current category is in options, if not (shouldn't happen normally but for safety), add it
                                if task['category'] not in e_cat_options:
                                    e_cat_options.append(task['category'])
                                    
                                e_cat_index = e_cat_options.index(task['category'])
                                e_selected_cat = st.selectbox("Category", e_cat_options, index=e_cat_index, key=f"cat_select_{task['id']}")
                                
                                if e_selected_cat == "Create New...":
                                    e_category = st.text_input("New Category Name", key=f"new_cat_{task['id']}")
                                else:
                                    e_category = e_selected_cat
                            with e_col2:
                                e_start_val = datetime.datetime.strptime(task['start_date'], '%Y-%m-%d').date() if task.get('start_date') else None
                                e_start_date = st.date_input("Start Date", value=e_start_val)
                                
                                e_deadline_val = datetime.datetime.strptime(task['deadline'], '%Y-%m-%d').date() if task['deadline'] else None
                                e_deadline = st.date_input("Deadline", value=e_deadline_val)
                            
                            e_note = st.text_area("Note", value=task['note'])
                            
                            if st.form_submit_button("Save Changes"):
                                edit_task(task['id'], e_name, e_priority, e_deadline, e_note, e_category, e_start_date)
                                st.success("Updated!")
                                st.rerun()
                    
                    st.divider()

    elif view_mode == "Gantt Chart":
        st.subheader("📊 Gantt Chart")
        
        # Prepare data for Gantt
        gantt_data = []
        for task in filtered_tasks:
            if task['start_date'] and task['deadline']:
                gantt_data.append({
                    "Task": task['name'],
                    "Start": task['start_date'],
                    "Finish": task['deadline'],
                    "Priority": task['priority'],
                    "Category": task['category'],
                    "Done": "Done" if task['done'] else "Pending"
                })
        
        if gantt_data:
            df = pd.DataFrame(gantt_data)
            
            # Convert to datetime to avoid serialization issues
            df["Start"] = pd.to_datetime(df["Start"])
            df["Finish"] = pd.to_datetime(df["Finish"])
            
            # Sort by Start date
            df = df.sort_values(by="Start")
            
            fig = px.timeline(
                df, 
                x_start="Start", 
                x_end="Finish", 
                y="Task", 
                color="Priority",
                hover_data=["Category", "Done"],
                color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"}
            )

            # Workaround for Streamlit/Plotly serialization issue with timedelta
            for trace in fig.data:
                if trace.x is not None and len(trace.x) > 0:
                    # Find the first non-null value to check type
                    first_valid = next((v for v in trace.x if v is not None and not pd.isnull(v)), None)
                    
                    if first_valid and isinstance(first_valid, (pd.Timedelta, datetime.timedelta, np.timedelta64)):
                        new_x = []
                        for v in trace.x:
                            if v is None or pd.isnull(v):
                                new_x.append(None)
                            elif hasattr(v, 'total_seconds'):
                                new_x.append(v.total_seconds() * 1000)
                            elif isinstance(v, np.timedelta64):
                                # Convert numpy timedelta64 to milliseconds
                                new_x.append(v.astype('timedelta64[ms]').astype(float))
                            else:
                                new_x.append(v)
                        trace.x = new_x
            
            # Update layout for better visibility
            fig.update_yaxes(autorange="reversed") # Tasks from top to bottom
            fig.update_layout(xaxis_title="Date", yaxis_title="Task")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No tasks with both Start Date and Deadline found to display in Gantt Chart.")
            st.markdown("""
                **Tip:** To see tasks here, make sure they have both a **Start Date** and a **Deadline**.
                You can edit existing tasks to add these dates.
            """)

if __name__ == "__main__":
    main()
