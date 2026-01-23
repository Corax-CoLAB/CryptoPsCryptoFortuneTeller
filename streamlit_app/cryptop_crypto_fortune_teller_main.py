# cryptop_crypto_fortune_teller_main.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modules.cryptop_crypto_fortune_teller_helper import (
    get_coin_list,
    get_historical_prices,
    get_historical_ohlc,
    get_coin_metrics,
    get_fear_and_greed_index,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    compute_volatility,
    get_trending_coins,
    get_current_price,
    calculate_backtest,
    get_batch_historical_prices,
)
from modules.cryptop_crypto_fortune_teller_models import (
    forecast_prophet,
    forecast_lstm,
)

# 1) Page config
st.set_page_config(
    page_title="Crypto P's Crypto Fortune Teller",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2) Custom CSS for "Awesome Design"
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #4B0082;
    }
    /* Custom Headers */
    h1, h2, h3 {
        color: #E0E0E0;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #161b22;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #fff;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4B0082;
        color: #fff;
    }
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #d0d0d0;
    }
    [data-testid="stMetricLabel"] {
        color: #909090;
    }
    /* Custom HR */
    hr {
        border-color: #4B0082;
    }
</style>
""", unsafe_allow_html=True)

# 3) Header
logo_path = "assets/logo.png"

col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    try:
        st.image(logo_path, width=120)
    except:
        st.write("🔮") # Fallback if image missing
    st.title("Crypto P's Crypto Fortune Teller")
    st.markdown("<h4 style='text-align: center; color: #a0a0a0;'>Predict Cryptocurrency Prices with Magic (and Math)</h4>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 4) Sidebar
with st.sidebar:
    st.header("🔍 User Inputs")

    # Coin Selection
    with st.spinner("Loading coins..."):
        df_coins = get_coin_list()

    if df_coins.empty:
        st.error("Could not load coin list.")
        st.stop()

    df_coins['display'] = df_coins['name'] + ' (' + df_coins['symbol'].str.upper() + ')'
    options = df_coins['display'].tolist()
    mapping = pd.Series(df_coins.id.values, index=df_coins.display).to_dict()

    selected_option = st.selectbox("Select Cryptocurrency", options, index=0, help="Search and select the cryptocurrency you want to analyze.")
    coin_id = mapping[selected_option]

    # Model Selection
    model_choice = st.selectbox("Forecast Model", ["Prophet", "LSTM"], help="Prophet: Best for capturing seasonality and trends.\nLSTM: Deep learning model for complex pattern recognition.")
    forecast_days = st.slider("Forecast Days", 7, 90, 30, help="Choose how far into the future you want to predict prices (up to 90 days).")

    st.markdown("---")

    # Fear & Greed Mini Display
    st.subheader("😱 Fear & Greed")
    fng = get_fear_and_greed_index()
    if fng:
        val = int(fng['value'])
        color = "red" if val < 40 else "green" if val > 60 else "orange"
        st.markdown(f"<h2 style='color: {color}; text-align: center;'>{val}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{fng['classification']}</p>", unsafe_allow_html=True)
    else:
        st.write("N/A")

    st.markdown("---")

    # Quick Converter
    st.subheader("💱 Quick Converter")
    conv_amount = st.number_input("Amount to Convert", min_value=0.0, value=1.0, step=0.1, help="Enter the amount of cryptocurrency to convert.")
    if st.button("Convert"):
        with st.spinner("Converting..."):
            prices = get_current_price(coin_id, vs_currencies='usd,eur,btc,eth')
            if prices and coin_id in prices:
                p = prices[coin_id]
                st.write(f"**USD:** ${p.get('usd', 0) * conv_amount:,.2f}")
                st.write(f"**EUR:** €{p.get('eur', 0) * conv_amount:,.2f}")
                st.write(f"**BTC:** ₿{p.get('btc', 0) * conv_amount:.6f}")
                st.write(f"**ETH:** Ξ{p.get('eth', 0) * conv_amount:.6f}")
            else:
                st.error("Conversion failed.")

    st.markdown("---")
    st.info("Note: Prediction models are for educational purposes only. Not financial advice.")

# 5) Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🔮 Forecast", "📊 Technical Analysis", "🧪 Backtest", "💰 Portfolio", "🔥 Trending", "🔧 Stats", "🧙 About"])

# --- TAB 1: FORECAST ---
with tab1:
    st.subheader(f"Price Forecast: {selected_option}")

    with st.spinner("Consulting the oracles..."):
        # Fetch Data
        # We need sufficient history for good forecast
        price_df = get_historical_prices(coin_id, 'usd', days=365)

        if price_df.empty:
            st.error("No historical data available for this coin.")
        else:
            # Forecasting
            if model_choice == "Prophet":
                forecast_df = forecast_prophet(price_df, periods=forecast_days)
                # Filter for future only
                fv = forecast_df[forecast_df['ds'] > price_df.index[-1]][['ds','yhat','yhat_lower','yhat_upper']]
            else:
                fv = forecast_lstm(price_df, periods=forecast_days)

            # Plotting
            fig = go.Figure()

            # Historical Data
            fig.add_trace(go.Scatter(
                x=price_df.index,
                y=price_df['close'],
                mode='lines',
                name='History',
                line=dict(color='#00CC96')
            ))

            # Forecast
            fig.add_trace(go.Scatter(
                x=fv['ds'],
                y=fv['yhat'],
                mode='lines',
                name='Forecast',
                line=dict(color='#AB63FA', dash='dash')
            ))

            # Confidence Intervals (Prophet only)
            if model_choice == "Prophet" and 'yhat_upper' in fv.columns:
                fig.add_trace(go.Scatter(
                    x=fv['ds'], y=fv['yhat_upper'],
                    mode='lines',
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=fv['ds'], y=fv['yhat_lower'],
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    mode='lines',
                    fillcolor='rgba(171, 99, 250, 0.2)',
                    fill='tonexty',
                    showlegend=False
                ))

            fig.update_layout(
                title=f"{selected_option} - {model_choice} Forecast",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Forecast Table
            with st.expander("View Forecast Data"):
                df_disp = fv.rename(columns={
                    'ds':'Date','yhat':'Forecast'
                })
                if 'yhat_lower' in fv.columns:
                    df_disp = df_disp.rename(columns={'yhat_lower':'Lower CI','yhat_upper':'Upper CI'})

                st.dataframe(df_disp.set_index('Date').style.format("{:.2f}"))

# --- TAB 2: ANALYSIS ---
with tab2:
    st.subheader("Technical Analysis")

    days_back = st.radio("Analysis Period", [90, 180, 365], index=0, horizontal=True, help="Select the historical time range for technical analysis charts.")

    with st.spinner("Analyzing market patterns..."):
        # Fetch OHLC for better analysis
        ohlc_df = get_historical_ohlc(coin_id, days=days_back)

        if ohlc_df.empty:
            st.warning("OHLC data not available, falling back to simple price data.")
            # Fallback
            ohlc_df = get_historical_prices(coin_id, days=days_back)
            if ohlc_df.empty:
                st.error("No data available.")
                st.stop()
            ohlc_df['open'] = ohlc_df['close']
            ohlc_df['high'] = ohlc_df['close']
            ohlc_df['low'] = ohlc_df['close']

        # Calculate Indicators
        rsi = calculate_rsi(ohlc_df)
        macd_df = calculate_macd(ohlc_df)
        bb_df = calculate_bollinger_bands(ohlc_df)

        # Plot 1: Candlestick + BB
        fig_main = go.Figure()

        fig_main.add_trace(go.Candlestick(
            x=ohlc_df.index,
            open=ohlc_df['open'],
            high=ohlc_df['high'],
            low=ohlc_df['low'],
            close=ohlc_df['close'],
            name='OHLC'
        ))

        if not bb_df.empty:
            fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Upper'], line=dict(color='gray', width=1), name='BB Upper'))
            fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Lower'], line=dict(color='gray', width=1), name='BB Lower', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'))
            fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['SMA'], line=dict(color='orange', width=1), name='SMA 20'))

        fig_main.update_layout(title="Price Action & Bollinger Bands", template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig_main, use_container_width=True)

        # Plot 2: RSI
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi, name='RSI', line=dict(color='#EF553B')))
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="green", annotation_text="Oversold")
        fig_rsi.update_layout(title="Relative Strength Index (RSI)", template="plotly_dark", height=300, yaxis_range=[0, 100])
        st.plotly_chart(fig_rsi, use_container_width=True)

        # Plot 3: MACD
        if not macd_df.empty:
            fig_macd = make_subplots(specs=[[{"secondary_y": False}]])
            fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df['Histogram'], name='Histogram', marker_color='gray'))
            fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['MACD'], name='MACD', line=dict(color='#00CC96')))
            fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['Signal'], name='Signal', line=dict(color='#EF553B')))
            fig_macd.update_layout(title="MACD", template="plotly_dark", height=300)
            st.plotly_chart(fig_macd, use_container_width=True)

        # Correlation Matrix
        st.markdown("---")
        st.subheader("🔗 Market Correlation Matrix (90 Days)")
        with st.spinner("Crunching correlation numbers..."):
            # Major coins + selected
            comparison_coins = ['bitcoin', 'ethereum', 'solana', 'ripple', 'cardano']
            if coin_id not in comparison_coins:
                comparison_coins.append(coin_id)

            corr_df = get_batch_historical_prices(comparison_coins, days=90)
            if not corr_df.empty:
                corr_matrix = corr_df.corr()

                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.index,
                    colorscale='Viridis',
                    zmin=-1, zmax=1
                ))
                fig_corr.update_layout(
                    title="Correlation Heatmap",
                    template="plotly_dark",
                    height=500
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("Could not fetch data for correlation.")

# --- TAB 3: BACKTEST ---
with tab3:
    st.subheader("🧪 Strategy Backtester")
    st.write("Test simple trading strategies on historical data.")

    col_strat1, col_strat2 = st.columns(2)
    with col_strat1:
        strategy = st.selectbox("Select Strategy", ["SMA Crossover", "RSI Mean Reversion"], help="SMA Crossover: Buy when short-term average crosses above long-term.\nRSI Mean Reversion: Buy when oversold, sell when overbought.")
    with col_strat2:
        # Use same OHLC data from Analysis tab if available, else fetch
        bt_days = st.selectbox("Backtest Period (Days)", [180, 365, 730], index=1, help="The duration of historical data to test the strategy against.")

    if st.button("Run Backtest"):
        with st.spinner("Simulating trades..."):
            bt_data = get_historical_prices(coin_id, days=bt_days)
            if not bt_data.empty:
                res_df, metrics = calculate_backtest(bt_data, strategy_type=strategy)

                if not res_df.empty:
                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                    m2.metric("Market Return", f"{metrics['Market Return']:.2%}")
                    alpha = metrics['Total Return'] - metrics['Market Return']
                    m3.metric("Alpha", f"{alpha:.2%}", delta_color="normal")

                    # Chart
                    fig_bt = go.Figure()
                    fig_bt.add_trace(go.Scatter(x=res_df.index, y=res_df['cumulative_market_returns'], name='Market (Buy & Hold)', line=dict(color='gray', dash='dot')))
                    fig_bt.add_trace(go.Scatter(x=res_df.index, y=res_df['cumulative_strategy_returns'], name='Strategy', line=dict(color='#00CC96', width=2)))
                    fig_bt.update_layout(title=f"Equity Curve - {strategy}", template="plotly_dark", yaxis_title="Growth Factor (1 = Initial)", xaxis_title="Date")
                    st.plotly_chart(fig_bt, use_container_width=True)

                    with st.expander("Trade Log (Signals)"):
                        st.dataframe(res_df[['close', 'signal', 'strategy_returns']].tail(50))
                else:
                    st.error("Backtest failed.")
            else:
                st.error("No data for backtest.")

# --- TAB 4: PORTFOLIO ---
with tab4:
    st.subheader("💰 Portfolio Tracker")
    st.write("Track your crypto holdings in real-time.")

    # Initialize session state for portfolio
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    # Add coin form
    with st.expander("Add Asset"):
        with st.form("add_asset_form"):
            # Use the global coin list
            p_coin = st.selectbox("Coin", options, help="Select the coin to add to your portfolio.")
            p_amount = st.number_input("Amount Owned", min_value=0.0, step=0.01, help="The total quantity of coins you hold.")
            p_buy_price = st.number_input("Avg Buy Price (USD)", min_value=0.0, step=0.01, help="Your average purchase price per coin in USD.")
            submitted = st.form_submit_button("Add to Portfolio")

            if submitted:
                p_coin_id = mapping[p_coin]
                p_symbol = p_coin.split('(')[1].replace(')', '')
                st.session_state.portfolio.append({
                    'id': p_coin_id,
                    'name': p_coin,
                    'symbol': p_symbol,
                    'amount': p_amount,
                    'buy_price': p_buy_price
                })
                st.success(f"Added {p_amount} {p_symbol}")

    if st.session_state.portfolio:
        # Calculate values
        port_data = []
        total_value = 0
        total_cost = 0

        # Get current prices for all coins in portfolio
        p_ids = list(set([item['id'] for item in st.session_state.portfolio]))
        curr_prices = get_current_price(p_ids)

        for item in st.session_state.portfolio:
            cid = item['id']
            c_price = curr_prices.get(cid, {}).get('usd', 0) if curr_prices else 0
            curr_val = item['amount'] * c_price
            cost_val = item['amount'] * item['buy_price']
            pnl = curr_val - cost_val
            pnl_pct = (pnl / cost_val * 100) if cost_val > 0 else 0

            total_value += curr_val
            total_cost += cost_val

            port_data.append({
                'Coin': item['name'],
                'Amount': item['amount'],
                'Current Price': c_price,
                'Value': curr_val,
                'PnL ($)': pnl,
                'PnL (%)': pnl_pct
            })

        df_port = pd.DataFrame(port_data)

        # Summary Metrics
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Total Portfolio Value", f"${total_value:,.2f}")
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        col_p2.metric("Total PnL", f"${total_pnl:,.2f}", delta=f"{total_pnl_pct:.2f}%")
        col_p3.metric("Holdings Count", len(df_port))

        st.dataframe(df_port.style.format({
            'Current Price': "${:.2f}",
            'Value': "${:.2f}",
            'PnL ($)': "${:.2f}",
            'PnL (%)': "{:.2f}%"
        }))

        # Allocation Pie Chart
        fig_pie = go.Figure(data=[go.Pie(labels=df_port['Coin'], values=df_port['Value'], hole=.3)])
        fig_pie.update_layout(title="Portfolio Allocation", template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

        if st.button("Clear Portfolio"):
            st.session_state.portfolio = []
            st.experimental_rerun()

    else:
        st.info("Your portfolio is empty. Add some assets above!")

# --- TAB 5: TRENDING ---
with tab5:
    st.subheader("🔥 Trending Now")
    st.write("Top 7 coins searched by users on CoinGecko in the last 24 hours.")

    trending_coins = get_trending_coins()

    if trending_coins:
        cols = st.columns(4) # Display in rows of 4
        for i, coin in enumerate(trending_coins):
            item = coin['item']
            c_rank = item.get('market_cap_rank', 'N/A')
            c_name = item.get('name')
            c_sym = item.get('symbol')
            c_thumb = item.get('large')
            c_price_btc = item.get('price_btc')

            with cols[i % 4]:
                st.image(c_thumb, width=60)
                st.markdown(f"**{c_name} ({c_sym})**")
                st.caption(f"Rank: #{c_rank}")
                st.write(f"Price (BTC): {c_price_btc:.8f}")
                st.markdown("---")
    else:
        st.error("Could not load trending coins.")

# --- TAB 6: STATS ---
with tab6:
    st.subheader("Volatility Analysis")
    with st.spinner("Calculating volatility..."):
        # Fetch data for volatility (using 180 days for a good trend view)
        vol_ohlc = get_historical_ohlc(coin_id, days=180)
        if vol_ohlc.empty:
            vol_ohlc = get_historical_prices(coin_id, days=180)
            if not vol_ohlc.empty:
                # Ensure we have required columns if falling back to simple prices
                if 'close' in vol_ohlc.columns and 'high' not in vol_ohlc.columns:
                     vol_ohlc['high'] = vol_ohlc['close']
                     vol_ohlc['low'] = vol_ohlc['close']

        if not vol_ohlc.empty:
            vol_metrics = compute_volatility(vol_ohlc)

            if not vol_metrics.empty:
                fig_vol = make_subplots(specs=[[{"secondary_y": True}]])

                # Rolling Std Dev
                fig_vol.add_trace(go.Scatter(
                    x=vol_metrics.index,
                    y=vol_metrics['rolling_std'],
                    name='Rolling Std Dev (14d)',
                    line=dict(color='#AB63FA')
                ), secondary_y=False)

                # ATR
                if 'ATR' in vol_metrics.columns:
                    fig_vol.add_trace(go.Scatter(
                        x=vol_metrics.index,
                        y=vol_metrics['ATR'],
                        name='Average True Range (ATR)',
                        line=dict(color='#00CC96', dash='dot')
                    ), secondary_y=True)

                fig_vol.update_layout(
                    title="Volatility Metrics (180 Days)",
                    template="plotly_dark",
                    height=400,
                    hovermode="x unified",
                    yaxis_title="Std Dev",
                    yaxis2_title="ATR"
                )
                st.plotly_chart(fig_vol, use_container_width=True)
            else:
                st.warning("Not enough data to calculate volatility metrics.")
        else:
            st.warning("Could not fetch data for volatility analysis.")

    st.markdown("---")

    st.subheader("Community & Developer Statistics")

    with st.spinner("Gathering intel..."):
        metrics = get_coin_metrics(coin_id)

    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Twitter Followers", metrics.get('twitter_followers', 'N/A'))
        col2.metric("Reddit Subscribers", metrics.get('reddit_subscribers', 'N/A'))
        col3.metric("GitHub Stars", metrics.get('stars', 'N/A'))
        col4.metric("Forks", metrics.get('forks', 'N/A'))

        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Issues", metrics.get('total_issues', 'N/A'))
        col2.metric("Closed Issues", metrics.get('closed_issues', 'N/A'))
        col3.metric("Sentiment Up", f"{metrics.get('sentiment_up_pct', 0)}%")
        col4.metric("Sentiment Down", f"{metrics.get('sentiment_down_pct', 0)}%")

        st.markdown("---")
        st.json(metrics, expanded=False)
    else:
        st.info("Metrics unavailable for this coin.")

# --- TAB 7: ABOUT ---
with tab7:
    st.markdown("""
    ### 🧙 About Crypto P's Crypto Fortune Teller

    This application allows you to peer into the misty future of cryptocurrency prices using advanced machine learning models.

    **Features:**
    *   **Prophet Model:** developed by Facebook, excellent for detecting seasonality and trends.
    *   **LSTM (Long Short-Term Memory):** A Recurrent Neural Network designed for sequence prediction.
    *   **Technical Analysis:** Real-time calculation of RSI, MACD, and Bollinger Bands.
    *   **Market Correlation:** See how your coin moves relative to the market leaders.
    *   **Strategy Backtester:** Test simple trading strategies (SMA, RSI) on historical data.
    *   **Portfolio Tracker:** Track the value and performance of your crypto holdings.
    *   **Trending Dashboard:** See what's hot in the crypto world right now.
    *   **Community Stats:** Gauge the sentiment and developer activity.

    ---
    *Disclaimer: This tool is for educational purposes only. Cryptocurrency markets are highly volatile and unpredictable. Never invest more than you can afford to lose.*

    © 2025 Crypto P • [cryptop.coraxgardening.se](https://cryptop.coraxgardening.se)
    """)
