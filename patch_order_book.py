import re

with open("streamlit_app/modules/exchange_manager.py", "r") as f:
    content = f.read()

ob_func = """
    def get_order_book(self, symbol, limit=100):
        \"\"\"
        Technical Improvement 4: Fetch L2 Order Book depth for analysis.
        \"\"\"
        if not self.exchange:
            return None, "Not connected to any exchange."
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return order_book, "Success"
        except Exception as e:
            self.logger.error(f"Failed to fetch order book: {str(e)}", exc_info=True)
            return None, f"Failed to fetch order book: {str(e)}"
"""

if "def get_order_book" not in content:
    # Insert before get_balance or similar
    content = content.replace("    def get_balance(self):", ob_func + "\n    def get_balance(self):")

with open("streamlit_app/modules/exchange_manager.py", "w") as f:
    f.write(content)
