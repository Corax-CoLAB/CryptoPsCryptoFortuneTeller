
import sys
import os
import time
import pandas as pd
import numpy as np
import warnings

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_circus_models import forecast_lstm

def test_lstm_history_dos():
    print("Generating dummy data...")
    # Generate 5000 days of data
    dates = pd.date_range(start='2010-01-01', periods=5000)
    df = pd.DataFrame({'close': np.random.rand(5000) * 100}, index=dates)
    df['date'] = df.index

    print(f"Running LSTM forecast with 5000 history points (30 periods)...")
    start_time = time.time()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        forecast_lstm(df, periods=30)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    test_lstm_history_dos()
