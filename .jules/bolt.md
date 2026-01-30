## 2025-01-23 - Streamlit Caching & Asset Optimization
**Learning:** `st.cache_data` is critical for ML models in Streamlit. Re-training an LSTM on every rerun blocked the main thread for 7+ seconds. Also, large assets in `assets/` folder are served as-is; always check image sizes.
**Action:** Always profile Streamlit apps for repeated expensive computations and cache them. Check `assets/` folder sizes early.

## 2026-01-30 - Parallel Model Ensemble & LSTM Batch Size
**Learning:** Parallelizing heterogeneous models (Prophet, LSTM, ARIMA) using `ThreadPoolExecutor` failed to improve performance and actually increased execution time (from ~5.7s to ~6.1s), likely due to GIL contention or TensorFlow overhead. However, increasing LSTM training `batch_size` from 16 to 32 provided a reliable ~20% speedup (approx 0.8s) with minimal risk.
**Action:** Be wary of threading Python-bound ML libraries. Prioritize hyperparameter optimization (like batch size) for quick wins before architectural complexity.
