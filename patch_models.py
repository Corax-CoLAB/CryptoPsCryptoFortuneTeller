import re

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "r") as f:
    content = f.read()

monte_carlo_func = """
@st.cache_data(ttl=3600)
def forecast_monte_carlo(df, periods=30, num_simulations=1000):
    \"\"\"
    Forecast future prices using Monte Carlo simulation based on Geometric Brownian Motion (GBM).
    \"\"\"
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

    # Calculate percentiles (Mean, 5th, 95th)
    mean_sim = np.mean(simulations, axis=1)
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

"""

ensemble_search = """        elif name == "Random Forest":
            f = forecast_random_forest(df, periods=periods)"""
ensemble_replace = """        elif name == "Random Forest":
            f = forecast_random_forest(df, periods=periods)
        elif name == "Monte Carlo (GBM)":
            f = forecast_monte_carlo(df, periods=periods)"""

content = content.replace(ensemble_search, ensemble_replace)
content += monte_carlo_func

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "w") as f:
    f.write(content)
