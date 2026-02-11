import requests
import pandas as pd

class FreqtradeManager:
    def __init__(self, api_url, username, password):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.access_token = None

    def _headers(self):
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        return {}

    def login(self):
        """
        Authenticate with Freqtrade API.
        """
        try:
            auth_url = f"{self.api_url}/api/v1/token/login"
            # Using data= for form-encoded or json= ? Freqtrade usually uses Basic Auth for token or form.
            # Let's try standard approach for Freqtrade API
            # Note: Freqtrade API typically uses Basic Auth to get the token, or just Basic Auth for requests.
            # But the modern one uses JWT.
            resp = requests.post(auth_url, auth=(self.username, self.password), timeout=5)

            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get('access_token')
                return True, "Login successful"
            else:
                return False, f"Login failed: {resp.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_status(self):
        """
        Get bot status.
        """
        try:
            resp = requests.get(f"{self.api_url}/api/v1/status", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), None
            return None, f"Error: {resp.status_code}"
        except Exception as e:
            return None, str(e)

    def start_bot(self):
        try:
            resp = requests.post(f"{self.api_url}/api/v1/start", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), "Bot started"
            return None, f"Error: {resp.json().get('status', 'Unknown')}"
        except Exception as e:
            return None, str(e)

    def stop_bot(self):
        try:
            resp = requests.post(f"{self.api_url}/api/v1/stop", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), "Bot stopped"
            return None, f"Error: {resp.json().get('status', 'Unknown')}"
        except Exception as e:
            return None, str(e)

    def get_profit(self):
        try:
            resp = requests.get(f"{self.api_url}/api/v1/profit", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), None
            return None, f"Error: {resp.status_code}"
        except Exception as e:
            return None, str(e)

    def get_whitelist(self):
        try:
            resp = requests.get(f"{self.api_url}/api/v1/whitelist", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json().get('whitelist', []), None
            return None, f"Error: {resp.status_code}"
        except Exception as e:
            return None, str(e)
