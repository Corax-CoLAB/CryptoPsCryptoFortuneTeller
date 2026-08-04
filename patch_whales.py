import re

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_helper.py", "r") as f:
    content = f.read()

replacement = """        whales = df[df['is_whale']].tail(10).copy()
        if not whales.empty:
            whales['volume'] = whales['volume'].apply(lambda x: f"${x:,.0f}")
            return whales[['timestamp', 'volume']].sort_values(by='timestamp', ascending=False)"""

content = re.sub(
    r"        whales = df\[df\['is_whale'\]\]\.tail\(10\)\.copy\(\)\n        if not whales\.empty:\n            whales\['volume'\] = \[f\"\$\{x:,\.0f\}\" for x in whales\['volume'\]\]\n            return whales\[\['timestamp', 'volume'\]\]\.sort_values\(by='timestamp', ascending=False\)",
    replacement,
    content
)

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_helper.py", "w") as f:
    f.write(content)
