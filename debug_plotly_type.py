import pandas as pd
import plotly.express as px
import datetime
import numpy as np

def inspect_figure():
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

    print("Inspecting Figure Data:")
    for i, trace in enumerate(fig.data):
        print(f"Trace {i}:")
        if hasattr(trace, 'x'):
            print(f"  x type: {type(trace.x)}")
            if len(trace.x) > 0:
                first_val = trace.x[0]
                print(f"  x[0] type: {type(first_val)}")
                print(f"  x[0] value: {first_val}")
                print(f"  Is instance of pd.Timedelta: {isinstance(first_val, pd.Timedelta)}")
                print(f"  Is instance of datetime.timedelta: {isinstance(first_val, datetime.timedelta)}")
                print(f"  Is instance of np.timedelta64: {isinstance(first_val, np.timedelta64)}")

if __name__ == "__main__":
    inspect_figure()
