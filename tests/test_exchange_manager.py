import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from modules.exchange_manager import ExchangeManager

class TestExchangeManager(unittest.TestCase):
    def setUp(self):
        self.manager = ExchangeManager()

    @patch('modules.exchange_manager.ccxt')
    def test_connect_success(self, mock_ccxt):
        # Mock the exchange class
        mock_exchange = MagicMock()
        mock_exchange.checkRequiredCredentials.return_value = True
        mock_exchange.load_markets.return_value = {'BTC/USDT': {}}

        # Configure the getattr on ccxt to return our mock class
        mock_ccxt.binance.return_value = mock_exchange

        success, msg = self.manager.connect('binance', 'key', 'secret')

        self.assertTrue(success)
        self.assertIn("Successfully connected", msg)
        self.assertIsNotNone(self.manager.exchange)

    @patch('modules.exchange_manager.ccxt')
    def test_connect_failure(self, mock_ccxt):
        # Simulate an exception during connection
        mock_ccxt.binance.side_effect = Exception("Connection failed")

        success, msg = self.manager.connect('binance', 'key', 'secret')

        self.assertFalse(success)
        self.assertIn("Connection error", msg)
        self.assertIsNone(self.manager.exchange)

    def test_get_balance_no_connection(self):
        df, err = self.manager.get_balance()
        self.assertIsNone(df)
        self.assertEqual(err, "Not connected to any exchange.")

    def test_create_order_no_connection(self):
        order, msg = self.manager.create_order('BTC/USDT', 'limit', 'buy', 1.0, 50000)
        self.assertIsNone(order)
        self.assertEqual(msg, "Not connected.")
