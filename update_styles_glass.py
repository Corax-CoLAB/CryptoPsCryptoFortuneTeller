with open("streamlit_app/modules/cryptop_crypto_circus_styles.py", "r") as f:
    content = f.read()

glass_css = """
    /* Visual Improvement 3: Glassmorphism Metric Cards */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) saturate(150%);
        -webkit-backdrop-filter: blur(10px) saturate(150%);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 15px;
        padding: 15px 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    /* Neon Top Border Glow */
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00FFFF, #FF00FF, transparent);
    }

    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 255, 255, 0.4);
        border-color: #FF00FF;
    }
"""

if "Visual Improvement 3" not in content:
    content = content.replace("</style>", glass_css + "\n</style>")

with open("streamlit_app/modules/cryptop_crypto_circus_styles.py", "w") as f:
    f.write(content)

print("Glass Metric Cards Added")
