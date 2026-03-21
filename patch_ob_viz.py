import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

# Make sure we flag it properly
search = """                            fig_ob = go.Figure()
                            fig_ob.add_trace(go.Scatter(x=bid_df['Price'], y=bid_df['Cumulative_Volume'], name='Bids', fill='tozeroy', line=dict(color='green')))
                            fig_ob.add_trace(go.Scatter(x=ask_df['Price'], y=ask_df['Cumulative_Volume'], name='Asks', fill='tozeroy', line=dict(color='red')))
                            fig_ob.update_layout(title=f"{t_symbol} Market Depth", xaxis_title="Price", yaxis_title="Cumulative Volume", template="plotly_dark")
                            st.plotly_chart(fig_ob, use_container_width=True)"""

replace = """                            # Visual Improvement 4: Order Book Depth Chart Visualization
                            fig_ob = go.Figure()
                            # Sort bids descending, asks ascending to create proper depth shape
                            bid_df_plot = bid_df.sort_values('Price', ascending=False)
                            bid_df_plot['Cumulative_Volume'] = bid_df_plot['Volume'].cumsum()
                            ask_df_plot = ask_df.sort_values('Price', ascending=True)
                            ask_df_plot['Cumulative_Volume'] = ask_df_plot['Volume'].cumsum()

                            fig_ob.add_trace(go.Scatter(x=bid_df_plot['Price'], y=bid_df_plot['Cumulative_Volume'], name='Bids', fill='tozeroy', fillcolor='rgba(0,255,0,0.3)', line=dict(color='#00FF00', width=2), hoverinfo='x+y', mode='lines'))
                            fig_ob.add_trace(go.Scatter(x=ask_df_plot['Price'], y=ask_df_plot['Cumulative_Volume'], name='Asks', fill='tozeroy', fillcolor='rgba(255,0,0,0.3)', line=dict(color='#FF0000', width=2), hoverinfo='x+y', mode='lines'))

                            current_price_mid = (bid_df['Price'].max() + ask_df['Price'].min()) / 2
                            fig_ob.add_vline(x=current_price_mid, line_dash="dash", line_color="gray", annotation_text="Mid Price")

                            fig_ob.update_layout(
                                title=f"L2 Market Depth for {t_symbol}",
                                xaxis_title="Price (USD)",
                                yaxis_title="Cumulative Depth",
                                template="plotly_dark",
                                hovermode="x unified",
                                height=400,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig_ob, use_container_width=True)"""

content = content.replace(search, replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
