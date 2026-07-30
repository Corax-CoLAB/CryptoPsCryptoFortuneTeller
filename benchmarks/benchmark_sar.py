import pandas as pd
import numpy as np
import time
from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import calculate_parabolic_sar

df = pd.DataFrame({
    'high': np.random.rand(10000) * 100,
    'low': np.random.rand(10000) * 100,
    'close': np.random.rand(10000) * 100
})

start = time.time()
calculate_parabolic_sar(df)
end = time.time()

print(f"Time: {end-start}")
