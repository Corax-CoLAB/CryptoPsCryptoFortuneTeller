import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_models import (
    forecast_prophet,
    forecast_lstm
)

def test_forecast_prophet():
    # Create dummy data
    dates = pd.date_range(start='2023-01-01', periods=20)
    data = {'close': np.arange(20)}
    df = pd.DataFrame(data, index=dates)

    # Check robustness on small data
    # Prophet requires at least 2 rows
    forecast = forecast_prophet(df, periods=5)

    assert 'ds' in forecast.columns
    assert 'yhat' in forecast.columns
    # Check if forecast goes beyond last date
    assert forecast['ds'].max() > dates.max()

def test_forecast_lstm_short_data():
    # Create very short dummy data (10 points)
    dates = pd.date_range(start='2023-01-01', periods=10)
    data = {'close': np.arange(10).astype(float)}
    df = pd.DataFrame(data, index=dates)

    # Should handle it without crashing thanks to my fix (n_steps will be adjusted)
    forecast = forecast_lstm(df, periods=2, n_steps=60)

    assert not forecast.empty
    assert len(forecast) == 2
    assert 'yhat' in forecast.columns
