
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

if __name__ == '__main__':
    unittest.main()
