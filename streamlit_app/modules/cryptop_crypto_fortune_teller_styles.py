def apply_custom_css():
    import streamlit as st
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rye&family=Cinzel:wght@400;700&family=Quicksand:wght@300;400;700&display=swap');

    /* Global Fonts */
    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Rye', cursive !important;
        color: #FFD700 !important; /* Gold */
        text-shadow: 2px 2px 4px #000000;
        letter-spacing: 1px;
    }

    /* Main Background - Deep Psychedelic */
    .stApp {
        background: radial-gradient(circle at center, #1a0b2e 0%, #0e0018 70%, #000000 100%);
        background-attachment: fixed;
        color: #e0f7fa;
    }

    /* Sidebar - Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(14, 0, 24, 0.85) !important;
        backdrop-filter: blur(10px);
        border-right: 2px solid #FF00FF;
        box-shadow: 5px 0 15px rgba(255, 0, 255, 0.2);
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
         color: #00FFFF !important; /* Cyan headers in sidebar */
         text-shadow: 0 0 5px #00FFFF;
    }

    /* Sidebar User Inputs */
    [data-testid="stSidebar"] .stMarkdown p {
        color: #bd93f9;
    }

    /* Tabs styling - Carnival Ticket Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: rgba(46, 11, 40, 0.6);
        border: 1px solid #FF00FF;
        border-bottom: none;
        border-radius: 12px 12px 0 0;
        color: #FF00FF;
        font-family: 'Cinzel', serif;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #FF00FF 0%, #a800a8 100%) !important;
        color: #fff !important;
        border: 1px solid #fff;
        box-shadow: 0 -5px 15px rgba(255, 0, 255, 0.6);
        transform: translateY(-2px);
    }

    /* Metric Cards - Crystal Ball Glow */
    [data-testid="stMetricValue"] {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem !important;
        color: #00FFFF !important;
        text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF;
    }
    [data-testid="stMetricLabel"] {
        color: #ff79c6;
        font-family: 'Rye', cursive;
        font-size: 1rem !important;
    }

    /* Inputs */
    .stSelectbox > div > div {
        background-color: #0e0018;
        border: 1px solid #bd93f9;
        color: #fff;
    }
    .stSelectbox > div > div:hover {
        border-color: #FF00FF;
    }

    /* Sliders */
    .stSlider > div > div > div > div {
        background-color: #FF00FF;
        box-shadow: 0 0 10px #FF00FF;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #FF00FF, #8A2BE2);
        color: #fff;
        font-family: 'Rye', cursive;
        border: 2px solid #fff;
        border-radius: 25px;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.6);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 0, 255, 0.8);
        border-color: #00FFFF;
        color: #00FFFF;
    }

    /* Divider */
    hr {
        border-color: #FF00FF;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 8px #FF00FF;
        opacity: 0.7;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Cinzel', serif;
        color: #00FFFF;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }

    /* Dataframe/Table */
    [data-testid="stDataFrame"] {
        border: 1px solid #444;
        border-radius: 5px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #0e0018;
    }
    ::-webkit-scrollbar-thumb {
        background: #FF00FF;
        border-radius: 5px;
    }

    /* Image glow */
    img {
        filter: drop-shadow(0 0 5px rgba(255, 0, 255, 0.5));
    }
</style>
""", unsafe_allow_html=True)
