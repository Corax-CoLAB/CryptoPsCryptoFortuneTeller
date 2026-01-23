import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_helper import (
    compute_volatility,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands
)

def test_compute_volatility():
    # Create dummy data
    data = {
        'close': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100, 101, 102, 103, 104],
        'high':  [101, 102, 103, 104, 103, 102, 101, 100, 99, 100, 101, 102, 103, 104, 105],
        'low':   [99, 100, 101, 102, 101, 100, 99, 98, 97, 98, 99, 100, 101, 102, 103]
    }
    df = pd.DataFrame(data)
    vol = compute_volatility(df, window=5)

    assert 'rolling_std' in vol.columns
    assert 'ATR' in vol.columns
    # The first few will be NaN due to window
    assert not vol['rolling_std'].iloc[-1] is np.nan

def test_calculate_rsi():
    # Constant uptrend
    data = {'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}
    df = pd.DataFrame(data)
    rsi = calculate_rsi(df, period=10)

    # RSI should be high
    assert rsi.iloc[-1] > 80

def test_calculate_indicators():
    data = {'close': np.random.rand(50) * 100}
    df = pd.DataFrame(data)

    macd = calculate_macd(df)
    assert 'MACD' in macd.columns
    assert 'Signal' in macd.columns

    bb = calculate_bollinger_bands(df)
    assert 'B_Upper' in bb.columns
    assert 'B_Lower' in bb.columns
    assert bb['B_Upper'].iloc[-1] >= bb['B_Lower'].iloc[-1]
