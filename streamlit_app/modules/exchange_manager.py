import ccxt
import pandas as pd

class ExchangeManager:
    def __init__(self):
        self.exchange = None
        self.exchange_id = None

    def connect(self, exchange_id, api_key, api_secret, password=None):
        """
        Connect to an exchange using CCXT.
        """
        try:
            exchange_class = getattr(ccxt, exchange_id)
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            }
            if password:
                config['password'] = password

            self.exchange = exchange_class(config)
            self.exchange.checkRequiredCredentials()
            self.exchange.load_markets()
            self.exchange_id = exchange_id
            return True, f"Successfully connected to {exchange_id.upper()}"
        except Exception as e:
            self.exchange = None
            return False, f"Connection error: {str(e)}"

    def get_balance(self):
        """
        Fetch balance and return as a DataFrame.
        """
        if not self.exchange:
            return None, "Not connected to any exchange."

        try:
            balance = self.exchange.fetch_balance()
            total_balance = balance.get('total', {})

            # Filter for non-zero balances
            data = [{'Currency': k, 'Total': v} for k, v in total_balance.items() if v > 0]

            if not data:
                return pd.DataFrame(), None

            df = pd.DataFrame(data)
            return df, None
        except Exception as e:
            return None, f"Error fetching balance: {str(e)}"

    def create_order(self, symbol, type, side, amount, price=None):
        """
        Create a trade order.
        """
        if not self.exchange:
            return None, "Not connected."

        try:
            # Check if symbol is valid
            if symbol not in self.exchange.markets:
                 return None, f"Symbol {symbol} not found on {self.exchange_id}."

            if type == 'limit':
                if price is None:
                    return None, "Price is required for limit orders."
                order = self.exchange.create_order(symbol, type, side, amount, price)
            else:
                order = self.exchange.create_order(symbol, type, side, amount)

            return order, "Order placed successfully!"
        except Exception as e:
            return None, f"Order failed: {str(e)}"

    def fetch_open_orders(self, symbol=None):
        """
        Fetch open orders.
        """
        if not self.exchange:
            return None, "Not connected."

        try:
            orders = self.exchange.fetch_open_orders(symbol)
            if not orders:
                return pd.DataFrame(), None

            # Simplify for display
            simple_orders = []
            for o in orders:
                simple_orders.append({
                    'id': o['id'],
                    'datetime': o['datetime'],
                    'symbol': o['symbol'],
                    'type': o['type'],
                    'side': o['side'],
                    'price': o['price'],
                    'amount': o['amount'],
                    'filled': o['filled'],
                    'status': o['status']
                })

            return pd.DataFrame(simple_orders), None
        except Exception as e:
            return None, f"Error fetching orders: {str(e)}"
