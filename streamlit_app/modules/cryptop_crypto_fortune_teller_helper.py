# cryptop_crypto_fortune_teller_helper.py
import pandas as pd
import numpy as np
from pycoingecko import CoinGeckoAPI
import streamlit as st
import requests
import concurrent.futures

# Initialize CoinGecko client (public demo API)
cg = CoinGeckoAPI()

@st.cache_data(ttl=86400) # Cache list for 24 hours
def get_coin_list():
    """
    Fetch list of all supported coins from CoinGecko.
    Returns a DataFrame with columns [id, symbol, name].
    """
    try:
        coins = cg.get_coins_list()  # get list of coins with id, symbol, name
        df_coins = pd.DataFrame(coins)
        return df_coins
    except Exception as e:
        st.error(f"Error fetching coin list: {e}")
        return pd.DataFrame(columns=['id', 'symbol', 'name'])

@st.cache_data(ttl=3600) # Cache prices for 1 hour
def get_historical_prices(coin_id, vs_currency='usd', days=365):
    """
    Fetch historical market data (prices) for a coin.
    Returns DataFrame with date index and 'close' prices.
    """
    try:
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
        # 'prices' is list of [timestamp, price]
        prices = data.get('prices', [])
        df = pd.DataFrame(prices, columns=['timestamp', 'close'])
        # convert ms timestamp to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        df = df[['close']]
        return df
    except Exception as e:
        st.error(f"Error fetching historical prices: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_historical_ohlc(coin_id, vs_currency='usd', days=30):
    """
    Fetch historical OHLC data for a coin.
    Returns DataFrame with date index and columns ['open','high','low','close'].
    Uses CoinGecko OHLC endpoint (30-day candlesticks).
    """
    try:
        ohlc_data = cg.get_coin_ohlc_by_id(id=coin_id, vs_currency=vs_currency, days=days)
        df = pd.DataFrame(ohlc_data, columns=['timestamp','open','high','low','close'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        df = df[['open','high','low','close']]
        return df
    except Exception as e:
        st.error(f"Error fetching OHLC data: {e}")
        return pd.DataFrame()

def compute_volatility(df, window=14):
    """
    Compute volatility indicators: rolling standard deviation and Average True Range (ATR).
    Returns DataFrame with columns ['rolling_std', 'ATR'].
    ATR is calculated using high, low, and previous close (Welles Wilder method).
    """
    if 'close' not in df or df.empty:
         return pd.DataFrame()

    vol = pd.DataFrame(index=df.index)
    vol['rolling_std'] = df['close'].rolling(window).std()
    # Compute ATR if high/low available
    if 'high' in df and 'low' in df:
        high_low = df['high'] - df['low']
        high_pc = (df['high'] - df['close'].shift(1)).abs()
        low_pc = (df['low'] - df['close'].shift(1)).abs()
        tr = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
        vol['ATR'] = tr.rolling(window).mean()
    else:
        vol['ATR'] = np.nan
    return vol

@st.cache_data(ttl=3600)
def get_coin_metrics(coin_id):
    """
    Fetch additional metrics for a coin: community and developer data.
    Uses CoinGecko API to get community (social) and developer stats.
    """
    try:
        data = cg.get_coin_by_id(id=coin_id, localization='false', tickers='false',
                                 market_data='false', community_data='true', developer_data='true', sparkline='false')
        comm = data.get('community_data', {}) or {}
        dev = data.get('developer_data', {}) or {}
        metrics = {
            'twitter_followers': comm.get('twitter_followers'),
            'reddit_subscribers': comm.get('reddit_subscribers'),
            'reddit_active_48h': comm.get('reddit_accounts_active_48h'),
            'reddit_avg_posts_48h': comm.get('reddit_average_posts_48h'),
            'reddit_avg_comments_48h': comm.get('reddit_average_comments_48h'),
            'total_issues': dev.get('total_issues'),
            'closed_issues': dev.get('closed_issues'),
            'pull_requests_merged': dev.get('pull_requests_merged'),
            'pr_contributors': dev.get('pull_request_contributors'),
            'forks': dev.get('forks'),
            'stars': dev.get('stars'),
            'subscribers': dev.get('subscribers'),
            'sentiment_up_pct': comm.get('sentiment_votes_up_percentage'),
            'sentiment_down_pct': comm.get('sentiment_votes_down_percentage')
        }
        return metrics
    except Exception as e:
        st.error(f"Error fetching coin metrics: {e}")
        return {}

@st.cache_data(ttl=3600)
def get_fear_and_greed_index():
    """
    Fetch the Crypto Fear & Greed Index from alternative.me.
    """
    url = "https://api.alternative.me/fng/"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('data'):
            item = data['data'][0]
            return {
                'value': item['value'],
                'classification': item['value_classification'],
                'timestamp': item['timestamp']
            }
        return None
    except Exception as e:
        st.error(f"Error fetching Fear & Greed Index: {e}")
        return None

def calculate_rsi(df, period=14):
    """Calculate RSI for a given DataFrame with a 'close' column."""
    if 'close' not in df:
        return pd.Series(dtype=float)

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Use Wilder's Smoothing (EMA with alpha=1/period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    """Calculate MACD, Signal, and Histogram."""
    if 'close' not in df:
        return pd.DataFrame()

    exp1 = df['close'].ewm(span=short_window, adjust=False).mean()
    exp2 = df['close'].ewm(span=long_window, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    hist = macd - signal
    return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': hist})

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands."""
    if 'close' not in df:
        return pd.DataFrame()

    sma = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return pd.DataFrame({'B_Upper': upper, 'B_Lower': lower, 'SMA': sma})

@st.cache_data(ttl=3600)
def get_trending_coins():
    """
    Fetch top 7 trending coins on CoinGecko.
    """
    try:
        trending = cg.get_search_trending()
        return trending.get('coins', [])
    except Exception as e:
        st.error(f"Error fetching trending coins: {e}")
        return []

@st.cache_data(ttl=60)
def get_current_price(coin_ids, vs_currencies='usd,eur,btc,eth'):
    """
    Fetch current prices for a list of coin IDs.
    """
    if isinstance(coin_ids, list):
        coin_ids = ','.join(coin_ids)
    try:
        prices = cg.get_price(ids=coin_ids, vs_currencies=vs_currencies)
        return prices
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
        return {}

def calculate_backtest(df, strategy_type='SMA Crossover'):
    """
    Perform a simple backtest on the provided DataFrame.
    Returns the dataframe with returns and a metrics dictionary.
    """
    if df.empty or 'close' not in df.columns:
        return pd.DataFrame(), {}

    df = df.copy()
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0

    # 1. Generate Signals
    if strategy_type == 'SMA Crossover':
        # Simple Moving Average Crossover (Golden Cross)
        short_window = 20
        long_window = 50
        df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
        df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()

        # Create signal: 1 when short > long, else 0
        signals['signal'] = np.where(df['short_mavg'] > df['long_mavg'], 1.0, 0.0)

    elif strategy_type == 'RSI Mean Reversion':
        # Buy if RSI < 30, Sell if RSI > 70
        rsi = calculate_rsi(df)

        # Vectorized approach using masking and forward fill
        signal_series = pd.Series(np.nan, index=rsi.index)
        signal_series[rsi < 30] = 1.0
        signal_series[rsi > 70] = 0.0

        # Forward fill to propagate the last active signal
        signal_series = signal_series.ffill().fillna(0.0)
        signals['signal'] = signal_series

    # 2. Calculate Returns
    # Market Returns
    df['returns'] = df['close'].pct_change()

    # Add signal to output df for visualization
    df['signal'] = signals['signal']

    # Strategy Returns = Position(t-1) * Return(t)
    df['strategy_returns'] = signals['signal'].shift(1) * df['returns']

    # 3. Metrics
    # Fill NaN (first row) with 0
    df['strategy_returns'] = df['strategy_returns'].fillna(0)
    df['returns'] = df['returns'].fillna(0)

    df['cumulative_market_returns'] = (1 + df['returns']).cumprod()
    df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()

    total_return = df['cumulative_strategy_returns'].iloc[-1] - 1
    market_return = df['cumulative_market_returns'].iloc[-1] - 1

    metrics = {
        'Total Return': total_return,
        'Market Return': market_return
    }

    return df, metrics

@st.cache_data(ttl=3600)
def get_batch_historical_prices(coin_ids, days=90):
    """
    Fetch historical prices for multiple coins and return a combined DataFrame.
    Uses concurrent requests to speed up fetching.
    """
    dfs = []

    def fetch_price(cid):
        try:
            # Re-use existing function but we need to bypass cache if needed or just use it.
            # It's cached, so it's fast.
            df = get_historical_prices(cid, days=days)
            if not df.empty:
                df = df.rename(columns={'close': cid})
                return df
        except Exception:
            pass
        return None

    # Use ThreadPoolExecutor for concurrent requests
    # Limit max_workers to avoid hitting rate limits too hard
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks. We maintain the order of futures to match coin_ids
        futures = [executor.submit(fetch_price, cid) for cid in coin_ids]

        # Collect results in order
        for future in futures:
            df = future.result()
            if df is not None:
                dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    # Concatenate all at once along columns (axis=1)
    combined_df = pd.concat(dfs, axis=1, join='outer')
    return combined_df
