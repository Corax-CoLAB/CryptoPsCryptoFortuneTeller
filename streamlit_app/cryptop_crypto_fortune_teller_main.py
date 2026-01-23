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

    options = [f"{row['name']} ({row['symbol'].upper()})" for _, row in df_coins.iterrows()]
    # Create a mapping
    mapping = {f"{row['name']} ({row['symbol'].upper()})": row['id'] for _, row in df_coins.iterrows()}

    selected_option = st.selectbox("Select Cryptocurrency", options, index=0)
    coin_id = mapping[selected_option]

    # Model Selection
    model_choice = st.selectbox("Forecast Model", ["Prophet", "LSTM"])
    forecast_days = st.slider("Forecast Days", 7, 90, 30)

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
    st.info("Note: Prediction models are for educational purposes only. Not financial advice.")

# 5) Main Content Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔮 Forecast", "📊 Technical Analysis", "🔧 Stats", "🧙 About"])

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

    days_back = st.radio("Analysis Period", [90, 180, 365], index=0, horizontal=True)

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

# --- TAB 3: STATS ---
with tab3:
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

# --- TAB 4: ABOUT ---
with tab4:
    st.markdown("""
    ### 🧙 About Crypto P's Crypto Fortune Teller

    This application allows you to peer into the misty future of cryptocurrency prices using advanced machine learning models.

    **Features:**
    *   **Prophet Model:** developed by Facebook, excellent for detecting seasonality and trends.
    *   **LSTM (Long Short-Term Memory):** A Recurrent Neural Network designed for sequence prediction.
    *   **Technical Analysis:** Real-time calculation of RSI, MACD, and Bollinger Bands.
    *   **Community Stats:** Gauge the sentiment and developer activity.

    ---
    *Disclaimer: This tool is for educational purposes only. Cryptocurrency markets are highly volatile and unpredictable. Never invest more than you can afford to lose.*

    © 2025 Crypto P • [cryptop.coraxgardening.se](https://cryptop.coraxgardening.se)
    """)
