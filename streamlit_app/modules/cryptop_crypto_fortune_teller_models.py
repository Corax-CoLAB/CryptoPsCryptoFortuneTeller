# cryptop_crypto_fortune_teller_models.py
import pandas as pd
import numpy as np
from prophet import Prophet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def forecast_prophet(df, periods=30):
    """
    Forecast future prices using Facebook Prophet model.
    Accepts DataFrame with date index and 'close' column.
    Returns DataFrame with 'ds', 'yhat', 'yhat_lower', 'yhat_upper'.
    Prophet is well-suited for data with strong seasonality:contentReference[oaicite:3]{index=3}.
    """
    df_prophet = df.reset_index().rename(columns={'date': 'ds', 'close': 'y'})
    model = Prophet(daily_seasonality=True)  # add seasonality
    model.fit(df_prophet)  # Prophet model (additive seasonal):contentReference[oaicite:4]{index=4}
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[['ds','yhat','yhat_lower','yhat_upper']]

def forecast_lstm(df, periods=30, n_steps=60):
    """
    Forecast future prices using a simple LSTM neural network.
    Accepts DataFrame with date index and 'close' column.
    Returns DataFrame with 'ds' and 'yhat'.
    """
    # Prepare data
    df_lstm = df.reset_index()
    df_lstm['date'] = pd.to_datetime(df_lstm['date'])
    series = df_lstm['close'].values
    # Scale data to [0,1]
    scaler = MinMaxScaler()
    series_scaled = scaler.fit_transform(series.reshape(-1,1))
    # Create sequences of length n_steps
    X, y = [], []
    for i in range(n_steps, len(series_scaled)):
        X.append(series_scaled[i-n_steps:i, 0])
        y.append(series_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    # Build LSTM model
    model = Sequential([
        LSTM(50, input_shape=(n_steps, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=16, verbose=0)
    # Forecast future values
    forecast_input = series_scaled[-n_steps:].reshape(1, n_steps, 1)
    preds = []
    for _ in range(periods):
        pred_scaled = model.predict(forecast_input)[0][0]
        preds.append(pred_scaled)
        # update input for next prediction
        forecast_input = np.append(forecast_input[:,1:,:], [[[pred_scaled]]], axis=1)
    preds = scaler.inverse_transform(np.array(preds).reshape(-1,1)).flatten()
    # Build result DataFrame
    last_date = pd.to_datetime(df_lstm['date'].iloc[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods+1)]
    forecast_df = pd.DataFrame({'ds': future_dates, 'yhat': preds})
    return forecast_df
