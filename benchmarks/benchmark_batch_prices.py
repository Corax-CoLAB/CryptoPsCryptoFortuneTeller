
import sys
import os
import time
import pandas as pd
import numpy as np
from unittest.mock import patch

# Add parent directory to path to allow importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit_app.modules.cryptop_crypto_circus_helper as helper
from streamlit_app.modules.cryptop_crypto_circus_helper import get_batch_historical_prices

# Define a mock for get_historical_prices that sleeps
def mock_get_historical_prices_slow(coin_id, vs_currency='usd', days=365):
    time.sleep(0.5) # Simulate 500ms network latency
    # Return a dummy dataframe
    dates = pd.date_range('2023-01-01', periods=10)
    df = pd.DataFrame({'close': np.random.rand(10) * 100}, index=dates)
    return df

def sequential_batch_prices(coin_ids, days=90):
    """
    Sequential implementation for comparison.
    """
    dfs = []
    for cid in coin_ids:
        try:
            # Call the slow function directly
            df = mock_get_historical_prices_slow(cid, days=days)
            if not df.empty:
                df = df.rename(columns={'close': cid})
                dfs.append(df)
        except Exception:
            pass

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, axis=1, join='outer')

def run_benchmark():
    coin_ids = ['bitcoin', 'ethereum', 'dogecoin', 'cardano', 'solana']
    print(f"Benchmarking with {len(coin_ids)} coins...")

    # 1. Benchmark Sequential
    print("\n--- Sequential Execution ---")
    start_time = time.time()
    res_seq = sequential_batch_prices(coin_ids)
    end_time = time.time()
    seq_duration = end_time - start_time
    print(f"Time taken: {seq_duration:.4f} seconds")

    # 2. Benchmark Concurrent (Existing Implementation)
    # We need to patch get_historical_prices inside the helper module
    print("\n--- Concurrent Execution (ThreadPoolExecutor) ---")

    # Patch the function used inside get_batch_historical_prices
    with patch('streamlit_app.modules.cryptop_crypto_circus_helper.get_historical_prices', side_effect=mock_get_historical_prices_slow):
        start_time = time.time()
        res_conc = get_batch_historical_prices(coin_ids)
        end_time = time.time()
        conc_duration = end_time - start_time
        print(f"Time taken: {conc_duration:.4f} seconds")

    # Calculate Speedup
    if conc_duration > 0:
        speedup = seq_duration / conc_duration
        print(f"\nSpeedup: {speedup:.2f}x")
    else:
        print("\nConcurrent duration was 0??")

if __name__ == "__main__":
    run_benchmark()
