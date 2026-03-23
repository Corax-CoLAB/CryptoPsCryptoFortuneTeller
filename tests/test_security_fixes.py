import pytest
import sys
import os
import importlib
from unittest.mock import patch, MagicMock

# Import from helper. Note: validate_coin_id might not exist yet if running TDD,
# but we assume it will be added.
# We need to ensure the module is importable for the reload to work.
import streamlit_app.modules.cryptop_crypto_circus_helper

def test_security_fixes_isolated():
    """
    Test security fixes in isolation by mocking streamlit and reloading the helper module.
    This avoids interference from Streamlit's caching mechanism and other tests.
    """
    # Create a mock for streamlit that handles cache_data decorator
    mock_st = MagicMock()
    # Ensure cache_data is a pass-through decorator
    mock_st.cache_data = lambda *args, **kwargs: (lambda func: func)

    with patch.dict(sys.modules, {'streamlit': mock_st}):
        # Reload helper to use the mocked streamlit
        from streamlit_app.modules import cryptop_crypto_circus_helper
        importlib.reload(cryptop_crypto_circus_helper)

        from streamlit_app.modules.cryptop_crypto_circus_helper import (
            get_historical_prices,
            get_historical_ohlc,
            get_coin_metrics,
            validate_coin_id
        )

        # Mock the CoinGeckoAPI client in the reloaded module
        mock_cg = MagicMock()
        cryptop_crypto_circus_helper.cg = mock_cg

        # --- TEST 1: validate_coin_id ---
        assert validate_coin_id("bitcoin") is True
        assert validate_coin_id("ethereum") is True
        assert validate_coin_id("polkadot.js") is True
        assert validate_coin_id("bitcoin-cash") is True
        assert validate_coin_id("0x") is True
        assert validate_coin_id("1inch") is True
        assert validate_coin_id("aave_v2") is True

        assert validate_coin_id("../bitcoin") is False
        assert validate_coin_id("bitcoin/ethereum") is False
        assert validate_coin_id("bitcoin\\ethereum") is False
        assert validate_coin_id("bitcoin;rm -rf") is False
        assert validate_coin_id("<script>") is False
        assert validate_coin_id(123) is False
        assert validate_coin_id(None) is False

        # --- TEST 2: get_historical_prices ---
        import time
        now_ms = int(time.time() * 1000)
        mock_cg.get_coin_market_chart_by_id.return_value = {'prices': [[now_ms, 50000]]}

        # Invalid
        df = get_historical_prices("../malicious")
        assert df.empty
        mock_cg.get_coin_market_chart_by_id.assert_not_called()

        # Valid
        df = get_historical_prices("bitcoin")
        mock_cg.get_coin_market_chart_by_id.assert_called_once()
        assert not df.empty

        mock_cg.reset_mock()

        # --- TEST 3: get_historical_ohlc ---
        mock_cg.get_coin_ohlc_by_id.return_value = [[now_ms, 100, 110, 90, 105]]

        # Invalid
        df = get_historical_ohlc("foo/bar")
        assert df.empty
        mock_cg.get_coin_ohlc_by_id.assert_not_called()

        # Valid
        df = get_historical_ohlc("litecoin")
        mock_cg.get_coin_ohlc_by_id.assert_called_once()
        assert not df.empty

        mock_cg.reset_mock()

        # --- TEST 4: get_coin_metrics ---
        mock_cg.get_coin_by_id.return_value = {}

        # Invalid
        metrics = get_coin_metrics("script<alert>")
        assert metrics == {}
        mock_cg.get_coin_by_id.assert_not_called()

        # Valid
        metrics = get_coin_metrics("ripple")
        mock_cg.get_coin_by_id.assert_called_once()
