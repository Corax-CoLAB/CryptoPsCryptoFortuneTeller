import re

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    content = f.read()

import_search = "from modules.cryptop_crypto_fortune_teller_models import ("
import_replace = import_search + "\n    auto_tune_prophet,"

content = content.replace(import_search, import_replace)

search = """            model_params = {
                'changepoint_prior_scale': p_changepoint,
                'seasonality_prior_scale': p_seasonality,
                'seasonality_mode': p_season_mode
            }"""

replace = """            auto_tune = st.checkbox("Auto-Tune Prophet Hyperparameters (Beta)", value=False, help="Run an automatic grid search to find optimal changepoint and seasonality scales. Overrides manual sliders.")

            if auto_tune:
                with st.spinner("Auto-tuning Prophet models..."):
                    # Use a small historical sample for speed
                    hist_for_tune = get_historical_prices(coin_id, days=365)
                    if not hist_for_tune.empty:
                        best_params = auto_tune_prophet(hist_for_tune)
                        st.success(f"Tuning complete. Best CPS: {best_params.get('changepoint_prior_scale')}, SPS: {best_params.get('seasonality_prior_scale')}")
                        p_changepoint = best_params.get('changepoint_prior_scale', p_changepoint)
                        p_seasonality = best_params.get('seasonality_prior_scale', p_seasonality)

            model_params = {
                'changepoint_prior_scale': p_changepoint,
                'seasonality_prior_scale': p_seasonality,
                'seasonality_mode': p_season_mode
            }"""

content = content.replace(search, replace)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(content)
