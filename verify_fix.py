import numpy as np
import pandas as pd

# Mocking the structure of a Plotly trace
class MockTrace:
    def __init__(self, x):
        self.x = x

def test_fix():
    print("Testing fix for ambiguous truth value error...")
    
    # Case 1: trace.x is a numpy array (this caused the error)
    x_array = np.array([1, 2, 3])
    trace_array = MockTrace(x_array)
    
    try:
        # The fixed logic
        if trace_array.x is not None and len(trace_array.x) > 0:
            print("PASS: Numpy array handled correctly.")
        else:
            print("FAIL: Numpy array not detected as having data.")
    except ValueError as e:
        print(f"FAIL: ValueError raised for numpy array: {e}")
    except Exception as e:
        print(f"FAIL: Unexpected error for numpy array: {e}")

    # Case 2: trace.x is None
    trace_none = MockTrace(None)
    try:
        if trace_none.x is not None and len(trace_none.x) > 0:
            print("FAIL: None treated as having data.")
        else:
            print("PASS: None handled correctly.")
    except Exception as e:
        print(f"FAIL: Error for None: {e}")

    # Case 3: trace.x is empty list
    trace_empty = MockTrace([])
    try:
        if trace_empty.x is not None and len(trace_empty.x) > 0:
            print("FAIL: Empty list treated as having data.")
        else:
            print("PASS: Empty list handled correctly.")
    except Exception as e:
        print(f"FAIL: Error for empty list: {e}")

if __name__ == "__main__":
    test_fix()
