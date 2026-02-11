# cryptop_crypto_fortune_teller_main.py

import streamlit as st
import logging
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import html

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
    calculate_stochastic_oscillator,
    calculate_ichimoku_cloud,
    calculate_pivot_points,
    calculate_fibonacci_levels,
    calculate_roi,
    calculate_moon_math,
    get_coin_market_cap_batch,
    get_coin_market_data,
    check_risk_level,
    generate_trading_signal,
    validate_coin_id,
    detect_candlestick_patterns,
    get_exchange_arbitrage,
    calculate_correlation_matrix,
    calculate_dca_strategy,
    detect_volume_anomalies,
    calculate_vwap,
    calculate_parabolic_sar,
    get_historical_volume
)
from modules.cryptop_crypto_fortune_teller_models import (
    forecast_general_ensemble
)
from modules.exchange_manager import ExchangeManager
from modules.freqtrade_manager import FreqtradeManager
from modules.cryptop_crypto_fortune_teller_styles import apply_custom_css

# 1) Page config
st.set_page_config(
    page_title="Crypto P's Crypto Fortune Teller",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2) Apply Custom CSS for "Awesome Design" - PSYCHEDELIC CARNIVAL THEME
apply_custom_css()

# 3) Header
logo_path = "assets/logo.png"

col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    try:
        st.image(logo_path, width=120)
    except:
        st.write("🔮") # Fallback if image missing
    st.markdown("<h1 style='text-align: center; color: #FFD700; text-shadow: 0 0 10px #FF00FF;'>🎪 Crypto P's 🔮<br>Crypto Fortune Teller</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #00FFFF; font-family: Cinzel, serif;'>✨ Peer into the Misty Future of the Blockchain ✨</h4>", unsafe_allow_html=True)

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

    display_series = df_coins['name'] + ' (' + df_coins['symbol'].str.upper() + ')'
    options = display_series.tolist()
    mapping = pd.Series(df_coins.id.values, index=display_series).to_dict()

    with st.expander("🪙 Asset Selection", expanded=True):
        selected_option = st.selectbox("Select Cryptocurrency", options, index=0, help="Search and select the cryptocurrency you want to analyze.")
        coin_id = mapping[selected_option]

        # 🛡️ Sentinel: Global Input Validation for coin_id
        if not validate_coin_id(coin_id):
            st.error("Invalid Asset ID detected. Please select a valid asset.")
            st.stop()

    with st.expander("🔮 Forecast Settings", expanded=True):
        st.markdown("### ⚙️ Model Ensemble")
        selected_models = st.multiselect(
            "Select Models to Combine",
            [
                "Prophet (Standard)",
                "Prophet (Volatile)",
                "Prophet (Conservative)",
                "LSTM",
                "ARIMA",
                "SARIMA"
            ],
            default=["Prophet (Standard)"],
            help="Combine multiple statistical and AI models for robust predictions."
        )

        forecast_days = st.slider("Forecast Horizon (Days)", 7, 365, 30, help="Predict up to 1 year into the future.")

        enhance_sentiment = st.checkbox(
            "Enhance with Community Sentiment",
            value=False,
            help="Analyze community data (Twitter/Reddit sentiment) to adjust the forecast."
        )

        with st.expander("🔧 Advanced Model Config"):
            st.write("Tune the Prophet model hyperparameters.")
            p_changepoint = st.slider("Changepoint Prior Scale", 0.001, 0.5, 0.05, step=0.001, help="Flexibility of the trend. Higher = more flexible (overfitting risk).")
            p_seasonality = st.slider("Seasonality Prior Scale", 0.01, 20.0, 10.0, step=0.1, help="Strength of seasonality.")
            p_season_mode = st.radio("Seasonality Mode", ["additive", "multiplicative"], index=0)

            model_params = {
                'changepoint_prior_scale': p_changepoint,
                'seasonality_prior_scale': p_seasonality,
                'seasonality_mode': p_season_mode
            }

    st.markdown("---")

    # Fear & Greed
    st.subheader("😱 Fear & Greed")
    fng = get_fear_and_greed_index()
    if fng:
        val = int(fng['value'])
        color = "red" if val < 40 else "green" if val > 60 else "orange"
        st.markdown(f"<h2 style='color: {html.escape(color)}; text-align: center;'>{html.escape(str(val))}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{html.escape(fng['classification'])}</p>", unsafe_allow_html=True)
    else:
        st.write("N/A")

    st.markdown("---")

    # Quick Converter
    with st.expander("💱 Quick Converter"):
        conv_amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)
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

    st.info("Note: Prediction models are for educational purposes only. Not financial advice.")

# 5) Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🔮 Forecast",
    "📊 Analysis",
    "⚖️ Compare",
    "🧪 Backtest",
    "💰 Portfolio",
    "🌍 Market",
    "🧮 Calculators",
    "🔧 Stats",
    "🔌 Connect",
    "🧙 About"
])

# --- TAB 1: FORECAST ---
with tab1:
    st.subheader(f"Price Forecast: {selected_option}")

    with st.spinner("Consulting the oracles..."):
        # Fetch sufficient history for all models (1 year min usually good, maybe 2 for seasonality)
        price_df = get_historical_prices(coin_id, 'usd', days=730)

        if price_df.empty:
            st.error("No historical data available for this coin.")
        else:
            # 1. Risk Warning
            risk_msg = check_risk_level(price_df)
            if risk_msg:
                st.warning(risk_msg)

            # 2. Sentiment Score
            s_score = 0.0
            if enhance_sentiment:
                metrics = get_coin_metrics(coin_id)
                up_pct = metrics.get('sentiment_up_pct')
                if up_pct is not None:
                    s_score = (float(up_pct) - 50.0) / 50.0
                    st.info(f"✨ Sentiment Enhancement Active! Market Sentiment is {up_pct:.1f}% Bullish. Adjustment Factor: {s_score:.2f}")
                else:
                    st.warning("Sentiment data unavailable. Proceeding with neutral sentiment.")

            if not selected_models:
                st.warning("Please select at least one model variant.")
                forecast_df = pd.DataFrame()
            else:
                forecast_df = forecast_general_ensemble(
                    price_df,
                    model_names=selected_models,
                    periods=forecast_days,
                    sentiment_score=s_score,
                    model_params=model_params
                )

            if not forecast_df.empty:
                # Generate Trading Signal
                current_p = price_df['close'].iloc[-1]
                signal, signal_color = generate_trading_signal(current_p, forecast_df)

                col_sig1, col_sig2 = st.columns([1, 3])
                with col_sig1:
                    st.markdown(f"""
                    <div style="border: 2px solid {html.escape(signal_color)}; padding: 10px; border-radius: 10px; text-align: center;">
                        <h3 style="color: {html.escape(signal_color)}; margin: 0;">{html.escape(signal)}</h3>
                        <p style="margin: 0; font-size: 0.8rem;">Trading Signal</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_sig2:
                    st.write("### AI Prediction Summary")
                    final_price = forecast_df['yhat'].iloc[-1]
                    gain_loss = ((final_price - current_p) / current_p) * 100
                    st.write(f"Projected Price in {forecast_days} days: **${final_price:,.2f}** ({gain_loss:+.2f}%)")

                # Plot
                fig = go.Figure()

                # Historical (Limit history view to last 365 days for clarity, but model used 730)
                disp_hist = price_df.iloc[-365:]
                fig.add_trace(go.Scatter(
                    x=disp_hist.index, y=disp_hist['close'],
                    mode='lines', name='History',
                    line=dict(color='#00FFFF', width=2)
                ))

                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_df['ds'], y=forecast_df['yhat'],
                    mode='lines', name='Forecast',
                    line=dict(color='#FF00FF', dash='dash', width=3)
                ))

                # Confidence Intervals if available and meaningful (not all zero/same)
                # Check if upper != lower
                if (forecast_df['yhat_upper'] != forecast_df['yhat_lower']).any():
                    fig.add_trace(go.Scatter(
                        x=forecast_df['ds'], y=forecast_df['yhat_upper'],
                        mode='lines', marker=dict(color="#444"), line=dict(width=0), showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_df['ds'], y=forecast_df['yhat_lower'],
                        marker=dict(color="#444"), line=dict(width=0), mode='lines',
                        fillcolor='rgba(255, 0, 255, 0.1)', fill='tonexty', showlegend=False
                    ))

                title_text = f"{selected_option} - Ensemble Forecast"

                fig.update_layout(
                    title=title_text,
                    xaxis_title="Date", yaxis_title="Price (USD)",
                    template="plotly_dark", height=500, hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Download Forecast Data
                csv = forecast_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Forecast CSV",
                    data=csv,
                    file_name=f'{coin_id}_forecast.csv',
                    mime='text/csv',
                )

# --- TAB 2: ANALYSIS ---
with tab2:
    st.subheader("Technical Analysis")

    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        date_opt = st.radio("Timeframe", ["90 Days", "180 Days", "1 Year", "Custom"], index=1)

        days_back = 180
        if date_opt == "90 Days": days_back = 90
        elif date_opt == "180 Days": days_back = 180
        elif date_opt == "1 Year": days_back = 365
        else:
             # Custom date range handling
             start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=180))
             days_back = (datetime.date.today() - start_date).days
             if days_back < 1: days_back = 7

    with col_ctrl2:
        st.write("Indicators & Overlays:")
        col_ind1, col_ind2, col_ind3 = st.columns(3)
        show_fib = col_ind1.checkbox("Fibonacci Levels")
        show_sma = col_ind2.checkbox("SMA Ribbon")
        show_ichi = col_ind3.checkbox("Ichimoku Cloud")
        show_stoch = col_ind1.checkbox("Stochastic Osc.")
        show_bb = col_ind2.checkbox("Bollinger Bands", value=True)
        show_pivot = col_ind3.checkbox("Pivot Points")
        show_vwap = col_ind1.checkbox("VWAP")
        show_sar = col_ind2.checkbox("Parabolic SAR")

    with st.spinner("Analyzing market patterns..."):
        # Fetch OHLC
        ohlc_df = get_historical_ohlc(coin_id, days=days_back)
        if ohlc_df.empty:
            ohlc_df = get_historical_prices(coin_id, days=days_back)
            if not ohlc_df.empty:
                ohlc_df['open'] = ohlc_df['close']
                ohlc_df['high'] = ohlc_df['close']
                ohlc_df['low'] = ohlc_df['close']

        if ohlc_df.empty:
            st.error("No data available.")
        else:
            # Calculations
            bb_df = calculate_bollinger_bands(ohlc_df) if show_bb else pd.DataFrame()
            ichi_df = calculate_ichimoku_cloud(ohlc_df) if show_ichi else pd.DataFrame()
            fib_levels = calculate_fibonacci_levels(ohlc_df) if show_fib else {}
            stoch_df = calculate_stochastic_oscillator(ohlc_df) if show_stoch else pd.DataFrame()
            pivot_points = calculate_pivot_points(ohlc_df) if show_pivot else {}

            # VWAP & SAR Logic
            vwap_series = pd.Series(dtype=float)
            if show_vwap:
                vol_df = get_historical_volume(coin_id, days=days_back)
                if not vol_df.empty:
                    # Join volume to OHLC for calculation
                    temp_df = ohlc_df.join(vol_df, how='left')
                    vwap_series = calculate_vwap(temp_df)

            sar_series = calculate_parabolic_sar(ohlc_df) if show_sar else pd.Series(dtype=float)

            # Plot 1: Main Chart
            fig_main = go.Figure()
            fig_main.add_trace(go.Candlestick(
                x=ohlc_df.index, open=ohlc_df['open'], high=ohlc_df['high'],
                low=ohlc_df['low'], close=ohlc_df['close'], name='OHLC'
            ))

            # VWAP
            if show_vwap and not vwap_series.empty:
                fig_main.add_trace(go.Scatter(x=vwap_series.index, y=vwap_series, line=dict(color='#ff9f43', width=2), name='VWAP'))

            # Parabolic SAR
            if show_sar and not sar_series.empty:
                fig_main.add_trace(go.Scatter(x=sar_series.index, y=sar_series, mode='markers', marker=dict(color='white', size=4, symbol='cross'), name='Parabolic SAR'))

            # Bollinger Bands
            if not bb_df.empty:
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Upper'], line=dict(color='#bd93f9', width=1), name='BB Upper'))
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Lower'], line=dict(color='#bd93f9', width=1), name='BB Lower', fill='tonexty', fillcolor='rgba(189, 147, 249, 0.1)'))
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['SMA'], line=dict(color='#FFD700', width=1), name='BB SMA 20'))

            # Ichimoku
            if not ichi_df.empty:
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanA'], line=dict(width=0), showlegend=False, name='Span A'))
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanB'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 255, 255, 0.1)', name='Ichimoku Cloud'))
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Tenkan'], line=dict(color='#00FFFF', width=1), name='Tenkan'))
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Kijun'], line=dict(color='#FF4500', width=1), name='Kijun'))

            # SMA Ribbon
            if show_sma:
                colors = ['#FF0000', '#FFA500', '#FFFF00', '#008000']
                for i, period in enumerate([20, 50, 100, 200]):
                    sma = ohlc_df['close'].rolling(window=period).mean()
                    fig_main.add_trace(go.Scatter(x=ohlc_df.index, y=sma, line=dict(color=colors[i], width=1), name=f'SMA {period}'))

            # Fibonacci
            if show_fib:
                for label, val in fib_levels.items():
                    fig_main.add_hline(y=val, line_dash="dot", line_color="gray", annotation_text=label)

            # Annotations (Max/Min)
            max_idx = ohlc_df['high'].idxmax()
            min_idx = ohlc_df['low'].idxmin()
            fig_main.add_annotation(x=max_idx, y=ohlc_df.loc[max_idx]['high'], text="Max", showarrow=True, arrowhead=1)
            fig_main.add_annotation(x=min_idx, y=ohlc_df.loc[min_idx]['low'], text="Min", showarrow=True, arrowhead=1)

            fig_main.update_layout(title="Price Action", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
            st.plotly_chart(fig_main, use_container_width=True)

            # Pivot Points Display
            if show_pivot and pivot_points:
                st.write("**Daily Pivot Points (Projected):**")
                cols = st.columns(7)
                cols[0].metric("S3", f"{pivot_points['S3']:.2f}")
                cols[1].metric("S2", f"{pivot_points['S2']:.2f}")
                cols[2].metric("S1", f"{pivot_points['S1']:.2f}")
                cols[3].metric("Pivot", f"{pivot_points['Pivot']:.2f}")
                cols[4].metric("R1", f"{pivot_points['R1']:.2f}")
                cols[5].metric("R2", f"{pivot_points['R2']:.2f}")
                cols[6].metric("R3", f"{pivot_points['R3']:.2f}")

            # Feature: Candlestick Pattern Recognition
            with st.expander("🕯️ AI Pattern Recognition", expanded=True):
                patterns = detect_candlestick_patterns(ohlc_df)
                if patterns:
                    st.success(f"Detected Patterns on Latest Candle: {', '.join(patterns)}")
                else:
                    st.info("No specific patterns detected on the latest candle.")

            # Sub-charts: RSI, Stoch, MACD
            st.markdown("### Indicators")

            # Stochastic
            if show_stoch and not stoch_df.empty:
                fig_stoch = go.Figure()
                fig_stoch.add_trace(go.Scatter(x=stoch_df.index, y=stoch_df['%K'], name='%K', line=dict(color='#00FFFF')))
                fig_stoch.add_trace(go.Scatter(x=stoch_df.index, y=stoch_df['%D'], name='%D', line=dict(color='#FF4500')))
                fig_stoch.add_hline(y=80, line_dash="dot", line_color="red")
                fig_stoch.add_hline(y=20, line_dash="dot", line_color="green")
                fig_stoch.update_layout(title="Stochastic Oscillator", template="plotly_dark", height=250, yaxis_range=[0, 100])
                st.plotly_chart(fig_stoch, use_container_width=True)

            col_a1, col_a2 = st.columns(2)

            with col_a1:
                rsi = calculate_rsi(ohlc_df)
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi, name='RSI', line=dict(color='#FF4500')))
                fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
                fig_rsi.update_layout(title="RSI", template="plotly_dark", height=250, yaxis_range=[0, 100])
                st.plotly_chart(fig_rsi, use_container_width=True)

            with col_a2:
                macd_df = calculate_macd(ohlc_df)
                if not macd_df.empty:
                    fig_macd = make_subplots(specs=[[{"secondary_y": False}]])
                    fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df['Histogram'], name='Hist', marker_color='#444'))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['MACD'], name='MACD', line=dict(color='#00FFFF')))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['Signal'], name='Signal', line=dict(color='#FF4500')))
                    fig_macd.update_layout(title="MACD", template="plotly_dark", height=250)
                    st.plotly_chart(fig_macd, use_container_width=True)

            # Export Data
            st.download_button(
                label="📥 Download Historical Data CSV",
                data=ohlc_df.to_csv().encode('utf-8'),
                file_name=f'{coin_id}_history.csv',
                mime='text/csv',
            )

# --- TAB 3: COMPARE ---
with tab3:
    st.subheader("⚖️ Asset Comparison")
    st.write("Compare the performance of multiple assets over time.")

    comp_coins = st.multiselect("Select Assets to Compare", options, default=[options[0], "Bitcoin (BTC)"] if "Bitcoin (BTC)" in options else [options[0]])
    comp_days = st.selectbox("Duration", [30, 90, 180, 365, 730], index=1)

    if comp_coins:
        with st.spinner("Fetching data..."):
            comp_ids = [mapping[c] for c in comp_coins]
            comp_df = get_batch_historical_prices(comp_ids, days=comp_days)

            if not comp_df.empty:
                # Normalize to 100 (Percentage Change)
                norm_df = (comp_df / comp_df.iloc[0]) * 100

                fig_comp = go.Figure()
                for col in norm_df.columns:
                    # Find symbol name for legend
                    sym = [k for k, v in mapping.items() if v == col][0]
                    fig_comp.add_trace(go.Scatter(x=norm_df.index, y=norm_df[col], name=sym, mode='lines'))

                fig_comp.update_layout(
                    title=f"Relative Performance (Base=100) - {comp_days} Days",
                    xaxis_title="Date",
                    yaxis_title="Normalized Price",
                    template="plotly_dark",
                    hovermode="x unified"
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                # Feature: Correlation Matrix
                st.markdown("### 🔗 Correlation Matrix")
                with st.spinner("Calculating correlations..."):
                    corr_matrix = calculate_correlation_matrix(comp_ids, days=comp_days)
                    if not corr_matrix.empty:
                        fig_corr = px.imshow(
                            corr_matrix,
                            text_auto=True,
                            aspect="auto",
                            color_continuous_scale='RdBu_r',
                            title=f"Correlation Heatmap ({comp_days} days)"
                        )
                        fig_corr.update_layout(template="plotly_dark")
                        st.plotly_chart(fig_corr, use_container_width=True)

            else:
                st.error("No data available for selected coins.")
    else:
        st.info("Select at least one asset to display.")

# --- TAB 4: BACKTEST ---
with tab4:
    st.subheader("🧪 Strategy Backtester")

    col_bt1, col_bt2 = st.columns(2)
    with col_bt1:
        strategy = st.selectbox("Strategy", ["SMA Crossover", "RSI Mean Reversion"])
    with col_bt2:
        bt_days = st.selectbox("Backtest Period", [180, 365, 730], index=1)

    if st.button("Run Backtest"):
        with st.spinner("Simulating..."):
            bt_data = get_historical_prices(coin_id, days=bt_days)
            if not bt_data.empty:
                res_df, metrics = calculate_backtest(bt_data, strategy_type=strategy)

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Return", f"{metrics['Total Return']:.2%}", delta_color="normal")
                m2.metric("Market Return", f"{metrics['Market Return']:.2%}", delta_color="normal")
                alpha = metrics['Total Return'] - metrics['Market Return']
                m3.metric("Alpha", f"{alpha:.2%}", delta=f"{alpha:.2%}")

                fig_bt = go.Figure()
                fig_bt.add_trace(go.Scatter(x=res_df.index, y=res_df['cumulative_market_returns'], name='Buy & Hold', line=dict(dash='dot')))
                fig_bt.add_trace(go.Scatter(x=res_df.index, y=res_df['cumulative_strategy_returns'], name='Strategy', line=dict(color='#00FF00', width=2)))
                fig_bt.update_layout(title="Equity Curve", template="plotly_dark", yaxis_title="Growth Factor")
                st.plotly_chart(fig_bt, use_container_width=True)
            else:
                st.error("Backtest failed.")

# --- TAB 5: PORTFOLIO ---
with tab5:
    st.subheader("💰 Portfolio Tracker")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    with st.expander("Add Asset", expanded=False):
        with st.form("add_asset_form"):
            p_coin = st.selectbox("Coin", options)
            p_amount = st.number_input("Amount", min_value=0.0, step=0.01)
            p_buy_price = st.number_input("Avg Buy Price ($)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add")

            if submitted:
                p_coin_id = mapping[p_coin]
                p_symbol = p_coin.split('(')[1].replace(')', '')
                st.session_state.portfolio.append({
                    'id': p_coin_id, 'name': p_coin, 'symbol': p_symbol,
                    'amount': p_amount, 'buy_price': p_buy_price
                })
                st.success(f"Added {p_amount} {p_symbol}")

    if st.session_state.portfolio:
        # Calculate
        port_data = []
        total_val = 0
        total_cost = 0

        p_ids = list(set([i['id'] for i in st.session_state.portfolio]))
        curr_prices = get_current_price(p_ids)

        for item in st.session_state.portfolio:
            cid = item['id']
            c_price = curr_prices.get(cid, {}).get('usd', 0) if curr_prices else 0
            val = item['amount'] * c_price
            cost = item['amount'] * item['buy_price']
            pnl = val - cost
            pnl_pct = (pnl / cost * 100) if cost > 0 else 0

            total_val += val
            total_cost += cost

            port_data.append({
                'Coin': item['name'], 'Amount': item['amount'],
                'Price': c_price, 'Value': val,
                'PnL ($)': pnl, 'PnL (%)': pnl_pct
            })

        df_port = pd.DataFrame(port_data)

        # Best/Worst Performer
        best_perf = df_port.loc[df_port['PnL (%)'].idxmax()]
        worst_perf = df_port.loc[df_port['PnL (%)'].idxmin()]

        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Total Value", f"${total_val:,.2f}")
        tpnl = total_val - total_cost
        tpnl_pct = (tpnl/total_cost*100) if total_cost>0 else 0
        col_p2.metric("Total PnL", f"${tpnl:,.2f}", delta=f"{tpnl_pct:.2f}%")
        col_p3.metric("Top Asset", best_perf['Coin'], delta=f"{best_perf['PnL (%)']:.2f}%")

        st.dataframe(df_port.style.format({'Price': "${:.2f}", 'Value': "${:.2f}", 'PnL ($)': "${:.2f}", 'PnL (%)': "{:.2f}%"}))

        fig_pie = px.pie(df_port, values='Value', names='Coin', title='Allocation', hole=0.3)
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

        if st.button("Clear Portfolio"):
            st.session_state.confirm_clear_portfolio = True

        if st.session_state.get('confirm_clear_portfolio'):
            st.warning("⚠️ Are you sure you want to clear your entire portfolio? This action cannot be undone.")
            col_conf_yes, col_conf_no = st.columns(2)
            with col_conf_yes:
                if st.button("Yes, Clear Everything", type="primary"):
                    st.session_state.portfolio = []
                    st.session_state.confirm_clear_portfolio = False
                    st.experimental_rerun()
            with col_conf_no:
                if st.button("Cancel"):
                    st.session_state.confirm_clear_portfolio = False
                    st.experimental_rerun()

        # Future Wealth Projection
        st.markdown("---")
        st.subheader("🔮 Future Wealth Projection")
        st.write("Estimate the future value of your assets based on AI forecasts (30-day horizon).")

        port_options = list(set([item['name'] for item in st.session_state.portfolio]))
        if port_options:
            selected_port_asset = st.selectbox("Select Asset to Project", port_options, key="port_forecast_select")

            # Find asset details (sum amount if multiple entries)
            # Simple approach: sum amount for this coin
            total_amt = sum([i['amount'] for i in st.session_state.portfolio if i['name'] == selected_port_asset])
            asset_id = next((i['id'] for i in st.session_state.portfolio if i['name'] == selected_port_asset), None)

            if asset_id and total_amt > 0:
                with st.spinner(f"Projecting value for {selected_port_asset}..."):
                     # Fetch history
                     p_hist = get_historical_prices(asset_id, days=365)
                     if not p_hist.empty:
                         # Forecast 30 days using Standard Prophet
                         p_forecast = forecast_general_ensemble(p_hist, ["Prophet (Standard)"], periods=30)

                         if not p_forecast.empty:
                             current_price = p_hist['close'].iloc[-1]
                             current_val = total_amt * current_price
                             future_price = p_forecast['yhat'].iloc[-1]
                             future_val = total_amt * future_price

                             gain_pct = ((future_val - current_val) / current_val) * 100 if current_val > 0 else 0

                             c_fw1, c_fw2 = st.columns(2)
                             c_fw1.metric("Current Value", f"${current_val:,.2f}")
                             c_fw2.metric("Projected Value (30 Days)", f"${future_val:,.2f}", delta=f"{gain_pct:.2f}%")

                             # Plot
                             fig_fw = go.Figure()
                             # History (Last 30 days)
                             disp_hist = p_hist.iloc[-30:]
                             fig_fw.add_trace(go.Scatter(x=disp_hist.index, y=disp_hist['close'] * total_amt, name='History', line=dict(color='cyan')))
                             # Forecast
                             fig_fw.add_trace(go.Scatter(x=p_forecast['ds'], y=p_forecast['yhat'] * total_amt, name='Forecast', line=dict(color='magenta', dash='dash')))

                             # Confidence
                             if 'yhat_upper' in p_forecast.columns:
                                 fig_fw.add_trace(go.Scatter(x=p_forecast['ds'], y=p_forecast['yhat_upper'] * total_amt, showlegend=False, line=dict(width=0)))
                                 fig_fw.add_trace(go.Scatter(x=p_forecast['ds'], y=p_forecast['yhat_lower'] * total_amt, fill='tonexty', showlegend=False, line=dict(width=0), fillcolor='rgba(255,0,255,0.1)'))

                             fig_fw.update_layout(title=f"Projected Value: {selected_port_asset}", template="plotly_dark", height=350, hovermode="x unified")
                             st.plotly_chart(fig_fw, use_container_width=True)
                         else:
                             st.warning("Forecast model returned no data.")
                     else:
                         st.warning("Insufficient historical data for projection.")

    else:
        st.info("Portfolio empty.")

# --- TAB 6: MARKET ---
with tab6:
    st.subheader("🌍 Market Overview")

    st.write("### 🏆 Top 50 Cryptocurrencies by Market Cap")
    with st.spinner("Fetching global market data..."):
        df_mkt = get_coin_market_cap_batch(limit=50)

        if not df_mkt.empty:
            # Treemap
            fig_tree = px.treemap(
                df_mkt, path=['symbol'], values='market_cap',
                color='price_change_percentage_24h',
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0,
                hover_data=['name', 'current_price', 'price_change_percentage_24h'],
                title="Market Cap Visualization (Color = 24h Change)"
            )
            fig_tree.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig_tree, use_container_width=True)

            with st.expander("View Market Data Table"):
                st.dataframe(df_mkt.style.format({'current_price': "${:.2f}", 'market_cap': "${:,.0f}"}))
        else:
            st.error("Could not load market data.")

    st.markdown("---")
    st.write("### 🌐 Global Arbitrage Scanner")
    arb_symbol = st.text_input("Enter Symbol for Arbitrage Check (e.g., BTC/USDT)", "BTC/USDT")
    if st.button("Scan Exchanges"):
        with st.spinner(f"Scanning exchanges for {arb_symbol}..."):
            arb_df = get_exchange_arbitrage(arb_symbol)
            if not arb_df.empty:
                st.dataframe(arb_df.style.format({'Price': "${:,.2f}", 'Spread %': "{:.2f}%"}))

                best_price = arb_df['Price'].max()
                best_ex = arb_df.loc[arb_df['Price'].idxmax()]['Exchange']
                worst_price = arb_df['Price'].min()
                worst_ex = arb_df.loc[arb_df['Price'].idxmin()]['Exchange']

                profit_pct = ((best_price - worst_price) / worst_price) * 100
                st.success(f"💎 Arbitrage Opportunity: Buy on **{worst_ex}** (${worst_price:,.2f}), Sell on **{best_ex}** (${best_price:,.2f}). Potential Profit: **{profit_pct:.2f}%**")
            else:
                st.warning("Could not fetch arbitrage data. Check symbol or API limits.")

# --- TAB 7: CALCULATORS ---
with tab7:
    st.subheader("🧮 Crypto Calculators")

    c_tab1, c_tab2, c_tab3, c_tab4 = st.tabs(["If I Invested...", "Moon Math", "Risk/Reward", "DCA Time Machine"])

    with c_tab1:
        st.write("#### 💸 If I Invested...")
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            inv_amount = st.number_input("Investment Amount ($)", 100, 10000, 1000, help="The initial amount in USD you want to simulate investing.")
            inv_date = st.date_input("On Date", datetime.date.today() - datetime.timedelta(days=365), help="The past date when you would have made this investment.")

        if st.button("Calculate ROI"):
            with st.spinner("Calculating ROI..."):
                # Fetch price on that date
                # We need to use history function roughly
                days_diff = (datetime.date.today() - inv_date).days
                if days_diff < 1:
                    st.warning("Date must be in the past.")
                else:
                    hist = get_historical_prices(coin_id, days=days_diff+5) # Buffer
                    if not hist.empty:
                        # Find closest date
                        closest_idx = hist.index.searchsorted(pd.Timestamp(inv_date))
                        if closest_idx < len(hist):
                            past_price = hist.iloc[closest_idx]['close']
                            curr_p = get_current_price(coin_id).get(coin_id, {}).get('usd', 0)

                            val, pct = calculate_roi(inv_amount, past_price, curr_p)
                            st.metric("Current Value", f"${val:,.2f}", delta=f"{pct:.2f}%")
                            st.write(f"Price then: ${past_price:,.2f} | Price now: ${curr_p:,.2f}")
                        else:
                            st.error("Date out of range.")
                    else:
                        st.error("Data unavailable.")

    with c_tab2:
        st.write("#### 🚀 Moon Math")
        st.write(f"Calculate the price of **{selected_option}** if it hits a target Market Cap.")

        mc_target_input = st.number_input("Target Market Cap ($)", value=1_000_000_000.0, step=1_000_000.0, help="Enter a hypothetical market cap (e.g., Bitcoin's market cap) to see what the coin price would be.")

        if st.button("Calculate Moon Price"):
            with st.spinner("Crunching the numbers..."):
                try:
                    # 🛡️ Sentinel: Input Validation for coin_id to prevent injection
                    # (Redundant due to global check, but kept for defense in depth)
                    if not validate_coin_id(coin_id):
                         st.error("Invalid Asset ID.")
                         st.stop()

                    market_data = get_coin_market_data(coin_id)
                    supply = market_data.get('circulating_supply')
                    curr_p = market_data.get('current_price')

                    if supply and curr_p is not None:
                        t_price, upside = calculate_moon_math(curr_p, supply, mc_target_input)
                        st.metric("Target Price", f"${t_price:,.4f}", delta=f"{upside:.2f}%")
                        st.write(f"Circulating Supply: {supply:,.0f}")
                    else:
                        st.error("Could not fetch supply data.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with c_tab3:
        st.write("#### ⚖️ Risk/Reward Calculator")
        col_r1, col_r2, col_r3 = st.columns(3)
        entry = col_r1.number_input("Entry Price", value=0.0, help="The price at which you plan to buy (or bought) the asset.")
        stop = col_r2.number_input("Stop Loss", value=0.0, help="The price at which you will sell to limit your loss.")
        target = col_r3.number_input("Take Profit", value=0.0, help="The price at which you will sell to take your profit.")

        if entry > 0 and stop > 0 and target > 0:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            rr = reward / risk if risk > 0 else 0

            st.metric("Risk / Reward Ratio", f"1 : {rr:.2f}")
            if rr >= 2:
                st.success("Good R:R Ratio!")
            elif rr < 1:
                st.warning("Poor R:R Ratio.")

    with c_tab4:
        st.write("#### ⏳ Dollar Cost Averaging (DCA) Time Machine")
        st.write("Simulate a recurring investment strategy vs. Lump Sum.")

        col_dca1, col_dca2, col_dca3 = st.columns(3)
        dca_amount = col_dca1.number_input("Recurring Amount ($)", 10, 10000, 100)
        dca_freq = col_dca2.number_input("Frequency (Days)", 1, 30, 7)
        dca_duration = col_dca3.number_input("Duration (Days)", 30, 1825, 365)

        if st.button("Run DCA Simulation"):
            with st.spinner("Travelling through time..."):
                dca_res = calculate_dca_strategy(coin_id, dca_amount, dca_freq, dca_duration)
                if dca_res:
                    st.metric("Total Invested", f"${dca_res['total_invested']:,.2f}")

                    c_dca_a, c_dca_b = st.columns(2)
                    dca_val = dca_res['dca_value']
                    lump_val = dca_res['lump_value']

                    dca_gain = ((dca_val - dca_res['total_invested']) / dca_res['total_invested']) * 100
                    lump_gain = ((lump_val - dca_res['total_invested']) / dca_res['total_invested']) * 100

                    c_dca_a.metric("DCA Final Value", f"${dca_val:,.2f}", delta=f"{dca_gain:.2f}%")
                    c_dca_b.metric("Lump Sum Value", f"${lump_val:,.2f}", delta=f"{lump_gain:.2f}%")

                    # Plot
                    hist_df = dca_res['history_df']
                    fig_dca = go.Figure()
                    fig_dca.add_trace(go.Scatter(x=hist_df.index, y=hist_df['value'], name='DCA Value', fill='tozeroy'))
                    fig_dca.add_trace(go.Scatter(x=hist_df.index, y=hist_df['invested'], name='Invested', line=dict(dash='dot')))
                    fig_dca.update_layout(title="DCA Portfolio Growth", template="plotly_dark")
                    st.plotly_chart(fig_dca, use_container_width=True)
                else:
                    st.error("Simulation failed. Check data availability.")

# --- TAB 8: STATS ---
with tab8:
    st.subheader("📊 Advanced Statistics")

    vol_ohlc = get_historical_ohlc(coin_id, days=180)
    if not vol_ohlc.empty:
        vol_metrics = compute_volatility(vol_ohlc)

        fig_vol = make_subplots(specs=[[{"secondary_y": True}]])
        fig_vol.add_trace(go.Scatter(x=vol_metrics.index, y=vol_metrics['rolling_std'], name='Vol (StdDev)', line=dict(color='#FF00FF')), secondary_y=False)
        fig_vol.add_trace(go.Scatter(x=vol_metrics.index, y=vol_metrics['ATR'], name='ATR', line=dict(color='#00FFFF', dash='dot')), secondary_y=True)
        fig_vol.update_layout(title="Volatility (180d)", template="plotly_dark", height=400)
        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("---")
    st.subheader("🐋 Whale Sonar (Volume Anomalies)")
    st.write("Detects days with unusual volume spikes (> 2x average).")

    anomalies = detect_volume_anomalies(coin_id, days=180)
    if not anomalies.empty:
        st.warning(f"Detected {len(anomalies)} volume anomalies in the last 180 days.")
        st.dataframe(anomalies.style.format({'volume': "{:,.0f}", 'vol_ma': "{:,.0f}"}))

        # Plot volume with markers
        fig_whale = go.Figure()
        fig_whale.add_trace(go.Bar(x=anomalies.index, y=anomalies['volume'], name='Whale Spike', marker_color='red'))
        fig_whale.update_layout(title="Volume Spikes", template="plotly_dark", height=300)
        st.plotly_chart(fig_whale, use_container_width=True)
    else:
        st.success("No significant volume anomalies detected recently.")

    st.markdown("---")
    metrics = get_coin_metrics(coin_id)
    if metrics:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Twitter", metrics.get('twitter_followers', 'N/A'))
        c2.metric("Reddit", metrics.get('reddit_subscribers', 'N/A'))
        c3.metric("GitHub Stars", metrics.get('stars', 'N/A'))
        c4.metric("Forks", metrics.get('forks', 'N/A'))
        st.json(metrics, expanded=False)

# --- TAB 9: CONNECT ---
with tab9:
    st.subheader("🔌 Exchange & Bot Connectivity")

    con_mode = st.radio("Connection Type", ["🏛️ Exchanges", "🤖 Freqtrade"], horizontal=True)

    # === Exchange Integration ===
    if con_mode == "🏛️ Exchanges":
        st.write("### Connect to Crypto Exchanges")
        st.info("Supports: Bitget, Gate, Bybit, OKX, KuCoin, Binance")

        # Session State for Exchange
        if 'exchange_client' not in st.session_state:
            st.session_state.exchange_client = ExchangeManager()
        if 'exchange_connected' not in st.session_state:
            st.session_state.exchange_connected = False

        # Connection Form
        with st.expander("🔑 API Credentials", expanded=not st.session_state.exchange_connected):
            with st.form("exchange_connect_form"):
                ex_name = st.selectbox("Exchange", ["Bitget", "Gate.io", "Bybit", "OKX", "KuCoin", "Binance"])
                ex_key = st.text_input("API Key", type="password")
                ex_secret = st.text_input("API Secret", type="password")
                ex_pass = st.text_input("Passphrase (if needed)", type="password", help="Required for OKX, KuCoin, Bitget")

                submitted_ex = st.form_submit_button("Connect")

                if submitted_ex:
                    # Normalize name for CCXT
                    ex_id_map = {
                        "Bitget": "bitget", "Gate.io": "gate", "Bybit": "bybit",
                        "OKX": "okx", "KuCoin": "kucoin", "Binance": "binance"
                    }
                    target_ex = ex_id_map[ex_name]

                    success, msg = st.session_state.exchange_client.connect(target_ex, ex_key, ex_secret, ex_pass)
                    if success:
                        st.session_state.exchange_connected = True
                        st.session_state.connected_exchange_name = ex_name
                        st.success(msg)
                    else:
                        st.error(msg)

        if st.session_state.exchange_connected:
            st.success(f"Connected to {st.session_state.connected_exchange_name} ✅")

            if st.button("Disconnect"):
                st.session_state.exchange_connected = False
                st.session_state.exchange_client = ExchangeManager()
                st.experimental_rerun()

            # Balance
            st.write("#### 💰 Wallet Balance")
            if st.button("Refresh Balance"):
                pass

            bal_df, bal_err = st.session_state.exchange_client.get_balance()
            if bal_df is not None and not bal_df.empty:
                st.dataframe(bal_df)
                # Pie chart of assets
                fig_bal = px.pie(bal_df, values='Total', names='Currency', title='Asset Allocation')
                fig_bal.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig_bal, use_container_width=True)
            elif bal_err:
                st.error(bal_err)
            else:
                st.info("Balance is empty.")

            # Trading Interface
            st.markdown("---")
            st.write("#### 📉 Trade Execution")

            col_t1, col_t2 = st.columns(2)

            with col_t1:
                t_symbol = st.text_input("Symbol (e.g., BTC/USDT)", "BTC/USDT").upper()
                t_type = st.selectbox("Order Type", ["Limit", "Market"])
                t_side = st.selectbox("Side", ["Buy", "Sell"])

            with col_t2:
                t_amount = st.number_input("Amount", min_value=0.0, step=0.001, format="%.6f")
                t_price = st.number_input("Price (USD)", min_value=0.0, step=0.01) if t_type == "Limit" else None

            if st.button("Place Order", type="primary"):
                if t_amount > 0:
                    with st.spinner("Placing order..."):
                        order, ord_msg = st.session_state.exchange_client.create_order(
                            t_symbol, t_type.lower(), t_side.lower(), t_amount, t_price
                        )
                        if order:
                            st.success(ord_msg)
                            st.json(order)
                        else:
                            st.error(ord_msg)
                else:
                    st.warning("Amount must be greater than 0")

            # Open Orders
            st.markdown("---")
            with st.expander("Open Orders"):
                if st.button("Refresh Orders"):
                    pass
                orders_df, ord_err = st.session_state.exchange_client.fetch_open_orders(t_symbol)
                if orders_df is not None and not orders_df.empty:
                    st.dataframe(orders_df)
                elif ord_err:
                    st.error(ord_err)
                else:
                    st.info("No open orders.")

    # === Freqtrade Integration ===
    elif con_mode == "🤖 Freqtrade":
        st.write("### 🤖 Freqtrade Bot Controller")

        # Session State for Freqtrade
        if 'ft_client' not in st.session_state:
            st.session_state.ft_client = None
        if 'ft_connected' not in st.session_state:
            st.session_state.ft_connected = False

        # Login Form
        with st.expander("🔌 Bot Configuration", expanded=not st.session_state.ft_connected):
            with st.form("ft_login_form"):
                ft_url = st.text_input("API URL", "http://127.0.0.1:8080")
                ft_user = st.text_input("Username", "freqtrader")
                ft_pass = st.text_input("Password", type="password")

                submitted_ft = st.form_submit_button("Connect Bot")

                if submitted_ft:
                    client = FreqtradeManager(ft_url, ft_user, ft_pass)
                    # Try login
                    success, msg = client.login()
                    if success:
                        st.session_state.ft_client = client
                        st.session_state.ft_connected = True
                        st.success(msg)
                    else:
                        st.error(msg)

        if st.session_state.ft_connected:
            st.success("Freqtrade Connected 🤖")

            client = st.session_state.ft_client

            # Controls
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                if st.button("▶️ Start Bot"):
                    res, msg = client.start_bot()
                    if res: st.success(msg)
                    else: st.error(msg)
            with col_c2:
                if st.button("⏹️ Stop Bot"):
                    res, msg = client.stop_bot()
                    if res: st.warning(msg)
                    else: st.error(msg)
            with col_c3:
                if st.button("🔄 Refresh Status"):
                    pass

            # Status Dashboard
            status, err = client.get_status()
            if status:
                st.metric("State", status.get('state', 'Unknown'))
            elif err:
                st.error(err)

            # Profit
            st.write("#### 📈 Performance")
            profit, p_err = client.get_profit()
            if profit:
                p_col1, p_col2, p_col3 = st.columns(3)
                p_col1.metric("Total Profit %", f"{profit.get('profit_all_coin', 0):.2f}%")
                p_col2.metric("Total Profit (USDT)", f"{profit.get('profit_total_usdt', 0):.2f}")
                p_col3.metric("Trade Count", profit.get('trade_count', 0))
            elif p_err:
                st.error(p_err)

            # Whitelist
            with st.expander("📜 Whitelist"):
                wl, wl_err = client.get_whitelist()
                if wl:
                    st.write(wl)
                elif wl_err:
                    st.error(wl_err)

# --- TAB 10: ABOUT ---
with tab10:
    st.markdown("""
    <div style='text-align: center;'>
        <h2>🧙 The Oracle Speaks 🧙</h2>
        <p style='font-size: 1.2rem; font-family: Cinzel, serif; color: #00FFFF;'>
            Welcome to the upgraded Crypto Fortune Teller v3.0!
        </p>
    </div>

    ### 🌟 New Features & Enhancements
    1.  **Grand Ensemble Forecasting:** Combine Prophet (3 variants), LSTM, ARIMA, and SARIMA models for the ultimate prediction engine.
    2.  **Long-Term Vision:** Forecast up to 365 days into the future.
    3.  **Risk Intelligence:** Automatic volatility detection and warnings.
    4.  **Actionable Signals:** Clear BUY/SELL trading signals based on AI projections.
    5.  **Sentiment Enhancement:** Enhance forecasts with real-time community sentiment data.
    6.  **Market Cap Treemap:** Visualize the entire market in one glance.
    7.  **Multi-Asset Comparison:** Compare performance of up to 5 coins side-by-side.
    8.  **Advanced Indicators:** Ichimoku Cloud, Stochastic, Pivot Points, SMA Ribbons.
    9.  **Calculators:** ROI, Moon Math, and Risk/Reward tools.
    10. **AI Pattern Recognition:** Detect candlestick patterns (Hammer, Engulfing, etc.).
    11. **Arbitrage Scanner:** Scan global exchanges for price differences.
    12. **Correlation Matrix:** Visualize asset correlations for diversification.
    13. **DCA Time Machine:** Backtest Dollar Cost Averaging strategies.
    14. **Whale Sonar:** Detect unusual volume spikes.

    ---
    *Disclaimer: This tool is for entertainment and educational purposes only. The future is always in flux.*

    <div style='text-align: center; margin-top: 20px;'>
        <p>© 2025 Crypto P • The Digital Mystic</p>
    </div>
    """, unsafe_allow_html=True)
