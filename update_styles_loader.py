with open("streamlit_app/modules/cryptop_crypto_circus_styles.py", "r") as f:
    content = f.read()

loader_css = """
    /* Visual Improvement 2: Magic Orb Loader */
    .stSpinner > div > div {
        border-color: #FF00FF transparent #00FFFF transparent !important;
        animation: spin-magic 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite !important;
        border-width: 4px !important;
        width: 30px !important;
        height: 30px !important;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
    }

    .stSpinner > div {
        color: #bd93f9 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: bold;
        text-shadow: 0 0 5px #FF00FF;
    }

    @keyframes spin-magic {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.2); }
        100% { transform: rotate(360deg) scale(1); }
    }
"""

if "Visual Improvement 2" not in content:
    content = content.replace("</style>", loader_css + "\n</style>")

with open("streamlit_app/modules/cryptop_crypto_circus_styles.py", "w") as f:
    f.write(content)

print("Loaders Updated")
