
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# Mock streamlit before importing helper
st_mock = MagicMock()
def cache_decorator(**kwargs):
    def wrapper(f):
        return f
    return wrapper
st_mock.cache_data = cache_decorator
sys.modules['streamlit'] = st_mock

# Add streamlit_app to path
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(current_dir)
app_path = os.path.join(repo_root, 'streamlit_app')
if app_path not in sys.path:
    sys.path.append(app_path)

# Import the helper module
from modules import cryptop_crypto_circus_helper as helper

class BenchmarkHistoricalCaching(unittest.TestCase):
    def setUp(self):
        # Mock the CoinGeckoAPI instance in the helper module
        self.cg_mock = MagicMock()
        helper.cg = self.cg_mock

        # Setup mock return values to avoid errors
        # Market Chart
        self.cg_mock.get_coin_market_chart_by_id.return_value = {
            'prices': [
                [1672531200000, 100.0], # 2023-01-01
                [1672617600000, 101.0], # 2023-01-02
                [1672704000000, 102.0], # 2023-01-03
            ]
        }
        # OHLC
        self.cg_mock.get_coin_ohlc_by_id.return_value = [
            [1672531200000, 100.0, 105.0, 95.0, 101.0],
            [1672617600000, 101.0, 106.0, 96.0, 102.0],
        ]

    def test_get_historical_prices_optimization(self):
        """
        Verify if get_historical_prices uses Tiered Caching Strategy (Buckets).
        """
        print("\nTesting get_historical_prices optimization (Tiered Caching)...")

        # Test Tier 1 (<= 1 day)
        helper.get_historical_prices('bitcoin', days=0.5)
        args, kwargs = self.cg_mock.get_coin_market_chart_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 1, "Should use Bucket 1 for days <= 1")

        # Test Tier 2 (<= 90 days)
        helper.get_historical_prices('bitcoin', days=30)
        args, kwargs = self.cg_mock.get_coin_market_chart_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 90, "Should use Bucket 90 for days <= 90")

        helper.get_historical_prices('bitcoin', days=90)
        args, kwargs = self.cg_mock.get_coin_market_chart_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 90, "Should use Bucket 90 for days=90")

        # Test Tier 3 (> 90 days)
        helper.get_historical_prices('bitcoin', days=365)
        args, kwargs = self.cg_mock.get_coin_market_chart_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 'max', "Should use Bucket 'max' for days > 90")

        # Test 'max' input explicitly (Code Review Regression Check)
        helper.get_historical_prices('bitcoin', days='max')
        args, kwargs = self.cg_mock.get_coin_market_chart_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 'max', "Should handle days='max' correctly")

        print("✅ get_historical_prices is OPTIMIZED (uses Buckets 1, 90, max)")

    def test_get_historical_ohlc_optimization(self):
        """
        Verify if get_historical_ohlc uses Tiered Caching Strategy (Buckets).
        """
        print("\nTesting get_historical_ohlc optimization (Tiered Caching)...")

        # Test Tier 1 (<= 1 day)
        helper.get_historical_ohlc('bitcoin', days=0.5)
        args, kwargs = self.cg_mock.get_coin_ohlc_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 1, "Should use Bucket 1 for days <= 1")

        # Test Tier 2 (<= 30 days)
        helper.get_historical_ohlc('bitcoin', days=15)
        args, kwargs = self.cg_mock.get_coin_ohlc_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 30, "Should use Bucket 30 for days <= 30")

        helper.get_historical_ohlc('bitcoin', days=30)
        args, kwargs = self.cg_mock.get_coin_ohlc_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 30, "Should use Bucket 30 for days=30")

        # Test Tier 3 (> 30 days)
        helper.get_historical_ohlc('bitcoin', days=90)
        args, kwargs = self.cg_mock.get_coin_ohlc_by_id.call_args_list[-1]
        self.assertEqual(kwargs.get('days'), 'max', "Should use Bucket 'max' for days > 30")

        print("✅ get_historical_ohlc is OPTIMIZED (uses Buckets 1, 30, max)")

if __name__ == '__main__':
    unittest.main()
