# Streamlit page title: 🧙‍♂️ About
# cryptop_crypto_fortune_teller_about.py

import streamlit as st
from datetime import datetime
import sys
import os

# Ensure modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.cryptop_crypto_fortune_teller_styles import apply_custom_css

# Apply Custom CSS
apply_custom_css()

st.title("🔮 About Crypto P's Fortune Teller 🔮")

# Description and credits
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h3 style='font-family: Rye, cursive; color: #FFD700;'>The Digital Carnival of the Future</h3>
</div>

**Crypto P's Fortune Teller** is an interactive web app built with Streamlit and Python 3.11.
It leverages cutting-edge machine learning models and multiple data sources to forecast cryptocurrency prices
and analyze market volatility and metrics.

- 📈 **Forecast Models:** Choose between Prophet (Bayesian time-series forecasting, great for seasonality) and LSTM (deep learning for complex patterns).
- 📊 **Volatility Indicators:** Rolling Standard Deviation and Average True Range (ATR) visualize risk and price swings.
- 🌐 **Data Sources:** CoinGecko public API provides historical prices, market cap, volume, community stats (Twitter, Reddit) and developer stats (GitHub).
- 🔄 **Dynamic Coverage:** Supports all available cryptocurrencies from CoinGecko's free demo API.
- ⚙️ **User Controls:** Select coin, model, forecast horizon; view interactive charts and tables.

**Note:** This app is for educational and entertainment purposes and is not financial advice. Always conduct your own research.

_Last updated: {}_
""".format(datetime.now().strftime("%Y-%m-%d")))
