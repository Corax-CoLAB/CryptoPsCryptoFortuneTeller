import sys
import time
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
import streamlit as st

# Mock streamlit cache
class MockCache:
    def __init__(self):
        self.cache = {}

    def __call__(self, ttl=None, **kwargs):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Construct a key.
                # We assume simple usage: df, config, periods (pos or kw)
                key_parts = [func.__name__]

                # args[0] is df
                if len(args) > 0:
                     key_parts.append(str(args[0].shape))
                # args[1] is config
                if len(args) > 1:
                     key_parts.append(str(args[1]))
                # args[2] is periods (optional)
                if len(args) > 2:
                     key_parts.append(str(args[2]))

                if 'periods' in kwargs:
                    key_parts.append(f"periods={kwargs['periods']}")

                key = tuple(key_parts)

                if key in self.cache:
                    # print(f"Cache HIT for {key}")
                    return self.cache[key]

                # print(f"Cache MISS for {key}")
                result = func(*args, **kwargs)
                self.cache[key] = result
                return result
            return wrapper
        return decorator

# Patch st.cache_data
st.cache_data = MockCache()

# Now import target
from streamlit_app.modules import cryptop_crypto_fortune_teller_models

def generate_data(n=2000):
    dates = pd.date_range(start='2018-01-01', periods=n, freq='D')
    values = np.random.randn(n).cumsum() + 100
    df = pd.DataFrame({'date': dates, 'close': values})
    # The module expects date index or date column.
    # It does `df.reset_index()` internally if date is index.
    # Let's use date index as typical usage
    df = df.set_index('date')
    return df

def run_benchmark():
    df = generate_data()
    config = {'changepoint_prior_scale': 0.05}

    print("--- Benchmark Start ---")

    # Run 1: periods=30
    start_time = time.time()
    res1 = cryptop_crypto_fortune_teller_models._run_prophet_model(df, config, periods=30)
    t1 = time.time() - start_time
    print(f"Run 1 (periods=30): {t1:.4f}s")

    # Run 2: periods=60
    # In current impl, this changes cache key -> Cache MISS -> Re-run
    start_time = time.time()
    res2 = cryptop_crypto_fortune_teller_models._run_prophet_model(df, config, periods=60)
    t2 = time.time() - start_time
    print(f"Run 2 (periods=60): {t2:.4f}s")

    print(f"Total Time: {t1+t2:.4f}s")

if __name__ == "__main__":
    run_benchmark()
