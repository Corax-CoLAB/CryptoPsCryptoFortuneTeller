<div align="center">

<img src="streamlit_app/assets/logo.png" alt="Crypto P's Crypto Fortune Teller Logo" width="250">

# 🔮 <span style="color:#A020F0">Crypto P's Crypto Fortune Teller</span> 🔮

**A Psychedelic Cosmic Circus of AI-Powered Crypto Analytics & Forecasting**

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blueviolet.svg?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg?style=for-the-badge&logo=streamlit)](https://cryptop.coraxcolab.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Security: Checked](https://img.shields.io/badge/Security-AST%20%26%20Regex%20Checked-brightgreen.svg?style=for-the-badge)](https://github.com/PelleNybe)

<img src="streamlit_app/assets/crypto.gif" alt="Crypto Animation" width="600">

---
**Peer into the misty future of cryptocurrency prices with advanced machine learning, real-time data, and deep technical analysis.**
</div>

## 🌟 Discover the Future of Trading

**Crypto P's Crypto Fortune Teller** is an interactive, stunningly designed Streamlit application that empowers you to peer into the misty future of cryptocurrency prices. By leveraging advanced machine learning models (Prophet, LSTM, ARIMA, Random Forest) and real-time data from CoinGecko, CCXT Exchanges, and Freqtrade, this tool provides price forecasts, deep technical analysis, strategy backtesting, and comprehensive market insights.

<br>

<details>
<summary><b>✨ Click to Expand: Core Features</b></summary>
<br>

### 🧠 AI-Powered Forecasting
- **Prophet Model:** Utilizes Facebook's Prophet model for accurate time-series forecasting, capturing seasonality and trends with confidence intervals.
- **LSTM Networks:** Deploys Long Short-Term Memory (Recurrent Neural Network) models to detect complex patterns in price sequences.
- **Ensemble Projections:** 30-day ensemble forecast to estimate the future value of specific assets in your portfolio.
- **Random Forest & ARIMA:** Advanced statistical and ensemble methods for comprehensive price prediction.
- **Customizable Horizon:** Forecast up to 365 days into the future (capped for performance).

### 📈 Advanced Technical Analysis
- **Interactive Candlestick Charts:** Zoom, pan, and analyze price action across multiple timeframes.
- **Rich Indicator Suite:** SMA Ribbon, Bollinger Bands, Ichimoku Cloud, Fibonacci Levels, Pivot Points.
- **Oscillators & Momentum:** RSI, Stochastic Oscillator, MACD, CCI, ADX, VWAP, Parabolic SAR.
- **Sentiment:** Real-time gauge of market sentiment via Fear & Greed Index.

### 🤖 Automated Trading & Exchanges
- **CCXT Integration:** Direct connectivity to Bitget, Gate, Bybit, OKX, KuCoin, and Binance.
- **Freqtrade Bot Manager:** Seamlessly monitor and control your Freqtrade bot instance via direct API calls.
- **Live Order Books & Volume:** Real-time data from major centralized exchanges.

### 🧪 Strategy Backtesting
- **Simulation Engine:** Test trading strategies against historical data (e.g., SMA Crossover, RSI Mean Reversion, Bollinger Squeeze, MACD Crossover).
- **Performance Metrics:** View Total Return, Market Return, Alpha, Equity Curves, and Risk assessment.

### 💼 Portfolio & Market Tools
- **Portfolio Tracker:** Monitor your holdings, track PnL, view allocation pie charts, and project future wealth.
- **Market Heatmap:** Visualize the top 50 coins by market cap using an interactive Treemap.
- **Smart Calculators:** DCA, ROI, "Moon Math", and Risk/Reward planning.
- **Social Intel:** Developer activity (GitHub) and community sentiment (Reddit/Twitter).

</details>

<br>

## 🚀 Live Demo & Connect

<div align="center">
  <h3>Try the App Now:</h3>
  <a href="https://cryptop.coraxcolab.com">
    <img src="https://img.shields.io/badge/Launch-Crypto_P's_Fortune_Teller-FF4B4B?style=for-the-badge&logo=streamlit" alt="Launch App">
  </a>
</div>

<br>

---

## 👨‍💻 Meet the Creator & Company

This masterpiece of crypto-analytical software was crafted by **Pelle Nyberg** at **Corax CoLAB**.

<div align="center">

### **Pelle Nyberg**
*Visionary Software Engineer & Crypto Analyst*

[![GitHub](https://img.shields.io/badge/GitHub-PelleNybe-181717?style=for-the-badge&logo=github)](https://github.com/PelleNybe)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/pellenyberg/)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit_Site-005571?style=for-the-badge&logo=firefox)](https://pellenybe.github.io)

### **Corax CoLAB**
*Innovating the Digital Frontier*

[![Corax CoLAB](https://img.shields.io/badge/Corax_CoLAB-Website-FF6B6B?style=for-the-badge&logo=googlechrome)](https://coraxcolab.com)

</div>

---

## 🎨 A Psychedelic Cosmic Circus Theme

The UI enforces a **'Psychedelic Cosmic Circus'** theme, utilizing dark-themed neon accents, deep purple/black radial gradients, and custom Google Fonts (`Rye`, `Cinzel`, `Quicksand`, `Orbitron`). It’s an immersive, trippy, yet highly professional analytics experience.

---

## 🛡️ Enterprise-Grade Security & Architecture

We take security seriously. This application includes:
- **XSS & SSRF Protection:** Automated AST-based XSS scanners and strict URL validators.
- **Session Vault:** Secure server-side caching of sensitive credentials (Exchange/Freqtrade keys).
- **Tiered Bucket Caching:** Optimized API calls via Streamlit `@st.cache_data`.
- **Rigorous Test Suite:** Over a dozen test files covering backtesting, ML models, ensemble logic, API endpoints, and security configurations.

---

## 📂 Project Structure Snapshot

<details>
<summary><b>View Directory Tree</b></summary>

```text
CryptoPsCryptoFortuneTeller/
├── streamlit_app/
│   ├── assets/
│   │   ├── logo.png               # App logo
│   │   └── crypto.gif             # Animation
│   ├── modules/
│   │   ├── cryptop_crypto_fortune_teller_helper.py  # Indicators, Data fetching
│   │   ├── cryptop_crypto_fortune_teller_models.py  # Prophet, LSTM, ARIMA, RF
│   │   ├── cryptop_crypto_fortune_teller_styles.py  # Psychedelic CSS Theme
│   │   ├── exchange_manager.py                      # CCXT Connectivity
│   │   └── freqtrade_manager.py                     # Freqtrade API control
│   └── cryptop_crypto_fortune_teller_main.py      # Entry point
├── benchmarks/                    # Performance benchmarking (LSTM, Prophet, Caching)
├── tests/                         # Extensive Pytest & Unittest suite
├── health_check.py                # Environment & API validation
└── requirements.txt               # Pinned dependencies (e.g. numpy<2.0.0)
```
</details>

---

## 🛠️ Tech Stack & Dependencies

*   **Frontend & Framework:** Streamlit
*   **Data & Math:** Pandas, NumPy (`>=1.25.0,<2.0.0`)
*   **Visualization:** Plotly
*   **Machine Learning:** Facebook Prophet, TensorFlow/Keras (LSTM), Scikit-Learn, Statsmodels
*   **Crypto & APIs:** PyCoinGecko, CCXT (Exchanges), Requests

---

## ⚙️ Installation & Local Development

### 1. Clone & Setup
```bash
git clone https://github.com/PelleNybe/CryptoPsCryptoFortuneTeller.git
cd CryptoPsCryptoFortuneTeller
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Health Check & Tests
Verify your environment and API connectivity:
```bash
python3 health_check.py
python3 -m pytest
```

### 4. Launch the Fortune Teller
```bash
streamlit run streamlit_app/cryptop_crypto_fortune_teller_main.py
```

---

## ⚠️ Disclaimer

**This application is for educational and entertainment purposes only.**

The price forecasts, backtests, and technical analysis provided by this tool are based on historical data and machine learning algorithms, which cannot predict the future with certainty. Cryptocurrency markets are highly volatile. **This is not financial advice.** Always conduct your own research and never invest more than you can afford to lose.

---

<div align="center">
  <p><b>Built with ❤️ by Pelle Nyberg & Corax CoLAB</b></p>
  <p>&copy; 2024 Corax CoLAB. All rights reserved.</p>
</div>

