with open('streamlit_app/cryptop_crypto_fortune_teller_main.py', 'r') as f:
    content = f.read()

content = content.replace('st.toast(msg, icon="✅")\n                        st.success(msg)', 'st.toast(msg, icon="✅")\n                            st.success(msg)')
content = content.replace('if res: st.toast(msg, icon="✅")\n                        st.success(msg)', 'if res:\n                        st.toast(msg, icon="✅")\n                        st.success(msg)')

with open('streamlit_app/cryptop_crypto_fortune_teller_main.py', 'w') as f:
    f.write(content)
