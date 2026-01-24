# 🔮 Crypto P's Crypto Fortune Teller

![Crypto P's Crypto Fortune Teller Logo](streamlit_app/assets/logo.png)

**Crypto P's Crypto Fortune Teller** is an interactive, "awesomely designed" Streamlit application that empowers you to peer into the misty future of cryptocurrency prices. By leveraging advanced machine learning models (Prophet & LSTM) and real-time data from CoinGecko, this tool provides price forecasts, deep technical analysis, strategy backtesting, and comprehensive market insights.

---

## ✨ Features

### 🔮 AI-Powered Forecasting
- **Prophet Model:** Utilizes Facebook's Prophet model for accurate time-series forecasting, capturing seasonality and trends with confidence intervals.
- **LSTM Model:** Deploys a Long Short-Term Memory (Recurrent Neural Network) model to detect complex patterns in price sequences.
- **Customizable Horizon:** Forecast up to 90 days into the future.
- **Exportable Data:** Download forecast results as CSV for offline analysis.

### 📊 Advanced Technical Analysis
- **Interactive Candlestick Charts:** Zoom, pan, and analyze price action across multiple timeframes (90d, 180d, 1y, Custom).
- **Rich Indicator Suite:**
  - **SMA Ribbon:** Visualize trends with Simple Moving Averages (20, 50, 100, 200).
  - **Bollinger Bands:** Analyze volatility and potential breakouts.
  - **Ichimoku Cloud:** Identify trend direction, support, and resistance.
  - **Fibonacci Levels:** Automatic retracement levels based on visible price range.
  - **Pivot Points:** Daily projected Support (S1-S3) and Resistance (R1-R3) levels.
  - **Oscillators:** RSI (Relative Strength Index), Stochastic Oscillator, and MACD (Moving Average Convergence Divergence).

### 🧪 Strategy Backtesting
- **Simulation Engine:** Test trading strategies against historical data.
- **Strategies Included:**
  - **SMA Crossover:** Classic "Golden Cross" strategy.
  - **RSI Mean Reversion:** Buy/Sell based on overbought/oversold conditions.
- **Performance Metrics:** View Total Return, Market Return, Alpha, and Equity Curves.

### 💰 Portfolio & Market Tools
- **Portfolio Tracker:** Monitor your holdings, track PnL ($ and %), and view allocation pie charts.
- **Asset Comparison:** Compare the relative performance (base 100) of up to 5 cryptocurrencies side-by-side.
- **Market Overview:** Visualize the top 50 coins by market cap using an interactive Treemap color-coded by 24h performance.

### 🧮 Smart Calculators
- **"If I Invested...":** Calculate historical ROI based on past dates.
- **Moon Math:** Determine the price required for a coin to reach a target Market Cap (and the potential upside).
- **Risk/Reward:** Plan your trades with a dedicated R:R ratio calculator.

### 🔧 Sentiment & Stats
- **Fear & Greed Index:** Real-time gauge of market sentiment.
- **Volatility Analysis:** Rolling Standard Deviation and Average True Range (ATR).
- **Community Intelligence:** Track Twitter followers, Reddit subscribers, and sentiment votes.
- **Developer Activity:** Monitor GitHub stars, forks, issues, and pull requests to assess project health.

### 🎨 Design
- **Psychedelic Carnival Theme:** A custom dark-themed interface with neon accents, Google Fonts ('Rye', 'Cinzel'), and responsive layout.
- **Quick Converter:** Instant currency conversion (USD, EUR, BTC, ETH).

---

## 📂 Project Structure

```text
CryptoPsCryptoFortuneTeller/
├── streamlit_app/
│   ├── assets/
│   │   ├── logo.png               # App logo
│   │   └── crypto.gif             # Animation
│   ├── modules/
│   │   ├── cryptop_crypto_fortune_teller_helper.py  # Data fetching, indicators, calcs
│   │   ├── cryptop_crypto_fortune_teller_models.py  # ML models (Prophet, LSTM)
│   │   └── cryptop_crypto_fortune_teller_styles.py  # Custom CSS & Theme
│   ├── pages/
│   │   └── 🧙 About.py             # About page
│   └── cryptop_crypto_fortune_teller_main.py      # Main application entry point
├── benchmarks/                    # Performance benchmarking scripts
├── tests/
│   ├── test_backtest.py           # Tests for trading strategies
│   └── ...                        # Other unit tests
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip

### Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd CryptoPsCryptoFortuneTeller
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 Usage

1. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app/cryptop_crypto_fortune_teller_main.py
   ```

2. **Navigate:**
   - Open your browser to `http://localhost:8501`.
   - **Sidebar:** Select your asset, configure forecast models, and check the Fear & Greed Index.
   - **Tabs:**
     - **🔮 Forecast:** View AI price predictions.
     - **📊 Analysis:** Deep dive with charts and indicators.
     - **⚖️ Compare:** Benchmark assets against each other.
     - **🧪 Backtest:** Validate your trading strategies.
     - **💰 Portfolio:** Track your crypto wealth.
     - **🌍 Market:** View the global market heatmap.
     - **🧮 Calculators:** Plan trades and dream big.
     - **🔧 Stats:** Check fundamental and social metrics.
     - **🧙 About:** Learn about the version updates.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Data Visualization:** [Plotly](https://plotly.com/python/)
- **Data Manipulation:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Machine Learning:**
  - [Prophet](https://facebook.github.io/prophet/) (Time-series forecasting)
  - [TensorFlow/Keras](https://www.tensorflow.org/) (LSTM Neural Networks)
  - [Scikit-learn](https://scikit-learn.org/) (Data preprocessing)
- **APIs:**
  - [CoinGecko API](https://www.coingecko.com/en/api) (Market data)
  - [Alternative.me API](https://alternative.me/crypto/fear-and-greed-index/) (Fear & Greed Index)

---

## 🧪 Testing

The project uses `pytest` for unit testing.

To run the tests:
```bash
pytest
```
This ensures the integrity of helper functions, indicators, backtesting logic, and forecasting models.

---

## ⚠️ Disclaimer

**This application is for educational and entertainment purposes only.**

The price forecasts, backtests, and technical analysis provided by this tool are based on historical data and machine learning algorithms, which cannot predict the future with certainty. Cryptocurrency markets are highly volatile. **This is not financial advice.** Always conduct your own research and never invest more than you can afford to lose.

---

## 📄 License

This project is licensed under the MIT License.
