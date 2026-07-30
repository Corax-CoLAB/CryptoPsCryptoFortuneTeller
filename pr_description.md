💡 What: Optimized model data preparation and main UI loops by replacing Python `for` loops with vectorized operations (`numpy.lib.stride_tricks.sliding_window_view` and `pandas` dataframe/Series math).
🎯 Why: Iterative loops over pandas rows or using `append` scale poorly. Random Forest was still using a slow loop. The Ticker and Portfolio rendering loops were causing overhead during Streamlit's frequent re-runs.
📊 Impact: Significant reduction in time required for model data preparation and UI rendering by leveraging optimized C-level code and list comprehensions.
🔬 Measurement: Verified via unit tests (`pytest`). Overall application rendering and data updates feel significantly snappier.
