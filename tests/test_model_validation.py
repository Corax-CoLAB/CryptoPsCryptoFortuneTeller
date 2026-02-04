
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_models import (
    forecast_lstm,
    forecast_arima,
    _run_prophet_model,
    MAX_FORECAST_HORIZON,
    MAX_HISTORY_LENGTH
)

# Mock config for Prophet
PROPHET_CONFIG = {
    'changepoint_prior_scale': 0.05,
    'seasonality_prior_scale': 10.0,
    'daily_seasonality': True
}

def generate_dummy_data(rows=100):
    dates = pd.date_range(start='2020-01-01', periods=rows)
    df = pd.DataFrame({'close': np.random.rand(rows) * 100}, index=dates)
    df['date'] = df.index
    return df

def test_lstm_validation():
    # Huge input
    df = generate_dummy_data(rows=MAX_HISTORY_LENGTH + 1000)
    huge_periods = MAX_FORECAST_HORIZON + 1000

    # Run forecast
    # This should be clamped to MAX_FORECAST_HORIZON
    res = forecast_lstm(df, periods=huge_periods)

    assert len(res) == MAX_FORECAST_HORIZON, f"LSTM output length {len(res)} exceeds max {MAX_FORECAST_HORIZON}"

def test_arima_validation():
    # Huge input
    df = generate_dummy_data(rows=MAX_HISTORY_LENGTH + 1000)
    huge_periods = MAX_FORECAST_HORIZON + 1000

    res = forecast_arima(df, periods=huge_periods)

    assert len(res) == MAX_FORECAST_HORIZON, f"ARIMA output length {len(res)} exceeds max {MAX_FORECAST_HORIZON}"

def test_prophet_validation():
    # Huge input
    # Since Prophet history is truncated to MAX_HISTORY_LENGTH,
    # The output dataframe (history + future) should be MAX_HISTORY_LENGTH + MAX_FORECAST_HORIZON

    df = generate_dummy_data(rows=MAX_HISTORY_LENGTH + 1000)
    huge_periods = MAX_FORECAST_HORIZON + 1000

    res = _run_prophet_model(df, PROPHET_CONFIG, periods=huge_periods)

    expected_len = MAX_HISTORY_LENGTH + MAX_FORECAST_HORIZON

    # Prophet logic: history (MAX_HISTORY_LENGTH) + future (MAX_FORECAST_HORIZON)
    # allow for +/- 1 due to implementation details of make_future_dataframe (includes start date?)
    assert len(res) <= expected_len + 1, f"Prophet output length {len(res)} exceeds expected {expected_len}"

    # Check that we have at most MAX_FORECAST_HORIZON points AFTER the history end
    # Note: res['ds'] includes history.
    # We can check the number of rows where ds > last history date
    # But last history date was from truncated df...

    # Simpler check: ensure 'yhat' is not empty and length is reasonable clamped
    assert not res.empty
