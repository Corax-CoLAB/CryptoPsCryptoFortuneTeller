import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_helper import check_risk_level, generate_trading_signal

class TestSignals(unittest.TestCase):

    def test_risk_level_low(self):
        # Stable data
        df = pd.DataFrame({'close': np.full(100, 100.0)}, index=pd.date_range('2023-01-01', periods=100))
        msg = check_risk_level(df)
        self.assertIsNone(msg)

    def test_risk_level_high(self):
        # Volatile end
        # 90 days stable, 10 days wild
        stable = np.full(90, 100.0)
        volatile = np.array([100, 150, 50, 200, 10, 100, 150, 50, 200, 10]) # High variance
        prices = np.concatenate([stable, volatile])

        df = pd.DataFrame({'close': prices}, index=pd.date_range('2023-01-01', periods=100))

        # Check volatility
        # We need check_risk_level to see High Volatility
        # compute_volatility uses window 14.
        # Last 14 days include the wild swings.
        # Average volatility over whole period will be low (mostly 0).
        # Current (last) volatility will be high.

        msg = check_risk_level(df)
        self.assertIsNotNone(msg)
        self.assertIn("High Volatility", msg)

    def test_trading_signal(self):
        current_price = 100.0

        # 1. Strong Buy (>20%)
        df_buy = pd.DataFrame({'yhat': [125.0]})
        sig, col = generate_trading_signal(current_price, df_buy)
        self.assertEqual(sig, "STRONG BUY")

        # 2. Sell (< -5%)
        df_sell = pd.DataFrame({'yhat': [94.0]})
        sig, col = generate_trading_signal(current_price, df_sell)
        self.assertEqual(sig, "SELL")

        # 3. Hold
        df_hold = pd.DataFrame({'yhat': [102.0]})
        sig, col = generate_trading_signal(current_price, df_hold)
        self.assertEqual(sig, "HOLD")

if __name__ == '__main__':
    unittest.main()
