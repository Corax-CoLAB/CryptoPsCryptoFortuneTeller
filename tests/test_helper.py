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
    calculate_bollinger_bands,
    calculate_moon_math,
    calculate_roi
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

def test_calculate_moon_math():
    # Test case 1: Normal calculation
    current_price = 10.0
    current_supply = 1_000_000.0
    target_mc = 20_000_000.0 # Implies target price of 20

    target_price, upside = calculate_moon_math(current_price, current_supply, target_mc)

    assert target_price == 20.0
    assert upside == 100.0 # (20 - 10) / 10 * 100 = 100%

    # Test case 2: Zero supply (should return 0, 0)
    assert calculate_moon_math(10, 0, 1000) == (0, 0)

    # Test case 3: Target lower than current (negative upside)
    target_mc_low = 5_000_000.0 # Implies target price 5
    t_price, up = calculate_moon_math(10, 1_000_000, target_mc_low)
    assert t_price == 5.0
    assert up == -50.0

def test_calculate_moon_math_zero_price():
    # Test case 4: Zero current price (should handle gracefully)
    t_price, up = calculate_moon_math(0, 1_000_000, 20_000_000)
    # Should return 0, 0 or similar to avoid crash
    assert t_price == 0
    assert up == 0

def test_calculate_roi_zero_investment():
    # Test case: Zero initial investment
    val, pct = calculate_roi(0, 10, 20)
    assert val == 0
    assert pct == 0
