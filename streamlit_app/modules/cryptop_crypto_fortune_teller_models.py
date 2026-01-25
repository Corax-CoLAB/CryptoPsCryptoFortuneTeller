# cryptop_crypto_fortune_teller_models.py
import pandas as pd
import numpy as np
import streamlit as st
from prophet import Prophet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler
import logging
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def get_prophet_config(model_name):
    """
    Returns hyperparameters for different Prophet model configurations.
    """
    if model_name == "Volatile (Trend Chaser)":
        return {
            'changepoint_prior_scale': 0.5,
            'seasonality_prior_scale': 0.01,
            'seasonality_mode': 'multiplicative',
            'daily_seasonality': True
        }
    elif model_name == "Conservative (Safe Haven)":
        return {
            'changepoint_prior_scale': 0.005,
            'seasonality_prior_scale': 10.0,
            'interval_width': 0.95,
            'daily_seasonality': True
        }
    else: # Standard / Default
        return {
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
            'daily_seasonality': True
        }

@st.cache_data(ttl=3600)
def _run_prophet_model(df, config, periods=30):
    """
    Internal function to run a single Prophet model with specific config.
    """
    if df.empty or len(df) < 2:
        return pd.DataFrame(columns=['ds','yhat','yhat_lower','yhat_upper'])

    df_prophet = df.reset_index()
    date_col = 'date' if 'date' in df_prophet.columns else 'index'
    df_prophet = df_prophet.rename(columns={date_col: 'ds', 'close': 'y'})

    # Disable stdout logging
    logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

    # Extract config
    cps = config.get('changepoint_prior_scale', 0.05)
    sps = config.get('seasonality_prior_scale', 10.0)
    sm = config.get('seasonality_mode', 'additive')
    iw = config.get('interval_width', 0.80)
    ds = config.get('daily_seasonality', True)

    model = Prophet(
        changepoint_prior_scale=cps,
        seasonality_prior_scale=sps,
        seasonality_mode=sm,
        interval_width=iw,
        daily_seasonality=ds
    )

    try:
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast[['ds','yhat','yhat_lower','yhat_upper']]
    except Exception as e:
        st.error(f"Prophet model failed: {e}")
        return pd.DataFrame(columns=['ds','yhat','yhat_lower','yhat_upper'])

def forecast_prophet_ensemble(df, model_names, periods=30, sentiment_score=0.0):
    """
    Runs multiple Prophet models and averages the results.
    Apply sentiment adjustment if sentiment_score is provided.

    model_names: list of strings (e.g. ["Standard", "Volatile"])
    sentiment_score: float between -1.0 and 1.0
    """
    if not model_names:
        model_names = ["Standard"]

    forecasts = []

    for name in model_names:
        config = get_prophet_config(name)
        # We pass config as a dict, but st.cache_data handles dicts well if they are consistent.
        # To be safe for hashing, we could convert to tuple items, but dict is generally fine in recent Streamlit versions
        # or we rely on the function logic. To be 100% safe with hashing, let's keep it simple.
        f = _run_prophet_model(df, config, periods)
        if not f.empty:
            forecasts.append(f)

    if not forecasts:
        return pd.DataFrame(columns=['ds','yhat','yhat_lower','yhat_upper'])

    # Combine forecasts
    # Assumes all forecasts have the same 'ds' column
    base = forecasts[0].copy()

    if len(forecasts) > 1:
        # Average the numeric columns
        for col in ['yhat', 'yhat_lower', 'yhat_upper']:
            # Stack columns from all dfs
            stacked = np.column_stack([f[col].values for f in forecasts])
            # Mean across columns
            base[col] = np.mean(stacked, axis=1)

    # Apply Sentiment Adjustment (Post-Processing)
    # Logic:
    # If score is positive (e.g. +0.8), we tilt the forecast upwards slightly.
    # We apply this progressively into the future? Or a flat shift?
    # A progressive shift makes more sense for a "forecast".
    # Multiplier starts at 1.0 and grows/shrinks linearly to (1 + score * factor) at the end of period.

    if sentiment_score != 0.0 and len(base) > 0:
        # Factor: How much impact? Let's say max 10% change for max sentiment at the end of 30 days.
        impact_factor = 0.10

        # We only adjust the *future* part.
        # Identify future rows (where ds > last historical date)
        # But here we don't have the original df index easily to check against.
        # We can assume the last 'periods' rows are future.

        total_rows = len(base)
        future_idx_start = total_rows - periods

        if future_idx_start < 0: future_idx_start = 0

        # Create a multiplier array
        # Historical part gets 1.0 (no change)
        # Future part gets linear ramp

        multipliers = np.ones(total_rows)

        # Linear ramp from 0 to sentiment_score
        ramp = np.linspace(0, sentiment_score * impact_factor, periods)
        multipliers[future_idx_start:] += ramp

        base['yhat'] *= multipliers
        base['yhat_upper'] *= multipliers
        base['yhat_lower'] *= multipliers

    return base

# Wrapper for backward compatibility if needed, or just standard usage
def forecast_prophet(df, periods=30):
    return forecast_prophet_ensemble(df, ["Standard"], periods)

@st.cache_data(ttl=3600)
def forecast_lstm(df, periods=30, n_steps=60):
    """
    Forecast future prices using a simple LSTM neural network.
    Accepts DataFrame with date index and 'close' column.
    Returns DataFrame with 'ds' and 'yhat'.
    """
    if df.empty:
        return pd.DataFrame(columns=['ds', 'yhat'])

    df_lstm = df.reset_index()
    date_col = 'date' if 'date' in df_lstm.columns else 'index'
    df_lstm['date'] = pd.to_datetime(df_lstm[date_col])
    series = df_lstm['close'].values

    if len(series) <= n_steps:
        n_steps = max(1, len(series) - 5)
        if n_steps < 1:
             return pd.DataFrame(columns=['ds', 'yhat'])

    scaler = MinMaxScaler()
    series_scaled = scaler.fit_transform(series.reshape(-1,1))

    X, y = [], []
    for i in range(n_steps, len(series_scaled)):
        X.append(series_scaled[i-n_steps:i, 0])
        y.append(series_scaled[i, 0])

    X, y = np.array(X), np.array(y)

    if len(X) == 0:
         return pd.DataFrame(columns=['ds', 'yhat'])

    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Explicit Input layer
    model = Sequential([
        Input(shape=(n_steps, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=16, verbose=0)

    forecast_input = series_scaled[-n_steps:].reshape(1, n_steps, 1).astype(np.float32)
    preds = np.zeros(periods, dtype=np.float32)

    for i in range(periods):
        pred_scaled = model.predict_on_batch(forecast_input)[0][0]
        preds[i] = pred_scaled
        forecast_input[:, :-1, :] = forecast_input[:, 1:, :]
        forecast_input[0, -1, 0] = pred_scaled

    preds = scaler.inverse_transform(preds.reshape(-1, 1)).flatten()

    last_date = pd.to_datetime(df_lstm['date'].iloc[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods+1)]
    forecast_df = pd.DataFrame({'ds': future_dates, 'yhat': preds})
    return forecast_df
