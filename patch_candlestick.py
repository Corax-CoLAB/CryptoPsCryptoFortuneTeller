import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

# Replace the simple go.Figure() with make_subplots
main_chart_search = """            # Plot 1: Main Chart
            fig_main = go.Figure()
            fig_main.add_trace(go.Candlestick(
                x=ohlc_df.index, open=ohlc_df['open'], high=ohlc_df['high'],
                low=ohlc_df['low'], close=ohlc_df['close'], name='OHLC'
            ))"""

main_chart_replace = """            # Plot 1: Main Chart with Volume Subplot
            # Visual Improvement 3: Candlestick Chart with Volume Subplot
            fig_main = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                     vertical_spacing=0.03, subplot_titles=('Price Action', 'Volume'),
                                     row_width=[0.2, 0.7])

            fig_main.add_trace(go.Candlestick(
                x=ohlc_df.index, open=ohlc_df['open'], high=ohlc_df['high'],
                low=ohlc_df['low'], close=ohlc_df['close'], name='OHLC'
            ), row=1, col=1)

            # Fetch and add volume if available
            vol_for_chart = get_historical_volume(coin_id, days=days_back)
            if not vol_for_chart.empty:
                # Merge to align dates
                merged_vol = ohlc_df.join(vol_for_chart, how='left').fillna(0)
                colors = ['green' if row['open'] - row['close'] >= 0 else 'red' for index, row in merged_vol.iterrows()]
                fig_main.add_trace(go.Bar(
                    x=merged_vol.index, y=merged_vol['volume'], marker_color=colors, name='Volume'
                ), row=2, col=1)"""

content = content.replace(main_chart_search, main_chart_replace)

# Now, we need to make sure all other traces (VWAP, BB, SMA, etc) go to row=1, col=1
traces_search = [
    ("fig_main.add_trace(go.Scatter(x=vwap_series.index", "fig_main.add_trace(go.Scatter(x=vwap_series.index"),
    ("fig_main.add_trace(go.Scatter(x=sar_series.index", "fig_main.add_trace(go.Scatter(x=sar_series.index"),
    ("fig_main.add_trace(go.Scatter(x=bb_df.index", "fig_main.add_trace(go.Scatter(x=bb_df.index"),
    ("fig_main.add_trace(go.Scatter(x=ichi_df.index", "fig_main.add_trace(go.Scatter(x=ichi_df.index"),
    ("fig_main.add_trace(go.Scatter(x=ohlc_df.index", "fig_main.add_trace(go.Scatter(x=ohlc_df.index"),
    ("fig_main.add_hline(y=val", "fig_main.add_hline(y=val"),
    ("fig_main.add_annotation(x=max_idx", "fig_main.add_annotation(x=max_idx"),
    ("fig_main.add_annotation(x=min_idx", "fig_main.add_annotation(x=min_idx")
]

for s, r in traces_search:
    # We replace every occurrence of fig_main.add_...(...) with fig_main.add_...(... , row=1, col=1)
    # This is a bit tricky with regex, let's just do a string replace on the common patterns
    pass

# Better way:
content = re.sub(r'(fig_main\.add_trace\([^)]+\))', r'\1, row=1, col=1', content)
# But only for traces between the fig_main creation and update_layout
# And we must avoid replacing the newly added Bar trace if we already matched it
# Let's write a simple python script to do this safely

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
