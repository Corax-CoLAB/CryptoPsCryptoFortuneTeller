with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

search = """                "LSTM",
                "ARIMA",
                "SARIMA",
                "Random Forest"
            ],"""
replace = """                "LSTM",
                "ARIMA",
                "SARIMA",
                "Random Forest",
                "Monte Carlo (GBM)"
            ],"""

content = content.replace(search, replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
