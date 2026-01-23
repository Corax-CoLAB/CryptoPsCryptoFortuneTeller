## 2025-01-23 - Streamlit Caching & Asset Optimization
**Learning:** `st.cache_data` is critical for ML models in Streamlit. Re-training an LSTM on every rerun blocked the main thread for 7+ seconds. Also, large assets in `assets/` folder are served as-is; always check image sizes.
**Action:** Always profile Streamlit apps for repeated expensive computations and cache them. Check `assets/` folder sizes early.
