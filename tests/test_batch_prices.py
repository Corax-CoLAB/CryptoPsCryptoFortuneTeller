
import pandas as pd
import unittest
from unittest.mock import patch
from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import get_batch_historical_prices

class TestOptimization(unittest.TestCase):
    @patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_historical_prices')
    def test_batch_prices(self, mock_get_prices):
        # Setup mock returns
        dates = pd.date_range('2023-01-01', periods=3)
        df1 = pd.DataFrame({'close': [10, 11, 12]}, index=dates)
        df2 = pd.DataFrame({'close': [20, 21, 22]}, index=dates)

        def side_effect(cid, days=90):
            if cid == 'bitcoin': return df1.copy()
            if cid == 'ethereum': return df2.copy()
            return pd.DataFrame()

        mock_get_prices.side_effect = side_effect

        # Run function
        # Note: Since we are running outside of Streamlit, cache_data decorator might complain
        # or just work if we ignore warnings.
        res = get_batch_historical_prices(['bitcoin', 'ethereum'])

        # Verify
        self.assertEqual(res.shape, (3, 2))
        self.assertIn('bitcoin', res.columns)
        self.assertIn('ethereum', res.columns)
        self.assertEqual(res['bitcoin'].iloc[0], 10)
        self.assertEqual(res['ethereum'].iloc[0], 20)
        print("Batch prices optimization verified!")

    @patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_historical_prices')
    @patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.st')
    def test_batch_prices_limit(self, mock_st, mock_get_prices):
        #Verify batch size limit

        # Setup mock returns to always return a valid DF
        dates = pd.date_range('2023-01-01', periods=1)
        mock_get_prices.return_value = pd.DataFrame({'close': [100]}, index=dates)

        # Create 15 dummy IDs
        coin_ids = [f'coin_{i}' for i in range(15)]

        # Run function
        res = get_batch_historical_prices(coin_ids)

        # Verify result has exactly 10 columns (the limit)
        self.assertEqual(res.shape[1], 10, "Should limit to 10 assets")

        # Verify warning was called
        mock_st.warning.assert_called_once()
        print("Security limit verified!")

    @patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_historical_prices')
    def test_batch_prices_deduplication(self, mock_get_prices):
        #Verify deduplication of inputs to prevent DoS

        # Setup mock
        dates = pd.date_range('2023-01-01', periods=1)
        mock_get_prices.return_value = pd.DataFrame({'close': [100]}, index=dates)

        # Duplicate inputs
        coin_ids = ['bitcoin', 'bitcoin', 'bitcoin']

        # Run
        res = get_batch_historical_prices(coin_ids)

        # Verify result has 1 column
        self.assertEqual(res.shape[1], 1, "Should deduplicate identical inputs")
        self.assertIn('bitcoin', res.columns)

        # Verify API called once
        # In multi-threaded context, side_effect tracking is safe because we verify the mock
        self.assertEqual(mock_get_prices.call_count, 1, "Should call API only once for unique ID")
        print("Deduplication verified!")

if __name__ == '__main__':
    unittest.main()
