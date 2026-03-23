import re
import os

with open("streamlit_app/modules/cryptop_crypto_circus_helper.py", "r") as f:
    content = f.read()

# 1. Add requests.adapters import
if "from requests.adapters import HTTPAdapter, Retry" not in content:
    content = content.replace("import requests", "import requests\nfrom requests.adapters import HTTPAdapter, Retry\nimport time")

# 2. Add the get_session() function
session_func = """
def get_session():
    \"\"\"
    Technical Improvement 1: Create a robust requests Session with retries and backoff
    to handle intermittent API failures.
    \"\"\"
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Global robust session
req_session = get_session()

# Replace cg direct requests to have retry wrapping where manual
def cg_retry_call(func, *args, retries=3, delay=1, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise e
"""
if "def get_session():" not in content:
    content = content.replace("cg.request_timeout = 20  # Sentinel: Enforce timeout to prevent hanging",
                              "cg.request_timeout = 20  # Sentinel: Enforce timeout to prevent hanging\n" + session_func)

# 3. Replace requests.get with req_session.get in _fetch_historical_prices_cached
content = content.replace("r = requests.get(url, params=params, timeout=3)", "r = req_session.get(url, params=params, timeout=5)")
content = content.replace("requests.get(url, headers=headers, timeout=20)", "req_session.get(url, headers=headers, timeout=20)")

# 4. Wrap CoinGeckoAPI calls with retry
cg_calls = [
    "cg.get_coins_list()",
    "cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days, timeout=3)",
    "cg.get_coin_ohlc_by_id(id=coin_id, vs_currency=vs_currency, days=days)",
    "cg.get_coin_by_id(",
    "cg.get_search_trending()",
    "cg.get_price(",
    "cg.get_coins_markets(",
    "cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=days)"
]

content = content.replace("cg.get_coins_list()", "cg_retry_call(cg.get_coins_list)")
content = content.replace("cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days, timeout=3)", "cg_retry_call(cg.get_coin_market_chart_by_id, id=coin_id, vs_currency=vs_currency, days=days, timeout=3)")
content = content.replace("cg.get_coin_ohlc_by_id(id=coin_id, vs_currency=vs_currency, days=days)", "cg_retry_call(cg.get_coin_ohlc_by_id, id=coin_id, vs_currency=vs_currency, days=days)")
content = content.replace("cg.get_search_trending()", "cg_retry_call(cg.get_search_trending)")
content = content.replace("cg.get_price(ids=coin_ids, vs_currencies=vs_currencies)", "cg_retry_call(cg.get_price, ids=coin_ids, vs_currencies=vs_currencies)")
content = content.replace("cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=100, page=1)", "cg_retry_call(cg.get_coins_markets, vs_currency='usd', order='market_cap_desc', per_page=100, page=1)")
content = content.replace("cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=limit, page=1)", "cg_retry_call(cg.get_coins_markets, vs_currency='usd', order='market_cap_desc', per_page=limit, page=1)")
content = content.replace("cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=days)", "cg_retry_call(cg.get_coin_market_chart_by_id, id=coin_id, vs_currency='usd', days=days)")

# Replace multi-line get_coin_by_id manually
import re
content = re.sub(
    r"cg\.get_coin_by_id\(\s*id=coin_id,\s*localization='false',\s*tickers='false',\s*market_data='false',\s*community_data='true',\s*developer_data='true',\s*sparkline='false'\s*\)",
    r"cg_retry_call(cg.get_coin_by_id, id=coin_id, localization='false', tickers='false', market_data='false', community_data='true', developer_data='true', sparkline='false')",
    content
)

content = re.sub(
    r"cg\.get_coin_by_id\(\s*id=coin_id,\s*localization='false',\s*tickers='false',\s*market_data='true',\s*community_data='false',\s*developer_data='false',\s*sparkline='false'\s*\)",
    r"cg_retry_call(cg.get_coin_by_id, id=coin_id, localization='false', tickers='false', market_data='true', community_data='false', developer_data='false', sparkline='false')",
    content
)

with open("streamlit_app/modules/cryptop_crypto_circus_helper.py", "w") as f:
    f.write(content)

print("Helper updated successfully")
