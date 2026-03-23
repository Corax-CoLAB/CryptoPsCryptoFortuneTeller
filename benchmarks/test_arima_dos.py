
import sys
import os
import time
import pandas as pd
import numpy as np

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_circus_models import forecast_arima

def test_arima_dos():
    print("Generating dummy data...")
    # Generate 5000 days of data (long history makes ARIMA slow)
    dates = pd.date_range(start='2010-01-01', periods=5000)
    df = pd.DataFrame({'close': np.random.rand(5000) * 100 + np.linspace(0, 100, 5000)}, index=dates)

    print(f"Running ARIMA forecast with 5000 history points...")
    start_time = time.time()

    forecast_arima(df, periods=30)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    test_arima_dos()
