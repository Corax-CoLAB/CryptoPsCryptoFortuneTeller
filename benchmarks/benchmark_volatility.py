import time
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# This is now the OPTIMIZED version from the codebase
from streamlit_app.modules.cryptop_crypto_circus_helper import compute_volatility as current_implementation

def old_compute_volatility(df, window=14):
    """
    Original slow implementation using pd.concat.
    """
    if 'close' not in df or df.empty:
         return pd.DataFrame()

    vol = pd.DataFrame(index=df.index)
    vol['rolling_std'] = df['close'].rolling(window).std()
    # Compute ATR if high/low available
    if 'high' in df and 'low' in df:
        high_low = df['high'] - df['low']
        high_pc = (df['high'] - df['close'].shift(1)).abs()
        low_pc = (df['low'] - df['close'].shift(1)).abs()
        tr = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
        vol['ATR'] = tr.rolling(window).mean()
    else:
        vol['ATR'] = np.nan
    return vol

def benchmark():
    # Generate synthetic data
    rows = 10000
    dates = pd.date_range(start='2020-01-01', periods=rows, freq='D')
    df = pd.DataFrame({
        'high': np.random.uniform(100, 200, rows),
        'low': np.random.uniform(50, 100, rows),
        'close': np.random.uniform(50, 200, rows)
    }, index=dates)

    print(f"Benchmarking with {rows} rows...")

    # Warmup
    current_implementation(df.copy())
    old_compute_volatility(df.copy())

    # OLD
    start = time.time()
    for _ in range(100):
        old_compute_volatility(df)
    end = time.time()
    avg_old = (end - start) / 100
    print(f"Old implementation average time: {avg_old:.6f}s")

    # NEW (Current)
    start = time.time()
    for _ in range(100):
        current_implementation(df)
    end = time.time()
    avg_new = (end - start) / 100
    print(f"New implementation average time: {avg_new:.6f}s")

    speedup = avg_old / avg_new
    print(f"Speedup: {speedup:.2f}x")

    # Verification
    res_old = old_compute_volatility(df)
    res_new = current_implementation(df)

    # Check if results are close
    try:
        pd.testing.assert_frame_equal(res_old, res_new)
        print("✅ Results match exactly!")
    except AssertionError as e:
        print("❌ Results do not match!")
        print(e)

if __name__ == "__main__":
    benchmark()
