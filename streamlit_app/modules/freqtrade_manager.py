import requests
import pandas as pd

class FreqtradeManager:
    def __init__(self, api_url, username, password):
        self._api_url = api_url.rstrip('/')
        self._username = username
        self._password = password
        self._access_token = None

    def __repr__(self):
        token_status = "Set" if self._access_token else "None"
        return f"FreqtradeManager(api_url='{self._api_url}', username='{self._username}', access_token={token_status})"

    def __str__(self):
        return self.__repr__()

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove sensitive info
        state['_password'] = '***'
        state['_access_token'] = '***'
        return state

    def _headers(self):
        if self._access_token:
            return {'Authorization': f'Bearer {self._access_token}'}
        return {}

    def login(self):
        """
        Authenticate with Freqtrade API.
        """
        try:
            auth_url = f"{self._api_url}/api/v1/token/login"
            # Using data= for form-encoded or json= ? Freqtrade usually uses Basic Auth for token or form.
            # Let's try standard approach for Freqtrade API
            # Note: Freqtrade API typically uses Basic Auth to get the token, or just Basic Auth for requests.
            # But the modern one uses JWT.
            resp = requests.post(auth_url, auth=(self._username, self._password), timeout=5)

            if resp.status_code == 200:
                data = resp.json()
                self._access_token = data.get('access_token')
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
            resp = requests.get(f"{self._api_url}/api/v1/status", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), None
            return None, f"Error: {resp.status_code}"
        except Exception as e:
            return None, str(e)

    def start_bot(self):
        try:
            resp = requests.post(f"{self._api_url}/api/v1/start", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), "Bot started"
            return None, f"Error: {resp.json().get('status', 'Unknown')}"
        except Exception as e:
            return None, str(e)

    def stop_bot(self):
        try:
            resp = requests.post(f"{self._api_url}/api/v1/stop", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), "Bot stopped"
            return None, f"Error: {resp.json().get('status', 'Unknown')}"
        except Exception as e:
            return None, str(e)

    def get_profit(self):
        try:
            resp = requests.get(f"{self._api_url}/api/v1/profit", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json(), None
            return None, f"Error: {resp.status_code}"
        except Exception as e:
            return None, str(e)

    def get_whitelist(self):
        try:
            resp = requests.get(f"{self._api_url}/api/v1/whitelist", headers=self._headers(), timeout=5)
            if resp.status_code == 200:
                return resp.json().get('whitelist', []), None
            return None, f"Error: {resp.status_code}"
        except Exception as e:
            return None, str(e)
