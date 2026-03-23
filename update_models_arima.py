with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "r") as f:
    content = f.read()

auto_arima_import = """
import warnings
import itertools
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)

def get_best_arima(series, max_p=3, max_q=3, d=1):
    \"\"\"
    Technical Improvement 2: Auto-ARIMA
    Finds best ARIMA(p,d,q) order based on AIC.
    \"\"\"
    best_aic = float("inf")
    best_order = (0, d, 0)
    for p, q in itertools.product(range(max_p+1), range(max_q+1)):
        try:
            model = ARIMA(series, order=(p, d, q))
            results = model.fit()
            if results.aic < best_aic:
                best_aic = results.aic
                best_order = (p, d, q)
        except:
            continue
    return best_order
"""

if "def get_best_arima" not in content:
    content = content.replace("from statsmodels.tsa.statespace.sarimax import SARIMAX\n",
                              "from statsmodels.tsa.statespace.sarimax import SARIMAX\n" + auto_arima_import)


# Replace forecast_arima logic
old_arima = """        model = ARIMA(series, order=(5, 1, 0))
        model_fit = model.fit()"""

new_arima = """        # Technical Improvement 2: Dynamic ARIMA order selection (Auto-ARIMA)
        best_order = get_best_arima(series, max_p=3, max_q=3, d=1)
        model = ARIMA(series, order=best_order)
        model_fit = model.fit()"""
content = content.replace(old_arima, new_arima)

# Replace forecast_sarima logic
old_sarima = """        # Using a simpler seasonal order to ensure stability in generic cases
        model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7))
        model_fit = model.fit(disp=False)"""

new_sarima = """        # Technical Improvement 2: Dynamic SARIMA order selection based on best ARIMA base
        best_order = get_best_arima(series, max_p=2, max_q=2, d=1) # Reduced grid for speed
        model = SARIMAX(series, order=best_order, seasonal_order=(0, 1, 1, 7))
        model_fit = model.fit(disp=False)"""
content = content.replace(old_sarima, new_sarima)

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "w") as f:
    f.write(content)

print("Models updated with Auto-ARIMA successfully")
