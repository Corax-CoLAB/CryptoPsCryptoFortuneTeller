with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

# Replace Pie chart with Sunburst/Donut and better tooltips
old_pie = """        fig_pie = px.pie(df_port, values='Value', names='Coin', title='Allocation', hole=0.3)
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)"""

new_pie = """        # Visual Improvement 5: Sunburst / Donut Upgrade
        df_port['Root'] = 'Portfolio'
        fig_pie = px.sunburst(
            df_port, path=['Root', 'Coin'], values='Value',
            color='PnL (%)', color_continuous_scale='RdYlGn', color_continuous_midpoint=0,
            title='Hierarchical Asset Allocation & Performance',
            hover_data=['Amount', 'Value', 'PnL ($)']
        )
        fig_pie.update_traces(textinfo="label+percent entry")
        fig_pie.update_layout(template="plotly_dark", height=500, margin=dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig_pie, use_container_width=True)"""

content = content.replace(old_pie, new_pie)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)

print("Sunburst Portfolio Added")
