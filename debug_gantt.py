import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

def main():
    st.title("Debug Gantt")
    gantt_data = [
        {
            "Task": "Test Task 1",
            "Start": "2023-10-26",
            "Finish": "2023-10-27",
            "Priority": "High",
            "Category": "Work",
            "Done": "Pending"
        }
    ]

    df = pd.DataFrame(gantt_data)
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])

    fig = px.timeline(
        df, 
        x_start="Start", 
        x_end="Finish", 
        y="Task", 
        color="Priority"
    )
    
    # Check data type before fix
    st.write("Data type of x (before fix):", type(fig.data[0].x))
    if fig.data[0].x is not None and len(fig.data[0].x) > 0:
        st.write("First element type:", type(fig.data[0].x[0]))

    # Apply Fix
    for trace in fig.data:
        if trace.x and len(trace.x) > 0:
            first_val = trace.x[0]
            if isinstance(first_val, (pd.Timedelta, datetime.timedelta)):
                trace.x = [v.total_seconds() * 1000 for v in trace.x]
    
    st.write("Data type of x (after fix):", type(fig.data[0].x))
    if fig.data[0].x is not None and len(fig.data[0].x) > 0:
        st.write("First element type (after fix):", type(fig.data[0].x[0]))

    st.plotly_chart(fig)
    st.success("Chart rendered successfully")

if __name__ == "__main__":
    main()
