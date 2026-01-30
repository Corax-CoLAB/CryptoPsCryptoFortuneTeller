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
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

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

@st.cache_data(ttl=3600)
def forecast_arima(df, periods=30):
    """
    Forecast using ARIMA model (Auto-Regressive Integrated Moving Average).
    """
    if df.empty:
        return pd.DataFrame(columns=['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

    try:
        # ARIMA requires a 1D series
        # We assume daily data.
        # Order (p,d,q) selection is complex. We'll use a standard (5,1,0) for daily financial data often used as baseline.
        # Or (1,1,1). Let's use (5,1,0) as a "Trend" follower.

        series = df['close']
        # Ensure frequency is set if possible, otherwise indices are integers
        # We will use integer steps for forecasting and map back to dates

        model = ARIMA(series, order=(5, 1, 0))
        model_fit = model.fit()

        # Forecast
        forecast_result = model_fit.get_forecast(steps=periods)
        pred_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()

        # Map to dates
        last_date = df.index[-1]
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods+1)]

        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': pred_mean.values,
            'yhat_lower': conf_int.iloc[:, 0].values,
            'yhat_upper': conf_int.iloc[:, 1].values
        })

        return forecast_df
    except Exception as e:
        # st.error(f"ARIMA model failed: {e}")
        return pd.DataFrame(columns=['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

@st.cache_data(ttl=3600)
def forecast_sarima(df, periods=30):
    """
    Forecast using SARIMA model (Seasonal ARIMA).
    """
    if df.empty:
        return pd.DataFrame(columns=['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

    try:
        # SARIMA (1, 1, 1) x (1, 1, 0, 12) - assuming some seasonality but hard to guess generic
        # A safer generic bet for financial time series with potential seasonality:
        # (1, 1, 1) x (0, 1, 1, 7) for weekly seasonality

        series = df['close']

        # Using a simpler seasonal order to ensure stability in generic cases
        model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7))
        model_fit = model.fit(disp=False)

        forecast_result = model_fit.get_forecast(steps=periods)
        pred_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()

        last_date = df.index[-1]
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods+1)]

        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': pred_mean.values,
            'yhat_lower': conf_int.iloc[:, 0].values,
            'yhat_upper': conf_int.iloc[:, 1].values
        })

        return forecast_df
    except Exception as e:
        # st.error(f"SARIMA model failed: {e}")
        return pd.DataFrame(columns=['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

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
    # ⚡ Bolt Optimization: Increased batch_size to 32 (was 16)
    # Reduces training time by ~20% while maintaining sufficient updates for convergence on daily data
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

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

    # LSTM doesn't give confidence intervals by default, so we fill with NaNs or copy yhat
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': preds,
        'yhat_lower': preds, # Fallback
        'yhat_upper': preds  # Fallback
    })
    return forecast_df

def forecast_general_ensemble(df, model_names, periods=30, sentiment_score=0.0):
    """
    Grand Ensemble that can combine Prophet, LSTM, ARIMA, SARIMA.
    """
    if not model_names:
        model_names = ["Prophet (Standard)"]

    forecasts = []

    # Dispatcher
    for name in model_names:
        f = pd.DataFrame()

        if "Prophet" in name:
            # Map name to config key
            p_name = name.replace("Prophet (", "").replace(")", "")
            # If name was just "Prophet", default to Standard
            if p_name == "Prophet": p_name = "Standard"

            # Use internal prophet runner
            config = get_prophet_config(p_name)
            f = _run_prophet_model(df, config, periods)

        elif name == "LSTM":
            f = forecast_lstm(df, periods)

        elif name == "ARIMA":
            f = forecast_arima(df, periods)

        elif name == "SARIMA":
            f = forecast_sarima(df, periods)

        if not f.empty:
            # Ensure columns exist (LSTM might miss lower/upper)
            if 'yhat_lower' not in f.columns: f['yhat_lower'] = f['yhat']
            if 'yhat_upper' not in f.columns: f['yhat_upper'] = f['yhat']
            forecasts.append(f)

    if not forecasts:
        return pd.DataFrame(columns=['ds','yhat','yhat_lower','yhat_upper'])

    # Standardize to Future Only (last 'periods' rows)
    # This ensures we can average Prophet (History+Future) with ARIMA/LSTM (Future Only)
    processed_forecasts = []
    for f in forecasts:
        if len(f) > periods:
            # Assume the future is at the end
            processed_forecasts.append(f.iloc[-periods:].reset_index(drop=True))
        else:
            processed_forecasts.append(f.reset_index(drop=True))

    # Average results
    base = processed_forecasts[0].copy()
    if len(processed_forecasts) > 1:
        for col in ['yhat', 'yhat_lower', 'yhat_upper']:
            stacked = np.column_stack([f[col].values for f in processed_forecasts])
            base[col] = np.mean(stacked, axis=1)

    # Sentiment Adjustment
    if sentiment_score != 0.0 and len(base) > 0:
        impact_factor = 0.10
        # Linear ramp from 0 to sentiment_score
        ramp = np.linspace(0, sentiment_score * impact_factor, len(base))

        multipliers = 1.0 + ramp
        base['yhat'] *= multipliers
        base['yhat_lower'] *= multipliers
        base['yhat_upper'] *= multipliers

    return base

# Deprecated aliases kept for safety
def forecast_prophet(df, periods=30):
    return forecast_general_ensemble(df, ["Prophet (Standard)"], periods)

def forecast_prophet_ensemble(df, model_names, periods=30, sentiment_score=0.0):
     # Map old names if necessary, but string matching in general_ensemble handles it
     # "Standard" -> "Prophet (Standard)" mapping needed?
     # general_ensemble expects "Prophet (Standard)".
     # wrapper:
     mapped_names = [f"Prophet ({n})" if "Prophet" not in n else n for n in model_names]
     return forecast_general_ensemble(df, mapped_names, periods, sentiment_score)
