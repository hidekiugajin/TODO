import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import datetime
import numpy as np
def main():
    st.title("Gantt Chart Repro")

    # Mimic the data from app.py
    # task['start_date'] and task['deadline'] are strings in 'YYYY-MM-DD' format
    gantt_data = [
        {
            "Task": "Test Task 1",
            "Start": "2023-10-26",
            "Finish": "2023-10-27",
            "Priority": "High",
            "Category": "Work",
            "Done": "Pending"
        },
        {
            "Task": "Test Task 2",
            "Start": "2023-10-27",
            "Finish": "2023-10-30",
            "Priority": "Medium",
            "Category": "Personal",
            "Done": "Done"
        }
    ]

    df = pd.DataFrame(gantt_data)
    
    # Fix: Convert to datetime
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    
    # Ensure columns are datetime objects? 
    # In app.py they are passed as strings directly from SQLite.
    # px.timeline handles strings, but let's see if that's the issue.
    
    st.write("Dataframe:", df)

    try:
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
            if trace.x and len(trace.x) > 0:
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
        
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(xaxis_title="Date", yaxis_title="Task")
        
        st.plotly_chart(fig, use_container_width=True)
        st.success("Chart rendered successfully")
    except Exception as e:
        st.error(f"Error: {e}")
        import traceback
        st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
