import re

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "r") as f:
    content = f.read()

search = """    # Calculate percentiles (Mean, 5th, 95th)
    mean_sim = np.mean(simulations, axis=1)
    lower_sim = np.percentile(simulations, 5, axis=1)
    upper_sim = np.percentile(simulations, 95, axis=1)"""

replace = """    # Calculate percentiles (Median, 5th, 95th)
    mean_sim = np.median(simulations, axis=1)
    lower_sim = np.percentile(simulations, 5, axis=1)
    upper_sim = np.percentile(simulations, 95, axis=1)"""

content = content.replace(search, replace)

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "w") as f:
    f.write(content)
