# cryptop_crypto_fortune_teller_helper.py
import pandas as pd
import numpy as np
from pycoingecko import CoinGeckoAPI
import streamlit as st

# Initialize CoinGecko client (public demo API)
cg = CoinGeckoAPI()

@st.cache_data
def get_coin_list():
    """
    Fetch list of all supported coins from CoinGecko.
    Returns a DataFrame with columns [id, symbol, name].
    """
    coins = cg.get_coins_list()  # get list of coins with id, symbol, name:contentReference[oaicite:0]{index=0}
    df_coins = pd.DataFrame(coins)
    return df_coins

@st.cache_data
def get_historical_prices(coin_id, vs_currency='usd', days=365):
    """
    Fetch historical market data (prices) for a coin.
    Returns DataFrame with date index and 'close' prices.
    """
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
    # 'prices' is list of [timestamp, price]
    prices = data.get('prices', [])
    df = pd.DataFrame(prices, columns=['timestamp', 'close'])
    # convert ms timestamp to datetime
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['close']]
    return df

@st.cache_data
def get_historical_ohlc(coin_id, vs_currency='usd', days=30):
    """
    Fetch historical OHLC data for a coin.
    Returns DataFrame with date index and columns ['open','high','low','close'].
    Uses CoinGecko OHLC endpoint (30-day candlesticks):contentReference[oaicite:1]{index=1}.
    """
    ohlc_data = cg.get_coin_ohlc_by_id(id=coin_id, vs_currency=vs_currency, days=days)
    df = pd.DataFrame(ohlc_data, columns=['timestamp','open','high','low','close'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['open','high','low','close']]
    return df

def compute_volatility(df, window=14):
    """
    Compute volatility indicators: rolling standard deviation and Average True Range (ATR).
    Returns DataFrame with columns ['rolling_std', 'ATR'].
    ATR is calculated using high, low, and previous close (Welles Wilder method):contentReference[oaicite:2]{index=2}.
    """
    if 'close' not in df:
        raise ValueError("DataFrame must contain 'close' column for volatility calculation.")
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

@st.cache_data
def get_coin_metrics(coin_id):
    """
    Fetch additional metrics for a coin: community and developer data.
    Uses CoinGecko API to get community (social) and developer stats.
    """
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
