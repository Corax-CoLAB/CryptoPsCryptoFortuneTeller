import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

# Let's fix the regex to be more specific, and only match the traces that should be on row 1
# Actually, since I ran the previous script and it just read/wrote the same content, let's do it cleanly

search = """            # Plot 1: Main Chart
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

            fig_main.update_layout(title="Price Action", template="plotly_dark", xaxis_rangeslider_visible=False, height=600)"""

replace = """            # Plot 1: Main Chart with Volume Subplot
            # Visual Improvement 3: Candlestick Chart with Volume Subplot
            fig_main = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                     vertical_spacing=0.03, subplot_titles=('Price Action', 'Volume'),
                                     row_width=[0.2, 0.7])

            fig_main.add_trace(go.Candlestick(
                x=ohlc_df.index, open=ohlc_df['open'], high=ohlc_df['high'],
                low=ohlc_df['low'], close=ohlc_df['close'], name='OHLC'
            ), row=1, col=1)

            # Add volume subplot
            vol_for_chart = get_historical_volume(coin_id, days=days_back)
            if not vol_for_chart.empty:
                # Align dates
                merged_vol = ohlc_df.join(vol_for_chart, how='left').fillna(0)
                colors = ['green' if row['open'] - row['close'] <= 0 else 'red' for index, row in merged_vol.iterrows()]
                fig_main.add_trace(go.Bar(
                    x=merged_vol.index, y=merged_vol['volume'], marker_color=colors, name='Volume'
                ), row=2, col=1)

            # VWAP
            if show_vwap and not vwap_series.empty:
                fig_main.add_trace(go.Scatter(x=vwap_series.index, y=vwap_series, line=dict(color='#ff9f43', width=2), name='VWAP'), row=1, col=1)

            # Parabolic SAR
            if show_sar and not sar_series.empty:
                fig_main.add_trace(go.Scatter(x=sar_series.index, y=sar_series, mode='markers', marker=dict(color='white', size=4, symbol='cross'), name='Parabolic SAR'), row=1, col=1)

            # Bollinger Bands
            if not bb_df.empty:
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Upper'], line=dict(color='#bd93f9', width=1), name='BB Upper'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['B_Lower'], line=dict(color='#bd93f9', width=1), name='BB Lower', fill='tonexty', fillcolor='rgba(189, 147, 249, 0.1)'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=bb_df.index, y=bb_df['SMA'], line=dict(color='#FFD700', width=1), name='BB SMA 20'), row=1, col=1)

            # Ichimoku
            if not ichi_df.empty:
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanA'], line=dict(width=0), showlegend=False, name='Span A'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['SpanB'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 255, 255, 0.1)', name='Ichimoku Cloud'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Tenkan'], line=dict(color='#00FFFF', width=1), name='Tenkan'), row=1, col=1)
                fig_main.add_trace(go.Scatter(x=ichi_df.index, y=ichi_df['Kijun'], line=dict(color='#FF4500', width=1), name='Kijun'), row=1, col=1)

            # SMA Ribbon
            if show_sma:
                colors = ['#FF0000', '#FFA500', '#FFFF00', '#008000']
                for i, period in enumerate([20, 50, 100, 200]):
                    sma = ohlc_df['close'].rolling(window=period).mean()
                    fig_main.add_trace(go.Scatter(x=ohlc_df.index, y=sma, line=dict(color=colors[i], width=1), name=f'SMA {period}'), row=1, col=1)

            # Fibonacci
            if show_fib:
                for label, val in fib_levels.items():
                    fig_main.add_hline(y=val, line_dash="dot", line_color="gray", annotation_text=label, row=1, col=1)

            # Annotations (Max/Min)
            max_idx = ohlc_df['high'].idxmax()
            min_idx = ohlc_df['low'].idxmin()
            fig_main.add_annotation(x=max_idx, y=ohlc_df.loc[max_idx]['high'], text="Max", showarrow=True, arrowhead=1, row=1, col=1)
            fig_main.add_annotation(x=min_idx, y=ohlc_df.loc[min_idx]['low'], text="Min", showarrow=True, arrowhead=1, row=1, col=1)

            fig_main.update_layout(title="Price Action", template="plotly_dark", xaxis_rangeslider_visible=False, height=750)"""

content = content.replace(search, replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
