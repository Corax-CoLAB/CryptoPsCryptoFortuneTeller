import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import sys
import os

# Mock streamlit before importing modules
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit'].cache_data = lambda func=None, **kwargs: (lambda f: f) if func is None else func
sys.modules['streamlit'].error = MagicMock()

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_models import forecast_prophet_ensemble, get_prophet_config

class TestProphetEnsemble(unittest.TestCase):

    def setUp(self):
        # Create dummy data
        self.df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=100),
            'close': np.linspace(100, 200, 100)
        }).set_index('date')

    @patch('modules.cryptop_crypto_fortune_teller_models.Prophet')
    def test_single_model(self, mock_prophet):
        # Setup mock return
        mock_model_instance = MagicMock()
        mock_prophet.return_value = mock_model_instance

        # Mock predict return
        future_dates = pd.date_range(start='2023-01-01', periods=130) # 100 hist + 30 forecast
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.linspace(100, 230, 130),
            'yhat_lower': np.linspace(90, 220, 130),
            'yhat_upper': np.linspace(110, 240, 130)
        })
        mock_model_instance.make_future_dataframe.return_value = pd.DataFrame({'ds': future_dates})
        mock_model_instance.predict.return_value = forecast_df

        # Run
        res = forecast_prophet_ensemble(self.df, ["Standard"], periods=30)

        # Verify
        self.assertEqual(len(res), 130)
        self.assertIn('yhat', res.columns)
        mock_prophet.assert_called() # Should be called

    @patch('modules.cryptop_crypto_fortune_teller_models.Prophet')
    def test_ensemble_averaging(self, mock_prophet):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_prophet.return_value = mock_model_instance

        # We need to simulate different returns for different calls if possible,
        # but since we are mocking the class, every instantiation returns the same mock instance.
        # We can use side_effect on predict, but the instance is created fresh each time inside the function.
        # However, mock_prophet is the Class constructor.

        # Let's make the Class constructor return *different* instances or instances that behave differently?
        # Simpler: The function instantiates Prophet() -> returns m1. Then m1.fit(). m1.predict().
        # Next call: Prophet() -> returns m2.

        # If we want to verify averaging, we need distinct values.
        # Let's set side_effect of predict to return different dataframes.

        future_dates = pd.date_range(start='2023-01-01', periods=130)

        # DataFrame 1 (Standard): yhat = 100
        df1 = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(130, 100.0),
            'yhat_lower': np.full(130, 90.0),
            'yhat_upper': np.full(130, 110.0)
        })

        # DataFrame 2 (Volatile): yhat = 200
        df2 = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(130, 200.0),
            'yhat_lower': np.full(130, 190.0),
            'yhat_upper': np.full(130, 210.0)
        })

        # We need to hook into the instance.predict method.
        # Since the function creates a new instance each time: `model = Prophet(...)`
        # We can make mock_prophet.side_effect return [mock_inst1, mock_inst2]

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
        self.assertAlmostEqual(res['yhat'].iloc[0], 150.0)
        self.assertAlmostEqual(res['yhat_lower'].iloc[0], 140.0)
        self.assertAlmostEqual(res['yhat_upper'].iloc[0], 160.0)

    @patch('modules.cryptop_crypto_fortune_teller_models.Prophet')
    def test_sentiment_adjustment(self, mock_prophet):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_prophet.return_value = mock_model_instance

        future_dates = pd.date_range(start='2023-01-01', periods=130) # 100 hist + 30 future

        # Constant forecast of 100
        df_base = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.full(130, 100.0),
            'yhat_lower': np.full(130, 90.0),
            'yhat_upper': np.full(130, 110.0)
        })

        mock_model_instance.predict.return_value = df_base
        mock_model_instance.make_future_dataframe.return_value = pd.DataFrame({'ds': future_dates})

        # Run with Sentiment Score = 0.5 (Positive)
        # Our logic: last 30 days get linear ramp up to (score * 0.10).
        # Max increase = 0.5 * 0.10 = 0.05 (5%)
        # So last value should be 100 * 1.05 = 105.
        # First value (historical) should be 100.

        res = forecast_prophet_ensemble(self.df, ["Standard"], periods=30, sentiment_score=0.5)

        # Check historical (index 0)
        self.assertEqual(res['yhat'].iloc[0], 100.0)

        # Check future (last index)
        # Note: floating point precision
        self.assertAlmostEqual(res['yhat'].iloc[-1], 105.0, places=1)

        # Run with Sentiment Score = -0.5 (Negative)
        # Max decrease = -0.5 * 0.10 = -0.05
        # Last value = 100 * 0.95 = 95

        # Need to reset mock side effect if we used it, but here return_value is static which is fine
        res_neg = forecast_prophet_ensemble(self.df, ["Standard"], periods=30, sentiment_score=-0.5)
        self.assertAlmostEqual(res_neg['yhat'].iloc[-1], 95.0, places=1)

if __name__ == '__main__':
    unittest.main()
