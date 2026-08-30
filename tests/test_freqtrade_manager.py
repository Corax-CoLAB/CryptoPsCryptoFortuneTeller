import unittest
from unittest.mock import MagicMock, patch
from modules.freqtrade_manager import FreqtradeManager

class TestFreqtradeManager(unittest.TestCase):
    def setUp(self):
        self.manager = FreqtradeManager("http://localhost:8080", "user", "pass")

    @patch('modules.freqtrade_manager.requests.post')
    def test_login_success(self, mock_post):
        # Mock successful login response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "fake_token", "refresh_token": "fake_refresh"}
        mock_post.return_value = mock_response

        success, msg = self.manager.login()

        self.assertTrue(success)
        self.assertEqual(self.manager._access_token, "fake_token")

    @patch('modules.freqtrade_manager.requests.post')
    def test_login_failure(self, mock_post):
        # Mock failed login response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        success, msg = self.manager.login()

        self.assertFalse(success)
        self.assertIn("Login failed", msg)

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_status_success(self, mock_get):
        self.manager._access_token = "fake_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"state": "running"}
        mock_get.return_value = mock_response

        status, err = self.manager.get_status()

        self.assertEqual(status, {"state": "running"})
        self.assertIsNone(err)

    @patch('modules.freqtrade_manager.requests.post')
    def test_start_bot_success(self, mock_post):
        self.manager._access_token = "fake_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "started"}
        mock_post.return_value = mock_response

        res, msg = self.manager.start_bot()

        self.assertEqual(res, {"status": "started"})
