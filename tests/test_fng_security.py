import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock streamlit before importing the module to bypass caching
sys.modules['streamlit'] = MagicMock()
# Ensure cache_data acts as a pass-through decorator
sys.modules['streamlit'].cache_data = lambda func=None, **kwargs: (lambda f: f) if func is None else func

import requests

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

# Reload module to apply mock
if 'modules.cryptop_crypto_fortune_teller_helper' in sys.modules:
    del sys.modules['modules.cryptop_crypto_fortune_teller_helper']

from modules.cryptop_crypto_fortune_teller_helper import get_fear_and_greed_index

class TestFnGSecurity(unittest.TestCase):

    @patch('modules.cryptop_crypto_fortune_teller_helper.req_session.get')
    def test_fng_raise_for_status(self, mock_get):
        """
        Sentinel Security Test:
        Verify that get_fear_and_greed_index calls raise_for_status() on the response object.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': [{'value': '50', 'value_classification': 'Neutral', 'timestamp': '123'}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        get_fear_and_greed_index()

        if not mock_response.raise_for_status.called:
             self.fail("Security Enhancement Required: response.raise_for_status() was not called.")

    @patch('modules.cryptop_crypto_fortune_teller_helper.req_session.get')
    def test_fng_user_agent(self, mock_get):
        """
        Sentinel Security Test:
        Verify that a User-Agent header is sent.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response

        get_fear_and_greed_index()

        if not mock_get.called:
            self.fail("requests.get was not called (cache issue?)")

        args, kwargs = mock_get.call_args
        headers = kwargs.get('headers', {})

        if 'User-Agent' not in headers:
             self.fail("Security Enhancement Required: Missing User-Agent header in requests.get call.")

        self.assertIn('CryptoFortuneTeller', headers['User-Agent'], "User-Agent should be descriptive.")

    @patch('modules.cryptop_crypto_fortune_teller_helper.req_session.get')
    def test_fng_timeout_consistency(self, mock_get):
        """
        Sentinel Security Test:
        Verify timeout is consistent with application standard (20s).
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response

        get_fear_and_greed_index()

        args, kwargs = mock_get.call_args
        timeout = kwargs.get('timeout')

        self.assertEqual(timeout, 20, "Timeout should be 20 seconds for consistency.")

if __name__ == '__main__':
    unittest.main()
