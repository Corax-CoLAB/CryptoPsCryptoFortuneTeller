with open("streamlit_app/cryptop_crypto_circus_main.py", "r") as f:
    content = f.read()

# Update RSI Plotly with shaded regions
old_rsi = """                fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")"""

new_rsi = """                fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
                # Technical Improvement: Advanced Shading
                fig_rsi.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, layer="below", line_width=0)
                fig_rsi.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, layer="below", line_width=0)"""

content = content.replace(old_rsi, new_rsi)

# Update MACD Plotly to fill area
old_macd = """                    fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df['Histogram'], name='Hist', marker_color='#444'))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['MACD'], name='MACD', line=dict(color='#00FFFF')))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['Signal'], name='Signal', line=dict(color='#FF4500')))"""

new_macd = """                    fig_macd.add_trace(go.Bar(x=macd_df.index, y=macd_df['Histogram'], name='Hist', marker_color=np.where(macd_df['Histogram'] < 0, 'red', 'green')))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['MACD'], name='MACD', line=dict(color='#00FFFF', width=2)))
                    fig_macd.add_trace(go.Scatter(x=macd_df.index, y=macd_df['Signal'], name='Signal', line=dict(color='#FF4500', width=2), fill='tonexty', fillcolor='rgba(255, 69, 0, 0.2)'))"""

content = content.replace(old_macd, new_macd)

with open("streamlit_app/cryptop_crypto_circus_main.py", "w") as f:
    f.write(content)

print("Plotly Advanced Formatting Added")
