import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

fng_search = """    st.subheader("😱 Fear & Greed")
    fng = get_fear_and_greed_index()
    if fng:
        val = int(fng['value'])
        color = "red" if val < 40 else "green" if val > 60 else "orange"
        st.markdown(f"<h2 style='color: {html.escape(color)}; text-align: center;'>{html.escape(str(val))}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{html.escape(fng['classification'])}</p>", unsafe_allow_html=True)
    else:
        st.write("N/A")"""

fng_replace = """    st.subheader("😱 Fear & Greed")
    fng = get_fear_and_greed_index()
    if fng:
        val = int(fng['value'])

        fig_fng = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = val,
            title = {'text': fng['classification'], 'font': {'size': 18}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "white"},
                'bgcolor': "black",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 60], 'color': "orange"},
                    {'range': [60, 100], 'color': "green"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))

        fig_fng.update_layout(height=250, margin=dict(t=30, b=0, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_fng, use_container_width=True)
    else:
        st.write("N/A")"""

content = content.replace(fng_search, fng_replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
