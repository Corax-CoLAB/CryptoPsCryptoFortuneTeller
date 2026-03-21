import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

heatmap_search = """                        fig_corr = px.imshow(
                            corr_matrix,
                            text_auto=True,
                            aspect="auto",
                            color_continuous_scale='RdBu_r',
                            title=f"Correlation Heatmap ({comp_days} days)"
                        )"""

heatmap_replace = """                        # Visual Improvement 2: Interactive Heatmap

                        # Replace IDs with names for better display
                        corr_names = [next(k for k, v in mapping.items() if v == col) for col in corr_matrix.columns]
                        corr_matrix.columns = corr_names
                        corr_matrix.index = corr_names

                        fig_corr = go.Figure(data=go.Heatmap(
                            z=corr_matrix.values,
                            x=corr_matrix.columns,
                            y=corr_matrix.index,
                            colorscale='RdBu',
                            zmin=-1, zmax=1,
                            hoverongaps=False,
                            text=np.round(corr_matrix.values, 2),
                            texttemplate="%{text}",
                            textfont={"size": 12}
                        ))

                        fig_corr.update_layout(
                            title=f"Correlation Heatmap ({comp_days} days)",
                            xaxis_title="Assets",
                            yaxis_title="Assets",
                            template="plotly_dark",
                            width=700,
                            height=600
                        )"""

content = content.replace(heatmap_search, heatmap_replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
