import re

with open("streamlit_app/modules/cryptop_crypto_circus_helper.py", "r") as f:
    content = f.read()

# Add VWAP logic to backtest
vwap_strategy = """    elif strategy_type == 'VWAP Reversion':
        # Buy when price dips 5% below VWAP, Sell when price crosses above VWAP
        # Technical Improvement 4: VWAP Reversion Strategy
        vwap = calculate_vwap(df)
        if not vwap.empty:
            df['vwap'] = vwap
            signal_series = pd.Series(np.nan, index=df.index)
            # Threshold: 5% below VWAP
            buy_threshold = df['vwap'] * 0.95
            signal_series[df['close'] < buy_threshold] = 1.0
            signal_series[df['close'] > df['vwap']] = 0.0
            # Forward fill
            signal_series = signal_series.ffill().fillna(0.0)
"""

if "'VWAP Reversion'" not in content:
    content = content.replace("    elif strategy_type == 'MACD Crossover':", vwap_strategy + "\n    elif strategy_type == 'MACD Crossover':")

with open("streamlit_app/modules/cryptop_crypto_circus_helper.py", "w") as f:
    f.write(content)

# Update Main App UI
with open("streamlit_app/cryptop_crypto_circus_main.py", "r") as f:
    main_content = f.read()

main_content = main_content.replace(
    '["SMA Crossover", "RSI Mean Reversion", "Bollinger Band Squeeze", "MACD Crossover"]',
    '["SMA Crossover", "RSI Mean Reversion", "Bollinger Band Squeeze", "MACD Crossover", "VWAP Reversion"]'
)

with open("streamlit_app/cryptop_crypto_circus_main.py", "w") as f:
    f.write(main_content)

print("VWAP Backtest Strategy Added")
