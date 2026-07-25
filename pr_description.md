💡 What: Replaced Python `for` loops with vectorized operations (`numpy.lib.stride_tricks.sliding_window_view`) in data preparation for LSTM and Random Forest models.
🎯 Why: Python `for` loops scale poorly with large datasets. The original code iterated through the entire dataset to build training sequences manually, causing O(N) Python-level operations per row.
📊 Impact: Significant reduction in time required for model data preparation for large arrays by leveraging highly optimized C-level code via NumPy vectorization. Eliminates iterative loops.
🔬 Measurement: Verified functionality using unit tests (`pytest tests/test_models.py` and `pytest tests/test_new_models.py`) and benchmarked the speedup on long arrays.
