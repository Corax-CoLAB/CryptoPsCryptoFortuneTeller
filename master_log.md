## 2026-07-25 - [Optimize CCI Indicator using Vectorization]
**Learning:** Using `.apply(lambda x: ...)` inside a `.rolling()` window is computationally expensive, especially for indicators like Commodity Channel Index (CCI) requiring Mean Absolute Deviation (MAD), causing O(n*k) overhead where `n` is data length and `k` is the window size.
**Action:** Replaced the lambda-based MAD calculation (`tp.rolling(period).apply(lambda x: pd.Series(x).mad())`) with fully vectorized operations using `numpy.lib.stride_tricks.sliding_window_view`. This eliminates the lambda loop entirely, computes the true MAD, and yielded a ~30x speedup (~1.6s to ~0.05s for 100k rows). Always seek pure pandas/numpy vectorized composition over `.apply()` loops.

## 2026-07-26 - [Optimize DataFrame iteration with itertuples]
**Learning:** Using `.iterrows()` is known to be slow because it creates a Series for each row.
**Action:** Replaced `.iterrows()` with `.itertuples()` for the ticker implementation in `cryptop_crypto_fortune_teller_main.py` where simple row iteration is needed. Used `getattr(row, 'column_name')` to safely access values.

## 2026-07-26 - [Optimize string formatting in DataFrames]
**Learning:** Using `.apply(lambda x: f"{x:.2f}")` on pandas Series is slow due to python-level loop overhead for each element.
**Action:** Replaced `.apply(lambda x: ...)` with list comprehensions like `[f"{x:.2f}" for x in df['col']]` which are significantly faster for string formatting operations.

## 2026-07-26 - [Optimize Conditional Assignments]
**Learning:** Using `.apply(lambda x: ... if ... else ...)` is slow compared to vectorized numpy operations.
**Action:** Replaced lambda conditionals with `np.where(condition, true_val, false_val)` in both chart color assignment and DataFrame column calculations (`Alpha Potential`), yielding massive speedups.
