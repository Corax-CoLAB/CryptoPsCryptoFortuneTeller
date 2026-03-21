import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

# Add import for calculate_black_scholes
import_search = "from modules.cryptop_crypto_fortune_teller_helper import ("
import_replace = import_search + "\n    calculate_black_scholes,"

content = content.replace(import_search, import_replace)

search = """    c_tab1, c_tab2, c_tab3, c_tab4, c_tab5 = st.tabs(["If I Invested...", "Moon Math", "Risk/Reward", "DCA Time Machine", "Impermanent Loss"])"""
replace = """    c_tab1, c_tab2, c_tab3, c_tab4, c_tab5, c_tab6 = st.tabs(["If I Invested...", "Moon Math", "Risk/Reward", "DCA Time Machine", "Impermanent Loss", "Options Pricing"])"""

content = content.replace(search, replace)

tab6_content = """    with c_tab5:
        st.write("#### 💧 Impermanent Loss Calculator")
        st.write("Estimate potential loss when providing liquidity to a pool.")
        col_il1, col_il2 = st.columns(2)
        price_a = col_il1.number_input("Price Change Asset A (%)", value=0.0, step=1.0)
        price_b = col_il2.number_input("Price Change Asset B (%)", value=0.0, step=1.0)

        il_val = calculate_impermanent_loss(price_a, price_b)
        st.metric("Impermanent Loss", f"{il_val:.2f}%", delta=f"{il_val:.2f}%")
        st.info("Note: This assumes a 50/50 Liquidity Pool.")

    with c_tab6:
        st.write("#### 📈 Black-Scholes Options Pricing")
        st.write("Estimate fair value for European Call and Put options.")

        # Pre-fill S with current price if available
        current_p = get_current_price(coin_id).get(coin_id, {}).get('usd', 0)

        col_bs1, col_bs2, col_bs3 = st.columns(3)
        S = col_bs1.number_input("Current Asset Price (S)", value=float(current_p) if current_p else 1000.0, min_value=0.0)
        K = col_bs2.number_input("Strike Price (K)", value=float(current_p) * 1.1 if current_p else 1100.0, min_value=0.0)
        T_days = col_bs3.number_input("Days to Expiration", value=30, min_value=1)

        col_bs4, col_bs5, col_bs6 = st.columns(3)
        r = col_bs4.number_input("Risk-Free Rate (Annual %)", value=4.5) / 100

        # Pre-fill Volatility from history if possible
        vol_est = 50.0 # Default 50%
        hist = get_historical_prices(coin_id, days=90)
        if not hist.empty:
            vol_est = hist['close'].pct_change().std() * np.sqrt(365) * 100

        sigma = col_bs5.number_input("Implied Volatility (Annual %)", value=float(vol_est)) / 100

        if st.button("Calculate Option Price"):
            T_years = T_days / 365.0
            call, put = calculate_black_scholes(S, K, T_years, r, sigma)

            # Interactive visualization of pricing surface
            bs_c1, bs_c2 = st.columns(2)
            bs_c1.metric("Call Option Fair Value", f"${call:.2f}")
            bs_c2.metric("Put Option Fair Value", f"${put:.2f}")

            st.info("Note: Crypto options often have American exercise styles and extreme jump-risk, making Black-Scholes an approximation.")"""

content = content.replace("""    with c_tab5:
        st.write("#### 💧 Impermanent Loss Calculator")
        st.write("Estimate potential loss when providing liquidity to a pool.")
        col_il1, col_il2 = st.columns(2)
        price_a = col_il1.number_input("Price Change Asset A (%)", value=0.0, step=1.0)
        price_b = col_il2.number_input("Price Change Asset B (%)", value=0.0, step=1.0)

        il_val = calculate_impermanent_loss(price_a, price_b)
        st.metric("Impermanent Loss", f"{il_val:.2f}%", delta=f"{il_val:.2f}%")
        st.info("Note: This assumes a 50/50 Liquidity Pool.")""", tab6_content)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
