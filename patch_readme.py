import re

with open("README.md", "r") as f:
    content = f.read()

features_search = """### 🧠 AI-Powered Forecasting
- **Prophet Model:** Utilizes Facebook's Prophet model for accurate time-series forecasting, capturing seasonality and trends with confidence intervals.
- **LSTM Networks:** Deploys Long Short-Term Memory (Recurrent Neural Network) models to detect complex patterns in price sequences.
- **Ensemble Projections:** 30-day ensemble forecast to estimate the future value of specific assets in your portfolio.
- **Random Forest & ARIMA:** Advanced statistical and ensemble methods for comprehensive price prediction.
- **Customizable Horizon:** Forecast up to 365 days into the future (capped for performance)."""

features_replace = features_search + """
- **Monte Carlo Simulations:** Geometric Brownian Motion model for probabilistic price paths.
- **Hyperparameter Auto-Tuning:** Automated grid-search CV for finding optimal Prophet parameters."""

content = content.replace(features_search, features_replace)

analysis_search = """### 💼 Portfolio & Market Tools
- **Portfolio Tracker:** Monitor your holdings, track PnL, view allocation pie charts, and project future wealth.
- **Market Heatmap:** Visualize the top 50 coins by market cap using an interactive Treemap.
- **Smart Calculators:** DCA, ROI, "Moon Math", and Risk/Reward planning.
- **Social Intel:** Developer activity (GitHub) and community sentiment (Reddit/Twitter)."""

analysis_replace = """### 💼 Portfolio & Market Tools
- **Portfolio Tracker:** Monitor your holdings, track PnL, view allocation pie charts, and project future wealth.
- **Advanced Risk Metrics:** Calculate Sharpe Ratio, Sortino Ratio, and Max Drawdown for your portfolio.
- **Market Heatmap:** Visualize the top 50 coins by market cap using an interactive Treemap.
- **Smart Calculators:** DCA, ROI, "Moon Math", Risk/Reward planning, and Black-Scholes Options Pricing.
- **Order Book Depth:** Fetch real-time L2 order books via CCXT and visualize bid-ask imbalances.
- **Social Intel:** Developer activity (GitHub) and community sentiment (Reddit/Twitter)."""

content = content.replace(analysis_search, analysis_replace)

about_search = """    ### 🌟 New Features & Enhancements
    1.  **Grand Ensemble Forecasting:** Combine Prophet (3 variants), LSTM, ARIMA, SARIMA, and Random Forest models.
    2.  **Advanced Indicators:** Added ADX/DMI and CCI for trend and momentum analysis.
    3.  **Market Intelligence:** View Top Gainers and Losers instantly.
    4.  **Impermanent Loss Calculator:** Estimate risks for liquidity provision.
    5.  **Portfolio Analytics:** New Diversity Score to track your asset distribution.
    6.  **Enhanced Backtesting:** New strategies including Bollinger Band Squeeze and MACD Crossover.
    7.  **Psychedelic Professional UI:** A completely revamped, immersive visual experience."""

about_replace = """    ### 🌟 New Features & Enhancements (v3.5)
    1.  **Monte Carlo Forecasting:** Geometric Brownian Motion simulations.
    2.  **Order Book Depth Analysis:** Real-time L2 Depth chart visualization.
    3.  **Black-Scholes Options Calculator:** Estimate fair value for calls/puts.
    4.  **Advanced Portfolio Risk Metrics:** Sharpe, Sortino, and Drawdown analytics.
    5.  **Prophet Auto-Tuning:** Automated grid-search optimization.
    6.  **Visual Overhaul:** Glassmorphism UI, Gauge Charts, Animated Loaders, and Interactive Heatmaps."""

content = content.replace("Welcome to the upgraded Crypto Fortune Teller v3.0!", "Welcome to the upgraded Crypto Fortune Teller v3.5!")

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as m:
    main_content = m.read()
    main_content = main_content.replace(about_search, about_replace)
    main_content = main_content.replace("Welcome to the upgraded Crypto Fortune Teller v3.0!", "Welcome to the upgraded Crypto Fortune Teller v3.5!")

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as m:
    m.write(main_content)

with open("README.md", "w") as f:
    f.write(content)
