Crypto P's Crypto Fortune Teller

An interactive Streamlit app for forecasting cryptocurrency prices with advanced ML models and volatility analysis.

Project Structure

CryptoPsCryptoFortuneTeller/
├── streamlit_app/
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── cryptop_crypto_fortune_teller_helper.py
│   │   └── cryptop_crypto_fortune_teller_models.py
│   ├── pages/
│   │   └── cryptop_crypto_fortune_teller_about.py
│   └── cryptop_crypto_fortune_teller_main.py
├── requirements.txt
└── README.md

streamlit_app/: Contains all Streamlit application code.

modules/: Helper functions for data fetching, metrics, and forecasting models.

pages/: Multipage "About" page for app description.

cryptop_crypto_fortune_teller_main.py: Main app entry point.

requirements.txt: List of Python dependencies.

README.md: This file.

Installation

Clone the repository

git clone <your-repo-url> CryptoPsCryptoFortuneTeller
cd CryptoPsCryptoFortuneTeller

Create a Python 3.11 virtual environment

python3.11 -m venv venv

On Windows (PowerShell):

py -3.11 -m venv venv

Activate the environment

macOS/Linux:

source venv/bin/activate

Windows (PowerShell):

.\venv\Scripts\Activate.ps1

Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

Verify installation

python -c "import streamlit, pandas, prophet, tensorflow; print('✅ OK')"

Running the App

From the project root:

cd streamlit_app
streamlit run cryptop_crypto_fortune_teller_main.py

Access the app at http://localhost:8501/

Use the sidebar to select coins, forecasting model, and view the About page under "Pages".

Features

Dynamic coin selection: All cryptocurrencies from CoinGecko.

Forecast models: Choose between Prophet and LSTM.

Volatility analysis: Rolling standard deviation and Average True Range (ATR).

Community & developer metrics: Twitter, Reddit, GitHub stats.

License

Licensed under the MIT License. See LICENSE.md for details.
