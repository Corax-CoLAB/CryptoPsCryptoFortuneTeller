import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

# I removed all row=1, col=1 above. Now let's carefully add them back ONLY ONCE where needed.
traces_to_fix = [
    "fig_main.add_trace(go.Scatter(x=vwap_series.index, y=vwap_series, line=dict(color='#ff9f43', width=2), name='VWAP')",
    "fig_main.add_trace(go.Scatter(x=sar_series.index, y=sar_series, mode='markers', marker=dict(color='white', size=4, symbol='cross'), name='Parabolic SAR')",
    "fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Upper'], line=dict(color='#bd93f9', width=1), name='BB Upper')",
    "fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Lower'], line=dict(color='#bd93f9', width=1), name='BB Lower', fill='tonexty', fillcolor='rgba(189, 147, 249, 0.1)')",
    "fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['SMA'], line=dict(color='#FFD700', width=1), name='BB SMA 20')",
    "fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanA'], line=dict(width=0), showlegend=False, name='Span A')",
    "fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanB'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 255, 255, 0.1)', name='Ichimoku Cloud')",
    "fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Tenkan'], line=dict(color='#00FFFF', width=1), name='Tenkan')",
    "fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Kijun'], line=dict(color='#FF4500', width=1), name='Kijun')",
    "fig_main.add_trace(go.Scatter(x=ohlc_df.index, y=sma, line=dict(color=colors[i], width=1), name=f'SMA {period}')",
    "fig_main.add_hline(y=val, line_dash=\"dot\", line_color=\"gray\", annotation_text=label",
    "fig_main.add_annotation(x=max_idx, y=ohlc_df.loc[max_idx]['high'], text=\"Max\", showarrow=True, arrowhead=1",
    "fig_main.add_annotation(x=min_idx, y=ohlc_df.loc[min_idx]['low'], text=\"Min\", showarrow=True, arrowhead=1"
]

for t in traces_to_fix:
    content = content.replace(t + ")", t + ", row=1, col=1)")

# The Bar chart needs row=2, col=1
bar_trace = "fig_main.add_trace(go.Bar(\n                    x=merged_vol.index, y=merged_vol['volume'], marker_color=colors, name='Volume'\n                ))"
content = content.replace(bar_trace, bar_trace.replace("))", "), row=2, col=1)"))

# The candlestick needs row=1, col=1
candlestick_trace = """            fig_main.add_trace(go.Candlestick(
                x=ohlc_df.index, open=ohlc_df['open'], high=ohlc_df['high'],
                low=ohlc_df['low'], close=ohlc_df['close'], name='OHLC'
            ))"""
content = content.replace(candlestick_trace, candlestick_trace.replace("))", "), row=1, col=1)"))

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
