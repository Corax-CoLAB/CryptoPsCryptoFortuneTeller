import re

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_helper.py", "r") as f:
    content = f.read()

bs_func = """
@st.cache_data
def calculate_black_scholes(S, K, T, r, sigma):
    \"\"\"
    Calculate Black-Scholes option price for Call and Put options.
    S: Current Asset Price
    K: Strike Price
    T: Time to Expiration (in years)
    r: Risk-free Interest Rate (annual)
    sigma: Volatility (annualized)
    \"\"\"
    from scipy.stats import norm
    import numpy as np

    # Handle zero/negative inputs
    if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
        return 0.0, 0.0

    d1 = (np.log(S / K) + (r + (sigma ** 2) / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return call_price, put_price

"""

if "def calculate_black_scholes" not in content:
    content += bs_func

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_helper.py", "w") as f:
    f.write(content)
