import re

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "r") as f:
    content = f.read()

tuning_func = """
@st.cache_data(ttl=86400)
def auto_tune_prophet(df, param_grid=None):
    \"\"\"
    Perform basic grid search cross-validation for Prophet hyperparameters.
    \"\"\"
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

"""

if "def auto_tune_prophet" not in content:
    # Insert near the top
    content = content.replace("def get_prophet_config", tuning_func + "\ndef get_prophet_config")

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "w") as f:
    f.write(content)
