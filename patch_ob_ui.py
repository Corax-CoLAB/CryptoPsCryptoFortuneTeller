import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

ob_ui_search = """            # Open Orders
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
                    st.info("No open orders.")"""

ob_ui_replace = """            # Open Orders
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

            # Order Book Analysis
            st.markdown("---")
            st.write("#### 📊 Order Book Depth Analysis")
            if st.button("Analyze Depth", key="ob_btn"):
                with st.spinner(f"Fetching L2 Order Book for {t_symbol}..."):
                    ob, err = st.session_state.exchange_client.get_order_book(t_symbol, limit=100)
                    if ob:
                        bids = ob.get('bids', [])
                        asks = ob.get('asks', [])

                        if bids and asks:
                            bid_df = pd.DataFrame(bids, columns=['Price', 'Volume'])
                            ask_df = pd.DataFrame(asks, columns=['Price', 'Volume'])

                            bid_df['Cumulative_Volume'] = bid_df['Volume'].cumsum()
                            ask_df['Cumulative_Volume'] = ask_df['Volume'].cumsum()

                            total_bid_vol = bid_df['Volume'].sum()
                            total_ask_vol = ask_df['Volume'].sum()
                            imbalance = total_bid_vol / (total_bid_vol + total_ask_vol)

                            ob_col1, ob_col2, ob_col3 = st.columns(3)
                            ob_col1.metric("Bid Imbalance", f"{imbalance*100:.2f}%")
                            ob_col2.metric("Total Bid Depth", f"{total_bid_vol:,.2f}")
                            ob_col3.metric("Total Ask Depth", f"{total_ask_vol:,.2f}")

                            fig_ob = go.Figure()
                            fig_ob.add_trace(go.Scatter(x=bid_df['Price'], y=bid_df['Cumulative_Volume'], name='Bids', fill='tozeroy', line=dict(color='green')))
                            fig_ob.add_trace(go.Scatter(x=ask_df['Price'], y=ask_df['Cumulative_Volume'], name='Asks', fill='tozeroy', line=dict(color='red')))
                            fig_ob.update_layout(title=f"{t_symbol} Market Depth", xaxis_title="Price", yaxis_title="Cumulative Volume", template="plotly_dark")
                            st.plotly_chart(fig_ob, use_container_width=True)
                        else:
                            st.warning("Order book data is empty.")
                    else:
                        st.error(err)"""

content = content.replace(ob_ui_search, ob_ui_replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
