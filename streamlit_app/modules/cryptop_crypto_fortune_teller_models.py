# cryptop_crypto_fortune_teller_models.py
import pandas as pd
import numpy as np
import streamlit as st
from prophet import Prophet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import logging
import os
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

import warnings
import itertools
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)

def get_best_arima(series, max_p=3, max_q=3, d=1):
    """
    Technical Improvement 2: Auto-ARIMA
    Finds best ARIMA(p,d,q) order based on AIC.
    """
    best_aic = float("inf")
    best_order = (0, d, 0)
    for p, q in itertools.product(range(max_p+1), range(max_q+1)):
        try:
            model = ARIMA(series, order=(p, d, q))
            results = model.fit()
            if results.aic < best_aic:
                best_aic = results.aic
                best_order = (p, d, q)
        except:
            continue
    return best_order

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#DoS Protection Limits
MAX_FORECAST_HORIZON = 365
MAX_HISTORY_LENGTH = 2000


@st.cache_data(ttl=86400)
def auto_tune_prophet(df, param_grid=None):
    """
    Perform basic grid search cross-validation for Prophet hyperparameters.
    """
    from prophet import Prophet
    from prophet.diagnostics import cross_validation, performance_metrics
    import itertools

    if param_grid is None:
        param_grid = {
            'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
            'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0]
        }

    # Generate all combinations of parameters
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    rmses = []  # Store the RMSEs for each params here

    if len(df) < 100:
        return {'changepoint_prior_scale': 0.05, 'seasonality_prior_scale': 10.0}

    # Prepare data
    df_cv = pd.DataFrame({'ds': df.index, 'y': df['close'].values})

    # We will just do a fast split for tuning to save time (not full CV)
    split_idx = int(len(df_cv) * 0.8)
    train_df = df_cv.iloc[:split_idx]
    test_df = df_cv.iloc[split_idx:]

    best_params = all_params[0]
    best_rmse = float('inf')

    # Find the best parameters
    for params in all_params:
        try:
            m = Prophet(**params, weekly_seasonality=False, daily_seasonality=False)
            m.fit(train_df)
            future = m.make_future_dataframe(periods=len(test_df))
            forecast = m.predict(future)

            # Calculate RMSE on test set
            y_pred = forecast['yhat'].iloc[-len(test_df):].values
            y_true = test_df['y'].values
            rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

            if rmse < best_rmse:
                best_rmse = rmse
                best_params = params
        except Exception:
            continue

    return best_params


def get_prophet_config(model_name, overrides=None):
    """
    Returns hyperparameters for different Prophet model configurations.
    """
    config = {}
    if model_name == "Volatile (Trend Chaser)":
        config = {
            'changepoint_prior_scale': 0.5,
            'seasonality_prior_scale': 0.01,
            'seasonality_mode': 'multiplicative',
            'daily_seasonality': True
        }
    elif model_name == "Conservative (Safe Haven)":
        config = {
            'changepoint_prior_scale': 0.005,
            'seasonality_prior_scale': 10.0,
            'interval_width': 0.95,
            'daily_seasonality': True
        }
    else: # Standard / Default
        config = {
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
            'daily_seasonality': True
        }

    # Apply overrides if provided
    if overrides:
        # Only override keys that are explicitly set in overrides
        config.update({k: v for k, v in overrides.items() if v is not None})

    return config

@st.cache_data(ttl=3600)
def _run_prophet_model_fixed(df, config):
    """
    Internal function to run a single Prophet model with fixed MAX_FORECAST_HORIZON.
    This avoids re-running the model when only the forecast horizon changes.
    """
    periods = MAX_FORECAST_HORIZON

    if len(df) > MAX_HISTORY_LENGTH:
        df = df.iloc[-MAX_HISTORY_LENGTH:]

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


def _run_prophet_model(df, config, periods=30):
    """
    Wrapper around _run_prophet_model_fixed to slice the result.
    """
    #Enforce Input Limits
    if periods > MAX_FORECAST_HORIZON:
        logging.warning(f"Prophet: periods {periods} clamped to {MAX_FORECAST_HORIZON}")
        periods = MAX_FORECAST_HORIZON

    full_forecast = _run_prophet_model_fixed(df, config)

    if full_forecast.empty:
        return full_forecast

    # Slice the result
    # The full_forecast has H + MAX_FORECAST_HORIZON rows.
    # We want H + periods rows.
    cutoff = MAX_FORECAST_HORIZON - periods
    if cutoff > 0:
        return full_forecast.iloc[:-cutoff]
    return full_forecast

@st.cache_data(ttl=3600)
def forecast_arima(df, periods=30):
    """
    Forecast using ARIMA model (Auto-Regressive Integrated Moving Average).
    """
    #Enforce Input Limits
    if periods > MAX_FORECAST_HORIZON:
        logging.warning(f"ARIMA: periods {periods} clamped to {MAX_FORECAST_HORIZON}")
        periods = MAX_FORECAST_HORIZON

    if len(df) > MAX_HISTORY_LENGTH:
        df = df.iloc[-MAX_HISTORY_LENGTH:]

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

        # Technical Improvement 2: Dynamic ARIMA order selection (Auto-ARIMA)
        best_order = get_best_arima(series, max_p=3, max_q=3, d=1)
        model = ARIMA(series, order=best_order)
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
    #Enforce Input Limits
    if periods > MAX_FORECAST_HORIZON:
        logging.warning(f"SARIMA: periods {periods} clamped to {MAX_FORECAST_HORIZON}")
        periods = MAX_FORECAST_HORIZON

    if len(df) > MAX_HISTORY_LENGTH:
        df = df.iloc[-MAX_HISTORY_LENGTH:]

    if df.empty:
        return pd.DataFrame(columns=['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

    try:
        # SARIMA (1, 1, 1) x (1, 1, 0, 12) - assuming some seasonality but hard to guess generic
        # A safer generic bet for financial time series with potential seasonality:
        # (1, 1, 1) x (0, 1, 1, 7) for weekly seasonality

        series = df['close']

        # Technical Improvement 2: Dynamic SARIMA order selection based on best ARIMA base
        best_order = get_best_arima(series, max_p=2, max_q=2, d=1) # Reduced grid for speed
        model = SARIMAX(series, order=best_order, seasonal_order=(0, 1, 1, 7))
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
    #Enforce Input Limits
    if periods > MAX_FORECAST_HORIZON:
        logging.warning(f"LSTM: periods {periods} clamped to {MAX_FORECAST_HORIZON}")
        periods = MAX_FORECAST_HORIZON

    if len(df) > MAX_HISTORY_LENGTH:
        df = df.iloc[-MAX_HISTORY_LENGTH:]

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

    # Optimization: Replaced Python loop with NumPy sliding_window_view for data prep
    # Expected Impact: Significant speedup in LSTM data preparation for large datasets
    from numpy.lib.stride_tricks import sliding_window_view
    series_1d = series_scaled[:, 0]

    if len(series_1d) >= n_steps + 1:
        windows = sliding_window_view(series_1d, window_shape=n_steps + 1)
        X = windows[:, :-1]
        y = windows[:, -1]
    else:
        X, y = np.array([]), np.array([])

    if len(X) == 0:
         return pd.DataFrame(columns=['ds', 'yhat'])

    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Technical Improvement 5: LSTM Architecture Upgrade
    model = Sequential([
        Input(shape=(n_steps, 1)),
        LSTM(100, return_sequences=True), # Increased complexity
        Dropout(0.2), # Prevent overfitting
        LSTM(50),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    # Early stopping
    early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)

    model.fit(X, y, epochs=20, batch_size=64, verbose=0, callbacks=[early_stop])

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

@st.cache_data(ttl=3600)
def forecast_random_forest(df, periods=30, n_lags=14):
    """
    Forecast using Random Forest Regressor.
    """
    #Enforce Input Limits
    if periods > MAX_FORECAST_HORIZON:
        logging.warning(f"RF: periods {periods} clamped to {MAX_FORECAST_HORIZON}")
        periods = MAX_FORECAST_HORIZON

    if len(df) > MAX_HISTORY_LENGTH:
        df = df.iloc[-MAX_HISTORY_LENGTH:]

    if df.empty:
         return pd.DataFrame(columns=['ds', 'yhat'])

    df_rf = df.reset_index()
    date_col = 'date' if 'date' in df_rf.columns else 'index'
    df_rf['date'] = pd.to_datetime(df_rf[date_col])

    # Feature Engineering: Lagged features
    series = df_rf['close']
    X, y = [], []

    # We need to construct supervised learning dataset
    # We will use 'n_lags' previous values to predict next one

    # Ensure we have enough data
    if len(series) <= n_lags:
        return pd.DataFrame(columns=['ds', 'yhat'])

    values = series.values
    from numpy.lib.stride_tricks import sliding_window_view
    if len(values) >= n_lags + 1:
        windows = sliding_window_view(values, window_shape=n_lags + 1)
        X = windows[:, :-1]
        y = windows[:, -1]
    else:
        X, y = np.array([]), np.array([])
        return pd.DataFrame(columns=['ds', 'yhat'])

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Recursive Forecasting
    preds = np.zeros(periods)
    current_lag = values[-n_lags:]

    for i in range(periods):
        next_val = model.predict(current_lag.reshape(1, -1))[0]
        preds[i] = next_val
        # Shift and append
        current_lag = np.append(current_lag[1:], next_val)

    last_date = pd.to_datetime(df_rf['date'].iloc[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods+1)]

    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': preds,
        'yhat_lower': preds, # No CI for standard RF
        'yhat_upper': preds
    })
    return forecast_df

def forecast_general_ensemble(df, model_names, periods=30, sentiment_score=0.0, model_params=None):
    """
    Grand Ensemble that can combine Prophet, LSTM, ARIMA, SARIMA, Random Forest.
    Accepts model_params dict to override default configurations.
    """
    if not model_names:
        model_names = ["Prophet (Standard)"]

    forecasts = []
    # Dispatcher
    for name in model_names:
        f = pd.DataFrame()
        if "Prophet" in name:
            p_name = name.replace("Prophet (", "").replace(")", "")
            if p_name == "Prophet": p_name = "Standard"
            config = get_prophet_config(p_name, overrides=model_params)
            f = _run_prophet_model(df, config, periods)
        elif name == "LSTM":
            f = forecast_lstm(df, periods)
        elif name == "ARIMA":
            f = forecast_arima(df, periods)
        elif name == "SARIMA":
            f = forecast_sarima(df, periods)
        elif name == "Random Forest":
            f = forecast_random_forest(df, periods)

        if not f.empty:
            if 'yhat_lower' not in f.columns: f['yhat_lower'] = f['yhat']
            if 'yhat_upper' not in f.columns: f['yhat_upper'] = f['yhat']
            forecasts.append(f)

    if not forecasts:
        return pd.DataFrame(columns=['ds','yhat','yhat_lower','yhat_upper'])

    # Standardize to Future Only (last 'periods' rows)
    # This ensures we can average Prophet (History+Future) with ARIMA/LSTM (Future Only)
    processed_forecasts = [
        f.iloc[-periods:].reset_index(drop=True) if len(f) > periods else f.reset_index(drop=True)
        for f in forecasts
    ]

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

@st.cache_data(ttl=3600)
def forecast_monte_carlo(df, periods=30, num_simulations=1000):
    """
    Forecast future prices using Monte Carlo simulation based on Geometric Brownian Motion (GBM).
    """
    if df.empty or 'close' not in df.columns:
        return pd.DataFrame()

    returns = df['close'].pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()

    last_price = df['close'].iloc[-1]

    simulations = np.zeros((periods, num_simulations))
    simulations[0] = last_price

    # Generate random shocks
    shocks = np.random.normal(0, 1, (periods - 1, num_simulations))

    for t in range(1, periods):
        simulations[t] = simulations[t-1] * np.exp((mu - (sigma**2) / 2) + sigma * shocks[t-1])

    # Calculate percentiles (Median, 5th, 95th)
    mean_sim = np.median(simulations, axis=1)
    lower_sim = np.percentile(simulations, 5, axis=1)
    upper_sim = np.percentile(simulations, 95, axis=1)

    # Create DataFrame
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)

    res_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': mean_sim,
        'yhat_lower': lower_sim,
        'yhat_upper': upper_sim
    })

    return res_df
