import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import sys
import os

# Mock streamlit
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit'].cache_data = lambda func=None, **kwargs: (lambda f: f) if func is None else func
sys.modules['streamlit'].error = MagicMock()

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_models import forecast_arima, forecast_sarima, forecast_general_ensemble

class TestNewModels(unittest.TestCase):

    def setUp(self):
        # Create dummy data (100 days of linear trend)
        self.df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=100),
            'close': np.linspace(100, 200, 100)
        }).set_index('date')

    def test_forecast_arima_structure(self):
        # Test that ARIMA returns correct structure even if values are mocked/approx
        # Since we can't easily mock statsmodels entirely without complex patching,
        # we will rely on the fact that statsmodels is installed and works on simple data.

        # NOTE: Running ARIMA on random small data might be unstable or warn,
        # but linear data should be fine.

        res = forecast_arima(self.df, periods=10)

        self.assertEqual(len(res), 10)
        self.assertListEqual(list(res.columns), ['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

        # Check that it predicts roughly the trend (next val > 200)
        self.assertTrue(res['yhat'].iloc[0] > 190) # generous buffer

    def test_forecast_sarima_structure(self):
        # SARIMA test
        res = forecast_sarima(self.df, periods=10)

        self.assertEqual(len(res), 10)
        self.assertListEqual(list(res.columns), ['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

        self.assertTrue(res['yhat'].iloc[0] > 190)

    @patch('modules.cryptop_crypto_fortune_teller_models.forecast_arima')
    @patch('modules.cryptop_crypto_fortune_teller_models.forecast_sarima')
    @patch('modules.cryptop_crypto_fortune_teller_models._run_prophet_model')
    def test_general_ensemble_mixing(self, mock_prophet, mock_sarima, mock_arima):
        # Setup mocks to return standard simple frames (future only for arima/sarima, full for prophet)

        future_dates = pd.date_range(start='2023-04-11', periods=10)

        # ARIMA returns 10 rows (future)
        df_future = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(10, 210.0),
            'yhat_lower': np.full(10, 200.0),
            'yhat_upper': np.full(10, 220.0)
        })
        mock_arima.return_value = df_future.copy()
        mock_sarima.return_value = df_future.copy()

        # Prophet returns 110 rows (100 hist + 10 future)
        full_dates = pd.date_range(start='2023-01-01', periods=110)
        df_prophet = pd.DataFrame({
            'ds': full_dates,
            'yhat': np.full(110, 210.0), # Simplification
            'yhat_lower': np.full(110, 200.0),
            'yhat_upper': np.full(110, 220.0)
        })
        mock_prophet.return_value = df_prophet

        # Test mixing
        model_names = ["Prophet (Standard)", "ARIMA"]
        res = forecast_general_ensemble(self.df, model_names, periods=10)

        # Result should be 10 rows (future only as per our design decision)
        self.assertEqual(len(res), 10)

        # Values should be average of 210 and 210 -> 210
        self.assertAlmostEqual(res['yhat'].iloc[0], 210.0)

        # Ensure both were called
        mock_arima.assert_called_once()
        mock_prophet.assert_called_once()
        mock_sarima.assert_not_called()

if __name__ == '__main__':
    unittest.main()
