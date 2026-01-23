# Streamlit page title: 🔮 Crypto P's Crypto Fortune Teller
# cryptop_crypto_fortune_teller_main.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from modules.cryptop_crypto_fortune_teller_helper import (
    get_coin_list,
    get_historical_prices,
    get_historical_ohlc,
    compute_volatility,
    get_coin_metrics,
)
from modules.cryptop_crypto_fortune_teller_models import (
    forecast_prophet,
    forecast_lstm,
)

# 1) Page config (must come first)
st.set_page_config(
    page_title="Crypto P's Crypto Fortune Teller",
    page_icon="🔮",
    layout="wide",
)

# 2) Header with local image support
logo_path = "assets/logo.png"

st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 4, 1])  # Fördelar utrymmet (vänster - center - höger)
with col2:
    st.image(logo_path, width=360)

st.markdown(
    "<h1 style='text-align: center; color: #E0E0E0; font-size: 2.8rem;'>"
    "Crypto P's Crypto Fortune Teller</h1>",
    unsafe_allow_html=True
)

st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)


# 3) Sidebar inputs
with st.sidebar:
    st.header("🔍 User Inputs")
    df_coins = get_coin_list()
    options = [f"{row['name']} ({row['symbol'].upper()})" for _, row in df_coins.iterrows()]
    mapping = {opt: df_coins.loc[i, "id"] for i, opt in enumerate(options)}
    selected = st.selectbox("Select Cryptocurrency", options)
    coin_id = mapping[selected]
    model_choice = st.selectbox("Forecast Model", ["Prophet", "LSTM"])
    forecast_days = st.slider("Forecast Days", 7, 90, 30)
    st.markdown("---")

# 4) Main title/subtitle
st.subheader("Predict Cryptocurrency Prices with Magic (and Math)")

# 5) Fetch data
with st.spinner("Fetching historical data…"):
    price_df = get_historical_prices(coin_id, 'usd', days=365)
    price_df.index = pd.to_datetime(price_df.index)

with st.spinner("Fetching additional metrics…"):
    metrics = get_coin_metrics(coin_id)

# 6) Community & Developer Stats
with st.container():
    st.subheader("🔧 Community & Developer Stats")
    cols = st.columns(4)
    if metrics:
        cols[0].metric("Twitter Followers", metrics.get('twitter_followers', 'N/A'))
        cols[1].metric("Reddit Subscribers", metrics.get('reddit_subscribers', 'N/A'))
        cols[2].metric("GitHub Stars", metrics.get('stars', 'N/A'))
        cols[3].metric("Open Issues", metrics.get('total_issues', 'N/A'))
        cols2 = st.columns(4)
        cols2[0].metric("GitHub Forks", metrics.get('forks', 'N/A'))
        cols2[1].metric("Closed Issues", metrics.get('closed_issues', 'N/A'))
        cols2[2].metric("Sentiment Up %", metrics.get('sentiment_up_pct', 'N/A'))
        cols2[3].metric("Sentiment Down %", metrics.get('sentiment_down_pct', 'N/A'))
    else:
        st.info("No metrics available.")

# 7) Price Forecasting
with st.container():
    st.subheader("🔮 Price Forecasting")
    if model_choice == "Prophet":
        forecast_df = forecast_prophet(price_df, periods=forecast_days)
        fv = forecast_df[forecast_df['ds'] > price_df.index[-1]][['ds','yhat','yhat_lower','yhat_upper']]
    else:
        fv = forecast_lstm(price_df, periods=forecast_days)

    fig = go.Figure(layout_template="plotly_dark")
    fig.add_trace(go.Scatter(x=price_df.index, y=price_df['close'], mode='lines', name='Historical'))
    fig.add_trace(go.Scatter(x=fv['ds'], y=fv['yhat'], mode='lines', name='Forecast'))
    if model_choice == "Prophet":
        fig.add_trace(go.Scatter(x=fv['ds'], y=fv['yhat_upper'],
                                 line=dict(color='gray'), showlegend=False))
        fig.add_trace(go.Scatter(x=fv['ds'], y=fv['yhat_lower'],
                                 fill='tonexty', line=dict(color='gray'),
                                 fillcolor='rgba(128,128,128,0.2)', showlegend=False))
    fig.update_layout(
        title=f"{selected} Price Forecast ({model_choice})",
        xaxis_title="Date", yaxis_title="Price (USD)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Forecasted Prices**")
    df_disp = fv.rename(columns={
        'ds':'Date','yhat':'Forecast',
        'yhat_lower':'Lower CI','yhat_upper':'Upper CI'
    }).set_index('Date')
    st.dataframe(df_disp)

# 8) Volatility Analysis
with st.container():
    st.subheader("📊 Volatility Analysis")
    ohlc = get_historical_ohlc(coin_id, 'usd', days=90)
    vol  = compute_volatility(ohlc)
    vcols = st.columns(2)
    fig1 = go.Figure(layout_template="plotly_dark")
    fig1.add_trace(go.Scatter(x=vol.index, y=vol['rolling_std'], name='Std Dev'))
    fig1.update_layout(title="Rolling Std Dev", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    vcols[0].plotly_chart(fig1, use_container_width=True)

    fig2 = go.Figure(layout_template="plotly_dark")
    fig2.add_trace(go.Scatter(x=vol.index, y=vol['ATR'], name='ATR'))
    fig2.update_layout(title="Average True Range", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    vcols[1].plotly_chart(fig2, use_container_width=True)

# 9) Footer
st.write("---")
st.markdown(
    "© 2025 Crypto P • [cryptop.coraxgardening.se](https://cryptop.coraxgardening.se)",
    unsafe_allow_html=True
)
