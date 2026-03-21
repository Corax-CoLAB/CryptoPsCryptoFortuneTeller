import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

search = """        # Diversity Score
        if total_val > 0:
            weights = (df_port['Value'] / total_val) ** 2
            hhi = weights.sum()
            div_score = (1 - hhi) * 100 # 0 to 100
            col_p4.metric("Diversity Score", f"{div_score:.1f}/100")
        else:
            col_p4.metric("Diversity Score", "N/A")

        st.dataframe(df_port.style.format({'Price': "${:.2f}", 'Value': "${:.2f}", 'PnL ($)': "${:.2f}", 'PnL (%)': "{:.2f}%"}))"""

replace = """        # Diversity Score
        if total_val > 0:
            weights = (df_port['Value'] / total_val) ** 2
            hhi = weights.sum()
            div_score = (1 - hhi) * 100 # 0 to 100
            col_p4.metric("Diversity Score", f"{div_score:.1f}/100")
        else:
            col_p4.metric("Diversity Score", "N/A")

        # Technical Improvement 2: Advanced Portfolio Risk Metrics
        if len(p_ids) > 0 and total_val > 0:
            with st.spinner("Calculating Risk Metrics..."):
                port_hist = get_batch_historical_prices(p_ids, days=180)
                if not port_hist.empty:
                    # Calculate daily portfolio returns based on current weights
                    current_weights = df_port.set_index('Coin')['Value'] / total_val
                    # Map from ids to names since history uses ids as columns
                    # Actually get_batch returns ids as columns
                    port_hist.columns = [next(k for k, v in mapping.items() if v == col) for col in port_hist.columns]

                    # Align weights
                    aligned_weights = current_weights.reindex(port_hist.columns).fillna(0)

                    # Daily returns for each asset
                    daily_returns = port_hist.pct_change().dropna()

                    # Portfolio daily return
                    port_daily_return = (daily_returns * aligned_weights).sum(axis=1)

                    # Risk-free rate (assumed 2% annual)
                    rf_daily = 0.02 / 365

                    # Excess returns
                    excess_returns = port_daily_return - rf_daily

                    # Sharpe Ratio (Annualized)
                    volatility = port_daily_return.std()
                    sharpe = (excess_returns.mean() / volatility) * np.sqrt(365) if volatility > 0 else 0

                    # Sortino Ratio (Downside volatility only)
                    downside_returns = excess_returns[excess_returns < 0]
                    downside_vol = downside_returns.std()
                    sortino = (excess_returns.mean() / downside_vol) * np.sqrt(365) if downside_vol > 0 else 0

                    # Max Drawdown
                    cumulative_returns = (1 + port_daily_return).cumprod()
                    running_max = cumulative_returns.cummax()
                    drawdown = (cumulative_returns - running_max) / running_max
                    max_drawdown = drawdown.min() * 100

                    st.markdown("### 🛡️ Risk Analysis (180-Day)")
                    r_col1, r_col2, r_col3 = st.columns(3)
                    r_col1.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Risk-adjusted return. >1 is good, >2 is excellent.")
                    r_col2.metric("Sortino Ratio", f"{sortino:.2f}", help="Penalizes only downside volatility. >1 is good.")
                    r_col3.metric("Max Drawdown", f"{max_drawdown:.2f}%", help="Largest single drop from peak to trough.")

                    # Optional: Plot Drawdown
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown * 100, fill='tozeroy', line=dict(color='red')))
                    fig_dd.update_layout(title="Historical Drawdown (%)", template="plotly_dark", height=200, margin=dict(t=30, b=0))
                    st.plotly_chart(fig_dd, use_container_width=True)

        st.dataframe(df_port.style.format({'Price': "${:.2f}", 'Value': "${:.2f}", 'PnL ($)': "${:.2f}", 'PnL (%)': "{:.2f}%"}))"""

content = content.replace(search, replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
