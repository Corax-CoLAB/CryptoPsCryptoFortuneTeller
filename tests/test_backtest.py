import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_circus_helper import calculate_backtest, calculate_rsi

def test_calculate_backtest_rsi_strategy():
    # Create synthetic data with a known pattern
    # We want RSI to dip below 30 then go above 70

    # 50 points
    idx = pd.date_range('2023-01-01', periods=100, freq='D')

    # Create a sine wave that will swing RSI
    # RSI correlates with price changes.
    # A sine wave in price will create a sine wave in RSI approx.
    x = np.linspace(0, 4*np.pi, 100)
    prices = 100 + 10 * np.sin(x)

    df = pd.DataFrame({'close': prices}, index=idx)

    # Run backtest
    res_df, metrics = calculate_backtest(df, strategy_type='RSI Mean Reversion')

    # Check structure
    assert 'signal' in res_df.columns
    assert 'strategy_returns' in res_df.columns
    assert 'cumulative_strategy_returns' in res_df.columns
    assert 'Total Return' in metrics

    # Verify signals logic manually
    # We can recalculate RSI and check if signals align
    rsi = calculate_rsi(df)

    # Check a few points
    # signal should be 1 if RSI < 30 was triggered and we haven't hit > 70 yet

    # Find points where RSI < 30
    oversold = rsi < 30
    overbought = rsi > 70

    # If there are any oversold points, the signal should turn 1
    if oversold.any():
        # Get the first index where oversold
        first_buy_idx = oversold[oversold].index[0]
        # Check if signal is 1 there (or after? Logic says "Buy if RSI < 30",
        # usually means signal becomes 1 AT that point or NEXT point depending on implementation.
        # The implementation: signal_series[rsi < 30] = 1.0. So at that point it is 1.

        # Verify signal is 1 at that index
        assert res_df.loc[first_buy_idx, 'signal'] == 1.0

    # Ensure signal stays 1 until overbought
    # This is harder to test generally without specific data, but we can check consistency
    # If signal is 1, and previous signal was 1, and RSI <= 70, it should be correct.

    # Let's just check that we don't have signal 0 when RSI < 30
    # (Unless it was overwrote? No, < 30 sets to 1.0)
    assert (res_df.loc[oversold, 'signal'] == 1.0).all()

    # Check we don't have signal 1 when RSI > 70
    assert (res_df.loc[overbought, 'signal'] == 0.0).all()

def test_calculate_backtest_sma_strategy():
    # Simple check for SMA
    idx = pd.date_range('2023-01-01', periods=100, freq='D')
    prices = np.linspace(100, 200, 100) # Uptrend
    df = pd.DataFrame({'close': prices}, index=idx)

    res_df, metrics = calculate_backtest(df, strategy_type='SMA Crossover')

    assert 'signal' in res_df.columns
    # In a perfect uptrend, short MA should eventually be > long MA -> signal 1
    # SMA 20 vs 50
    # After 50 points, we should have values
    assert res_df['signal'].iloc[-1] == 1.0
