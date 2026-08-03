import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# We need to add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

def get_helper_module():
    """Helper to reload the module with mocked streamlit"""
    if 'modules.cryptop_crypto_fortune_teller_helper' in sys.modules:
        del sys.modules['modules.cryptop_crypto_fortune_teller_helper']
    import modules.cryptop_crypto_fortune_teller_helper as helper
    return helper

def test_get_historical_prices_dos_prevention():
    """

    Verify that get_historical_prices handles large 'days' values gracefully
    without raising OutOfBoundsTimedelta or OverflowError (DoS prevention).
    """
    # Mock streamlit using patch.dict on sys.modules
    mock_st = MagicMock()

    # Handle both @st.cache_data and @st.cache_data(ttl=...) usage
    def mock_cache_data(func=None, **kwargs):
        if func:
            return func
        return lambda f: f

    mock_st.cache_data = mock_cache_data

    with patch.dict(sys.modules, {'streamlit': mock_st}):
        helper = get_helper_module()

        # Mock the internal cache function
        # We must patch the function on the RELOADED module object
        with patch.object(helper, '_fetch_historical_prices_cached') as mock_fetch:
            # Create a dummy dataframe with some history
            #Ensure naive timestamps
            dates = pd.date_range(end=pd.Timestamp.now('UTC').replace(tzinfo=None), periods=100)
            df = pd.DataFrame({'close': range(100)}, index=dates)
            mock_fetch.return_value = df

            # Test case 1: days > MAX_HISTORY_DAYS
            large_days = helper.MAX_HISTORY_DAYS + 1000
            result = helper.get_historical_prices('bitcoin', days=large_days)
            assert not result.empty
            assert len(result) == 100

            # Test case 2: Extremely large days
            huge_days = 200000
            try:
                result = helper.get_historical_prices('bitcoin', days=huge_days)
                assert not result.empty
            except Exception as e:
                pytest.fail(f"get_historical_prices crashed with large input: {e}")

            # Test case 3: Negative days
            result = helper.get_historical_prices('bitcoin', days=-1)
            assert not result.empty

def test_get_historical_ohlc_dos_prevention():
    """

    Verify that get_historical_ohlc handles large 'days' values gracefully.
    """
    mock_st = MagicMock()

    def mock_cache_data(func=None, **kwargs):
        if func:
            return func
        return lambda f: f

    mock_st.cache_data = mock_cache_data

    with patch.dict(sys.modules, {'streamlit': mock_st}):
        helper = get_helper_module()

        with patch.object(helper, '_fetch_historical_ohlc_cached') as mock_fetch:
            dates = pd.date_range(end=pd.Timestamp.now('UTC').replace(tzinfo=None), periods=50)
            df = pd.DataFrame({
                'open': range(50), 'high': range(50), 'low': range(50), 'close': range(50)
            }, index=dates)
            mock_fetch.return_value = df

            huge_days = 200000
            try:
                result = helper.get_historical_ohlc('bitcoin', days=huge_days)
                assert not result.empty
            except Exception as e:
                pytest.fail(f"get_historical_ohlc crashed with large input: {e}")

def test_max_history_days_constant():
    """
    Verify the constant is set to a safe value.
    """
    # Use standard import for constant check (no need to mock streamlit if just checking constant)
    # But to be safe, we can use the helper
    mock_st = MagicMock()

    def mock_cache_data(func=None, **kwargs):
        if func:
            return func
        return lambda f: f

    mock_st.cache_data = mock_cache_data

    with patch.dict(sys.modules, {'streamlit': mock_st}):
        helper = get_helper_module()
        assert helper.MAX_HISTORY_DAYS < 106752
        assert helper.MAX_HISTORY_DAYS > 365
