import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock streamlit before importing the module
sys.modules['streamlit'] = MagicMock()

# Import the module under test
# We need to add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))
from modules.cryptop_crypto_fortune_teller_helper import get_historical_prices, get_historical_ohlc, MAX_HISTORY_DAYS

def test_get_historical_prices_dos_prevention():
    """
    Sentinel Security Test:
    Verify that get_historical_prices handles large 'days' values gracefully
    without raising OutOfBoundsTimedelta or OverflowError (DoS prevention).
    """
    # Mock the internal cache function to return a valid dataframe
    with patch('modules.cryptop_crypto_fortune_teller_helper._fetch_historical_prices_cached') as mock_fetch:
        # Create a dummy dataframe with some history
        dates = pd.date_range(end=pd.Timestamp.utcnow(), periods=100)
        df = pd.DataFrame({'close': range(100)}, index=dates)
        mock_fetch.return_value = df

        # Test case 1: days > MAX_HISTORY_DAYS
        # Should return full dataframe (safe fallback)
        large_days = MAX_HISTORY_DAYS + 1000
        result = get_historical_prices('bitcoin', days=large_days)
        assert not result.empty
        assert len(result) == 100

        # Test case 2: Extremely large days (overflow pd.Timedelta)
        huge_days = 200000 # ~547 years
        try:
            result = get_historical_prices('bitcoin', days=huge_days)
            assert not result.empty
        except Exception as e:
            pytest.fail(f"get_historical_prices crashed with large input: {e}")

        # Test case 3: Negative days (should return full df or handle gracefully)
        result = get_historical_prices('bitcoin', days=-1)
        assert not result.empty # Currently logic returns full df if < 0

def test_get_historical_ohlc_dos_prevention():
    """
    Sentinel Security Test:
    Verify that get_historical_ohlc handles large 'days' values gracefully.
    """
    with patch('modules.cryptop_crypto_fortune_teller_helper._fetch_historical_ohlc_cached') as mock_fetch:
        dates = pd.date_range(end=pd.Timestamp.utcnow(), periods=50)
        df = pd.DataFrame({
            'open': range(50), 'high': range(50), 'low': range(50), 'close': range(50)
        }, index=dates)
        mock_fetch.return_value = df

        huge_days = 200000
        try:
            result = get_historical_ohlc('bitcoin', days=huge_days)
            assert not result.empty
        except Exception as e:
            pytest.fail(f"get_historical_ohlc crashed with large input: {e}")

def test_max_history_days_constant():
    """
    Verify the constant is set to a safe value.
    """
    # Pandas Timedelta overflow is approx 106752 days
    assert MAX_HISTORY_DAYS < 106752
    assert MAX_HISTORY_DAYS > 365 # Should be reasonably large
