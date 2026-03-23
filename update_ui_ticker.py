with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

ticker_code = """
# Feature: Ticker Tape (Visual Improvement 1)
# Fetch trending coins quickly for the banner
with st.spinner("Initializing Oracle..."):
    gainers, losers = get_top_gainers_losers(limit=10)

if not gainers.empty:
    ticker_items = []
    for _, row in gainers.head(5).iterrows():
        sym = row['symbol'].upper()
        pct = row['price_change_percentage_24h']
        color = "#00FF00" if pct > 0 else "#FF0000"
        ticker_items.append(f"<span style='margin-right: 30px; font-weight: bold;'>🔥 {sym} <span style='color: {color};'>{pct:+.2f}%</span></span>")

    for _, row in losers.head(5).iterrows():
        sym = row['symbol'].upper()
        pct = row['price_change_percentage_24h']
        color = "#00FF00" if pct > 0 else "#FF0000"
        ticker_items.append(f"<span style='margin-right: 30px; font-weight: bold;'>🧊 {sym} <span style='color: {color};'>{pct:+.2f}%</span></span>")

    ticker_html = f\"\"\"
    <div style="width: 100%; overflow: hidden; background: linear-gradient(90deg, #150020, #2a0e3b, #150020); border-bottom: 2px solid #FF00FF; border-top: 2px solid #00FFFF; padding: 10px 0; margin-bottom: 20px;">
        <div style="white-space: nowrap; animation: ticker 25s linear infinite; font-family: 'Orbitron', sans-serif; font-size: 1.2rem; color: white;">
            {''.join(ticker_items)}
            {''.join(ticker_items)}
        </div>
    </div>
    <style>
        @keyframes ticker {{
            0%   {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
    </style>
    \"\"\"
    st.markdown(ticker_html, unsafe_allow_html=True)
"""

if "Feature: Ticker Tape" not in content:
    content = content.replace("st.markdown(\"<hr>\", unsafe_allow_html=True)", "st.markdown(\"<hr>\", unsafe_allow_html=True)\n" + ticker_code)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)

print("Ticker Tape Added")
