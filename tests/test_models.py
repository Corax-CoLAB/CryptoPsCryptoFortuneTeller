import pytest
import pandas as pd
import numpy as np
import sys
import os
import warnings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_circus_models import (
    forecast_prophet,
    forecast_lstm,
    _run_prophet_model,
    MAX_FORECAST_HORIZON
)
from unittest.mock import patch

def test_prophet_slicing_logic():
    # We want to verify that _run_prophet_model returns the correct number of rows
    # and that it correctly slices the cached result.

    history_len = 10
    total_len = history_len + MAX_FORECAST_HORIZON

    df_dummy = pd.DataFrame({
        'ds': pd.date_range(start='2020-01-01', periods=total_len),
        'yhat': np.arange(total_len),
        'yhat_lower': np.arange(total_len),
        'yhat_upper': np.arange(total_len)
    })

    # We mock the FIXED function, not the wrapper
    with patch('modules.cryptop_crypto_circus_models._run_prophet_model_fixed') as mock_fixed:
        mock_fixed.return_value = df_dummy

        # Case 1: periods = 30
        res = _run_prophet_model(pd.DataFrame(), {}, periods=30)
        assert len(res) == history_len + 30
        assert res.iloc[-1]['yhat'] == history_len + 30 - 1

        # Case 2: periods = MAX_FORECAST_HORIZON (365)
        res_full = _run_prophet_model(pd.DataFrame(), {}, periods=MAX_FORECAST_HORIZON)
        assert len(res_full) == total_len

        # Case 3: periods = 1
        res_1 = _run_prophet_model(pd.DataFrame(), {}, periods=1)
        assert len(res_1) == history_len + 1

        # Case 4: periods > MAX (clamped)
        res_clamp = _run_prophet_model(pd.DataFrame(), {}, periods=MAX_FORECAST_HORIZON + 10)
        assert len(res_clamp) == total_len

def test_forecast_prophet():
    # Create dummy data
    dates = pd.date_range(start='2023-01-01', periods=20)
    data = {'close': np.arange(20)}
    df = pd.DataFrame(data, index=dates)

    # Check robustness on small data
    # Prophet requires at least 2 rows
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
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
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        forecast = forecast_lstm(df, periods=2, n_steps=60)

    assert not forecast.empty
    assert len(forecast) == 2
    assert 'yhat' in forecast.columns

def test_monte_carlo():
    from modules.cryptop_crypto_circus_models import forecast_monte_carlo
    # Create synthetic daily data
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    prices = np.linspace(100, 150, 100) + np.random.normal(0, 5, 100)
    df = pd.DataFrame({'close': prices}, index=dates)

    # Test typical forecast
    res_df = forecast_monte_carlo(df, periods=30)
    assert not res_df.empty, "Monte Carlo forecast should return a dataframe"
    assert len(res_df) == 30, "Forecast length should match periods"
    assert 'yhat' in res_df.columns, "Missing 'yhat' column"
    assert 'yhat_lower' in res_df.columns, "Missing 'yhat_lower' column"
    assert 'yhat_upper' in res_df.columns, "Missing 'yhat_upper' column"

    # Check that yhat_lower <= yhat <= yhat_upper
    assert (res_df['yhat_lower'] <= res_df['yhat']).all(), "yhat_lower must be <= yhat"
    assert (res_df['yhat'] <= res_df['yhat_upper']).all(), "yhat must be <= yhat_upper"
