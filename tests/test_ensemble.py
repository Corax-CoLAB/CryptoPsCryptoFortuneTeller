import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import sys
import os
import importlib

# Mock streamlit before importing modules
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit'].cache_data = lambda func=None, **kwargs: (lambda f: f) if func is None else func
sys.modules['streamlit'].error = MagicMock()

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

import modules.cryptop_crypto_circus_models
# Force reload to ensure it uses the mocked streamlit
importlib.reload(modules.cryptop_crypto_circus_models)

from modules.cryptop_crypto_circus_models import forecast_prophet_ensemble, get_prophet_config

class TestProphetEnsemble(unittest.TestCase):

    def setUp(self):
        # Create dummy data
        self.df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=100),
            'close': np.linspace(100, 200, 100)
        }).set_index('date')

    @patch('modules.cryptop_crypto_circus_models.Prophet')
    def test_single_model(self, mock_prophet):
        # Setup mock return
        mock_model_instance = MagicMock()
        mock_prophet.return_value = mock_model_instance

        # Mock predict return
        # Since _run_prophet_model now runs for MAX_FORECAST_HORIZON (365) + History (100) = 465
        future_dates = pd.date_range(start='2023-01-01', periods=465)
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.linspace(100, 565, 465),
            'yhat_lower': np.linspace(90, 555, 465),
            'yhat_upper': np.linspace(110, 575, 465)
        })
        mock_model_instance.make_future_dataframe.return_value = pd.DataFrame({'ds': future_dates})
        mock_model_instance.predict.return_value = forecast_df

        # Run
        res = forecast_prophet_ensemble(self.df, ["Standard"], periods=30)

        # Verify
        # Now expects only future periods (30)
        self.assertEqual(len(res), 30)
        self.assertIn('yhat', res.columns)
        mock_prophet.assert_called() # Should be called

    @patch('modules.cryptop_crypto_circus_models.Prophet')
    def test_ensemble_averaging(self, mock_prophet):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_prophet.return_value = mock_model_instance

        # 100 history + 365 future = 465
        future_dates = pd.date_range(start='2023-01-01', periods=465)

        # DataFrame 1 (Standard): yhat = 100
        df1 = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(465, 100.0),
            'yhat_lower': np.full(465, 90.0),
            'yhat_upper': np.full(465, 110.0)
        })

        # DataFrame 2 (Volatile): yhat = 200
        df2 = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(465, 200.0),
            'yhat_lower': np.full(465, 190.0),
            'yhat_upper': np.full(465, 210.0)
        })

        m1 = MagicMock()
        m1.predict.return_value = df1
        m1.make_future_dataframe.return_value = pd.DataFrame({'ds': future_dates})

        m2 = MagicMock()
        m2.predict.return_value = df2
        m2.make_future_dataframe.return_value = pd.DataFrame({'ds': future_dates})

        mock_prophet.side_effect = [m1, m2]

        # Run with 2 models
        res = forecast_prophet_ensemble(self.df, ["Standard", "Volatile (Trend Chaser)"], periods=30)

        # Expected Average: (100 + 200) / 2 = 150
        # Since input is constant, result is constant 150
        self.assertAlmostEqual(res['yhat'].iloc[0], 150.0)
        self.assertAlmostEqual(res['yhat_lower'].iloc[0], 140.0)
        self.assertAlmostEqual(res['yhat_upper'].iloc[0], 160.0)

    @patch('modules.cryptop_crypto_circus_models.Prophet')
    def test_sentiment_adjustment(self, mock_prophet):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_prophet.return_value = mock_model_instance

        # 100 history + 365 future = 465
        future_dates = pd.date_range(start='2023-01-01', periods=465)

        # Constant forecast of 100
        df_base = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(465, 100.0),
            'yhat_lower': np.full(465, 90.0),
            'yhat_upper': np.full(465, 110.0)
        })

        mock_model_instance.predict.return_value = df_base
        mock_model_instance.make_future_dataframe.return_value = pd.DataFrame({'ds': future_dates})

        # Run with Sentiment Score = 0.5 (Positive)
        # Result is now only future (30 days).
        # Ramp starts at 0 at index 0 (start of forecast) and goes to 0.5*0.1 = 0.05 at index -1.

        res = forecast_prophet_ensemble(self.df, ["Standard"], periods=30, sentiment_score=0.5)

        # Check start of forecast (index 0)
        # Should be 100 * (1.0 + 0) = 100
        self.assertEqual(res['yhat'].iloc[0], 100.0)

        # Check end of forecast (index -1)
        # Should be 100 * (1.0 + 0.05) = 105
        self.assertAlmostEqual(res['yhat'].iloc[-1], 105.0, places=1)

        # Run with Sentiment Score = -0.5 (Negative)
        # End value = 100 * (1.0 - 0.05) = 95

        res_neg = forecast_prophet_ensemble(self.df, ["Standard"], periods=30, sentiment_score=-0.5)
        self.assertAlmostEqual(res_neg['yhat'].iloc[-1], 95.0, places=1)

if __name__ == '__main__':
    unittest.main()
