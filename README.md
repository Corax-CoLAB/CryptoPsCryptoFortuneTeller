# 🔮 Crypto P's Crypto Fortune Teller

![Crypto P's Crypto Fortune Teller Logo](streamlit_app/assets/logo.png)

**Crypto P's Crypto Fortune Teller** is an interactive, "awesomely designed" Streamlit application that empowers you to peer into the misty future of cryptocurrency prices. By leveraging advanced machine learning models (Prophet & LSTM) and real-time data from CoinGecko, this tool provides price forecasts, technical analysis, and deep insights into market sentiment and community activity.

---

## ✨ Features

### 🔮 Price Forecasting
- **Prophet Model:** Utilizes Facebook's Prophet model for accurate time-series forecasting, capturing seasonality and trends with confidence intervals.
- **LSTM Model:** Deploys a Long Short-Term Memory (Recurrent Neural Network) model to detect complex patterns in price sequences.
- **Customizable Horizon:** Forecast up to 90 days into the future.
- **Interactive Charts:** Beautiful Plotly visualizations comparing historical data with future predictions.

### 📊 Technical Analysis
- **Advanced Charting:** View Candlestick charts with adjustable lookback periods (90, 180, 365 days).
- **Indicators:**
  - **Bollinger Bands:** For volatility analysis and potential breakout detection.
  - **RSI (Relative Strength Index):** To identify overbought or oversold conditions.
  - **MACD (Moving Average Convergence Divergence):** To spot momentum changes and trend reversals.

### 🔧 Market & Community Stats
- **Fear & Greed Index:** Real-time gauge of market sentiment (Fear, Greed, etc.).
- **Volatility Analysis:** Rolling Standard Deviation and Average True Range (ATR) metrics.
- **Community Intelligence:** Track Twitter followers, Reddit subscribers, and sentiment votes (Bullish/Bearish).
- **Developer Activity:** Monitor GitHub stars, forks, issues, and pull requests to assess project health.

### 🎨 Design
- **Modern UI:** A custom dark-themed interface with purple accents for a "mystical" yet professional look.
- **Responsive Layout:** Optimized for wide screens with sidebar controls and tabbed content.

---

## 📂 Project Structure

```text
CryptoPsCryptoFortuneTeller/
├── streamlit_app/
│   ├── assets/
│   │   ├── logo.png               # App logo
│   │   └── crypto.gif             # Animation
│   ├── modules/
│   │   ├── cryptop_crypto_fortune_teller_helper.py  # Data fetching & indicators
│   │   └── cryptop_crypto_fortune_teller_models.py  # ML models (Prophet, LSTM)
│   ├── pages/
│   │   └── 🧙 About.py             # About page
│   └── cryptop_crypto_fortune_teller_main.py      # Main application entry point
├── tests/
│   ├── test_helper.py             # Tests for helper functions
│   └── test_models.py             # Tests for ML models
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
   - Use the **Sidebar** to:
     - Select a Cryptocurrency (fetched dynamically from CoinGecko).
     - Choose your Forecast Model (Prophet or LSTM).
     - Set the Forecast Days slider.
   - Explore the **Tabs**:
     - **🔮 Forecast:** View price predictions.
     - **📊 Technical Analysis:** Analyze charts and indicators.
     - **🔧 Stats:** Check community and developer metrics.
     - **🧙 About:** Learn more about the project.

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

This will verify the integrity of the helper functions, indicators, and forecasting models.

---

## ⚠️ Disclaimer

**This application is for educational and entertainment purposes only.**

The price forecasts and technical analysis provided by this tool are based on historical data and machine learning algorithms, which cannot predict the future with certainty. Cryptocurrency markets are highly volatile. **This is not financial advice.** Always conduct your own research and never invest more than you can afford to lose.

---

## 📄 License

This project is licensed under the MIT License.
