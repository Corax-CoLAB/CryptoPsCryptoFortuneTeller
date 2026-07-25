import sys
import os
import pytest

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.cryptop_crypto_fortune_teller_helper import cg

def test_coingecko_timeout_configuration():
    """

    Verify that CoinGeckoAPI client has a reasonable timeout configured
    to prevent DoS / hanging processes.
    """
    assert cg.request_timeout == 20, "CoinGeckoAPI timeout should be set to 20 seconds to prevent hanging."
    assert cg.request_timeout < 120, "Timeout is too long (default 120s)."
