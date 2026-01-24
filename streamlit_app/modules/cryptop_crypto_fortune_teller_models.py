# cryptop_crypto_fortune_teller_models.py
import pandas as pd
import numpy as np
import streamlit as st
from prophet import Prophet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler
import logging

# Suppress TensorFlow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

@st.cache_data(ttl=3600)
def forecast_prophet(df, periods=30):
    """
    Forecast future prices using Facebook Prophet model.
    Accepts DataFrame with date index and 'close' column.
    Returns DataFrame with 'ds', 'yhat', 'yhat_lower', 'yhat_upper'.
    Prophet is well-suited for data with strong seasonality.
    """
    if df.empty or len(df) < 2:
        # Return empty DataFrame with expected columns if not enough data
        return pd.DataFrame(columns=['ds','yhat','yhat_lower','yhat_upper'])

    df_prophet = df.reset_index()
    # Handle index name variation (if index was unnamed, reset_index created 'index')
    date_col = 'date' if 'date' in df_prophet.columns else 'index'
    df_prophet = df_prophet.rename(columns={date_col: 'ds', 'close': 'y'})

    # Disable stdout logging from Prophet
    logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

    model = Prophet(daily_seasonality=True)  # add seasonality
    model.fit(df_prophet)  # Prophet model (additive seasonal)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[['ds','yhat','yhat_lower','yhat_upper']]

@st.cache_data(ttl=3600)
def forecast_lstm(df, periods=30, n_steps=60):
    """
    Forecast future prices using a simple LSTM neural network.
    Accepts DataFrame with date index and 'close' column.
    Returns DataFrame with 'ds' and 'yhat'.
    """
    if df.empty:
        return pd.DataFrame(columns=['ds', 'yhat'])

    # Prepare data
    df_lstm = df.reset_index()
    # Handle index name variation
    date_col = 'date' if 'date' in df_lstm.columns else 'index'
    df_lstm['date'] = pd.to_datetime(df_lstm[date_col])
    series = df_lstm['close'].values

    # Adjust n_steps if data is too short
    # We need at least n_steps + 1 data points to train (X -> y)
    if len(series) <= n_steps:
        n_steps = max(1, len(series) - 5)
        if n_steps < 1:
            # Not enough data to train
             return pd.DataFrame(columns=['ds', 'yhat'])

    # Scale data to [0,1]
    scaler = MinMaxScaler()
    series_scaled = scaler.fit_transform(series.reshape(-1,1))

    # Create sequences of length n_steps
    X, y = [], []
    for i in range(n_steps, len(series_scaled)):
        X.append(series_scaled[i-n_steps:i, 0])
        y.append(series_scaled[i, 0])

    X, y = np.array(X), np.array(y)

    if len(X) == 0:
         return pd.DataFrame(columns=['ds', 'yhat'])

    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Build LSTM model
    model = Sequential([
        Input(shape=(n_steps, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=16, verbose=0)

    # Forecast future values
    forecast_input = series_scaled[-n_steps:].reshape(1, n_steps, 1).astype(np.float32)
    preds = np.zeros(periods, dtype=np.float32)

    for i in range(periods):
        # Predict one step
        pred_scaled = model.predict_on_batch(forecast_input)[0][0]
        preds[i] = pred_scaled
        # Update input for next prediction: shift left and append new prediction
        forecast_input[:, :-1, :] = forecast_input[:, 1:, :]
        forecast_input[0, -1, 0] = pred_scaled

    preds = scaler.inverse_transform(preds.reshape(-1, 1)).flatten()

    # Build result DataFrame
    last_date = pd.to_datetime(df_lstm['date'].iloc[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods+1)]
    forecast_df = pd.DataFrame({'ds': future_dates, 'yhat': preds})
    return forecast_df
