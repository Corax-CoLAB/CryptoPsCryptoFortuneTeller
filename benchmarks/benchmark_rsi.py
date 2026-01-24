import pandas as pd
import numpy as np
import timeit

def calculate_rsi(df, period=14):
    """Calculate RSI for a given DataFrame with a 'close' column."""
    if 'close' not in df:
        return pd.Series(dtype=float)

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Use Wilder's Smoothing (EMA with alpha=1/period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def iterative_strategy(rsi):
    position = 0
    pos_list = []
    # Force conversion to list to match "for r in rsi" behavior if rsi is Series
    # But "for r in rsi" on a series iterates values.
    for r in rsi:
        if r < 30:
            position = 1
        elif r > 70:
            position = 0
        pos_list.append(position)
    return pd.Series(pos_list, index=rsi.index)

def vectorized_strategy(rsi):
    signal_series = pd.Series(np.nan, index=rsi.index)
    signal_series[rsi < 30] = 1.0
    signal_series[rsi > 70] = 0.0
    signal_series = signal_series.ffill().fillna(0.0)
    return signal_series

def run_benchmark():
    # Generate large dataset
    n_rows = 100000
    print(f"Generating data with {n_rows} rows...")
    dates = pd.date_range('2020-01-01', periods=n_rows, freq='min')
    # Random walk
    close_prices = np.cumsum(np.random.randn(n_rows)) + 1000
    df = pd.DataFrame({'close': close_prices}, index=dates)

    print("Calculating RSI...")
    rsi = calculate_rsi(df)

    print("Benchmarking Iterative Strategy...")
    # Run 10 times
    t_iter = timeit.timeit(lambda: iterative_strategy(rsi), number=10)
    avg_iter = t_iter / 10
    print(f"Iterative Average Time: {avg_iter:.6f}s")

    print("Benchmarking Vectorized Strategy...")
    t_vect = timeit.timeit(lambda: vectorized_strategy(rsi), number=10)
    avg_vect = t_vect / 10
    print(f"Vectorized Average Time: {avg_vect:.6f}s")

    speedup = avg_iter / avg_vect
    print(f"Speedup: {speedup:.2f}x")

    # Verify correctness
    print("Verifying correctness...")
    s1 = iterative_strategy(rsi)
    s2 = vectorized_strategy(rsi)

    # Note: Iterative strategy starts with position=0.
    # Vectorized starts with NaN -> 0.
    # We need to align types for comparison (int vs float)
    s1 = s1.astype(float)
    s2 = s2.astype(float)

    if s1.equals(s2):
        print("Outputs match perfectly!")
    else:
        print("Outputs differ!")
        print("Iterative sample:", s1.head(20).values)
        print("Vectorized sample:", s2.head(20).values)
        diff_count = (s1 != s2).sum()
        print(f"Differences: {diff_count} out of {n_rows}")

if __name__ == "__main__":
    run_benchmark()
