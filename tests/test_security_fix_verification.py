import unittest
from unittest.mock import MagicMock
from streamlit_app.modules.freqtrade_manager import FreqtradeManager
from streamlit_app.modules.exchange_manager import ExchangeManager
import ccxt

class TestSecurityFixVerification(unittest.TestCase):
    def test_freqtrade_manager_repr_masking(self):
        """
        Verify that FreqtradeManager masks sensitive information in __repr__ and __str__.
        """
        manager = FreqtradeManager("http://localhost:8080", "user", "super_secret_password")
        manager.access_token = "sensitive_access_token"

        repr_str = repr(manager)
        str_str = str(manager)

        # Check if password is leaked
        self.assertNotIn("super_secret_password", repr_str, "Password leaked in __repr__")
        self.assertNotIn("super_secret_password", str_str, "Password leaked in __str__")

        # Check if access token is leaked
        self.assertNotIn("sensitive_access_token", repr_str, "Access token leaked in __repr__")
        self.assertNotIn("sensitive_access_token", str_str, "Access token leaked in __str__")

        # Ensure it's a custom repr, not default object at ...
        self.assertNotIn("object at 0x", repr_str, "Default __repr__ used")

        # Ensure it contains useful info
        self.assertIn("FreqtradeManager", repr_str)
        self.assertIn("http://localhost:8080", repr_str)

    def test_exchange_manager_repr_masking(self):
        """
        Verify that ExchangeManager masks sensitive information in __repr__ and __str__.
        """
        manager = ExchangeManager()
        # Mock the exchange object to simulate one with credentials
        manager.exchange = MagicMock()
        manager.exchange.apiKey = "visible_api_key"
        manager.exchange.secret = "super_secret_api_key"
        manager.exchange_id = "binance"

        repr_str = repr(manager)
        str_str = str(manager)

        self.assertNotIn("super_secret_api_key", repr_str, "Secret leaked in __repr__")
        self.assertNotIn("super_secret_api_key", str_str, "Secret leaked in __str__")

        # Ensure it's a custom repr
        self.assertNotIn("object at 0x", repr_str, "Default __repr__ used")

        self.assertIn("ExchangeManager", repr_str)
        self.assertIn("binance", repr_str)

if __name__ == '__main__':
    unittest.main()
