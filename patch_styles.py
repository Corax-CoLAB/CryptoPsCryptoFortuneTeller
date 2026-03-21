import re

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_styles.py", "r") as f:
    content = f.read()

styles_add = """
        /* Visual Improvement 5: Glassmorphism UI Elements and Custom Loader */

        /* Glassmorphism for expanders and metrics */
        .streamlit-expanderHeader {
            background: rgba(20, 0, 30, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 12px 12px 0 0 !important;
            border-bottom: 1px solid rgba(255, 0, 255, 0.3) !important;
        }

        .streamlit-expanderContent {
            background: rgba(10, 0, 20, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 0 0 12px 12px !important;
            border: 1px solid rgba(0, 255, 255, 0.2) !important;
            border-top: none !important;
        }

        div[data-testid="stMetricValue"] {
            background: linear-gradient(135deg, rgba(255,0,255,0.1) 0%, rgba(0,255,255,0.1) 100%);
            padding: 10px 15px;
            border-radius: 8px;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.1);
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
            display: inline-block;
        }

        /* Animated neon borders for dataframes */
        div[data-testid="stDataFrame"] {
            border: 2px solid transparent;
            border-image: linear-gradient(45deg, #FF00FF, #00FFFF) 1;
            box-shadow: 0 0 15px rgba(255, 0, 255, 0.2);
            animation: pulse-border 3s infinite alternate;
        }

        @keyframes pulse-border {
            0% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.2); }
            100% { box-shadow: 0 0 20px rgba(255, 0, 255, 0.5); }
        }

        /* Custom Spinner/Loader Styling override */
        .stSpinner > div > div {
            border-top-color: #FF00FF !important;
            border-right-color: #00FFFF !important;
            border-bottom-color: #FF00FF !important;
            border-left-color: #00FFFF !important;
            animation: spin 1s linear infinite, color-shift 3s ease-in-out infinite alternate !important;
        }

        @keyframes color-shift {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
"""

search = "</style>"
replace = styles_add + "\n    </style>"

content = content.replace(search, replace)

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_styles.py", "w") as f:
    f.write(content)
