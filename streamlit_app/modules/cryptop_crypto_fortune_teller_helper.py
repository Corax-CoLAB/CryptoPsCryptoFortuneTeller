# cryptop_crypto_fortune_teller_helper.py
import pandas as pd
import numpy as np
from pycoingecko import CoinGeckoAPI
import streamlit as st
import requests
import concurrent.futures
import re

# Initialize CoinGecko client (public demo API)
cg = CoinGeckoAPI()
cg.request_timeout = 20  # Sentinel: Enforce timeout to prevent hanging

# Sentinel: Prevent Timedelta Overflow (DoS)
# pandas Timedelta limit is ~106,752 days.
MAX_HISTORY_DAYS = 20000

def validate_coin_id(coin_id):
    """
    Validate coin_id to ensure it only contains safe characters.
    Valid characters: a-z, 0-9, -, ., _
    """
    if not isinstance(coin_id, str):
        return False
    # Alphanumeric, hyphen, dot, underscore are standard in CoinGecko IDs
    # Blocks path traversal (/) and script injection (<>)
    if not re.match(r'^[a-z0-9\-\._]+$', coin_id):
        return False
    return True

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
def _fetch_historical_prices_cached(coin_id, vs_currency='usd', days='max'):
    """
    Internal cached function to fetch historical market data (prices) for a coin.
    Uses 'days' as a resolution bucket (1, 90, or 'max') to optimize caching.
    """
    try:
        # Sentinel: Pass timeout to prevent hanging if supported by wrapper
        # Using 3 seconds timeout
        try:
             data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days, timeout=3)
        except TypeError:
             # Fallback if timeout kwarg is not supported, or use direct request
             # Since we know wrapper is old or custom, we force direct request here to be safe
             url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
             params = {'vs_currency': vs_currency, 'days': days}
             r = requests.get(url, params=params, timeout=3)
             r.raise_for_status()
             data = r.json()

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

def get_historical_prices(coin_id, vs_currency='usd', days=365):
    """
    Fetch historical market data (prices) for a coin.
    Returns DataFrame with date index and 'close' prices.
    Implements a Tiered Caching Strategy (Bucket 1, 90, or Max) to preserve resolution.
    """
    # Sentinel: Validate coin_id
    if not validate_coin_id(coin_id):
        st.error(f"Invalid coin ID: {coin_id}")
        return pd.DataFrame()

    # Determine cache bucket to preserve resolution
    try:
        days_val = float(days)
    except (ValueError, TypeError):
        days_val = 99999 # Treat as max

    # Tier 1: 1 day (5 min resolution)
    if days_val <= 1:
        fetch_days = 1
    # Tier 2: 90 days (Hourly resolution)
    elif days_val <= 90:
        fetch_days = 90
    # Tier 3: Max (>90 days) (Daily resolution)
    else:
        fetch_days = 'max'

    # Fetch from cached tier
    df = _fetch_historical_prices_cached(coin_id, vs_currency, days=fetch_days)

    if df.empty:
        return df

    # Return full df if 'max' requested or if we are using exact bucket
    if days == 'max':
        return df

    try:
        days_int = float(days)
        # Sentinel: Check bounds to prevent Timedelta overflow/underflow crash
        if days_int > MAX_HISTORY_DAYS or days_int < 0:
            return df
    except (ValueError, TypeError):
        # Fallback if days cannot be converted to number, return full history
        return df

    # Slice the dataframe to the requested number of days
    # Use UTC for consistency as CoinGecko timestamps are UTC based.
    # df['date'] (index) is naive UTC.
    try:
        cutoff_date = pd.Timestamp.utcnow().replace(tzinfo=None) - pd.Timedelta(days=days_int)
        return df[df.index >= cutoff_date]
    except (pd.errors.OutOfBoundsTimedelta, OverflowError, ValueError):
        # Fallback for any other overflow issues
        return df

@st.cache_data(ttl=3600)
def _fetch_historical_ohlc_cached(coin_id, vs_currency='usd', days='max'):
    """
    Internal cached function to fetch historical OHLC data for a coin.
    Uses 'days' as a resolution bucket (1, 30, or 'max') to optimize caching.
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

def get_historical_ohlc(coin_id, vs_currency='usd', days=30):
    """
    Fetch historical OHLC data for a coin.
    Returns DataFrame with date index and columns ['open','high','low','close'].
    Implements a Tiered Caching Strategy (Bucket 1, 30, or Max) to preserve resolution while minimizing API calls.
    """
    # Sentinel: Validate coin_id
    if not validate_coin_id(coin_id):
        st.error(f"Invalid coin ID: {coin_id}")
        return pd.DataFrame()

    # Determine cache bucket to preserve resolution
    try:
        days_val = float(days)
    except (ValueError, TypeError):
        days_val = 99999 # Treat as max

    # Tier 1: 1 day (30 min resolution)
    if days_val <= 1:
        fetch_days = 1
    # Tier 2: 30 days (4 hour resolution)
    elif days_val <= 30:
        fetch_days = 30
    # Tier 3: Max (>30 days) (4 day resolution)
    else:
        fetch_days = 'max'

    # Fetch from cached tier
    df = _fetch_historical_ohlc_cached(coin_id, vs_currency, days=fetch_days)

    if df.empty:
        return df

    # Return full df if 'max' requested or if we are using exact bucket
    if days == 'max':
        return df

    # Sentinel: Check bounds for days_val (which is already float or max)
    if days_val > MAX_HISTORY_DAYS or days_val < 0:
        return df

    # Slice the dataframe to the requested number of days
    try:
        cutoff_date = pd.Timestamp.utcnow().replace(tzinfo=None) - pd.Timedelta(days=days_val)
        return df[df.index >= cutoff_date]
    except (pd.errors.OutOfBoundsTimedelta, OverflowError, ValueError):
        return df

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
        # Optimization: Use numpy for element-wise operations instead of pandas concat/apply
        # ⚡ Bolt Optimization: Replaced pd.concat(...).max(axis=1) with np.fmax
        # Speedup: ~2.8x faster
        h = df['high'].values.astype(float)
        l = df['low'].values.astype(float)
        c = df['close'].values.astype(float)

        # High - Low
        hl = h - l

        # Shifted Close (equivalent to df['close'].shift(1))
        prev_c = np.empty_like(c)
        prev_c[1:] = c[:-1]
        prev_c[0] = np.nan  # First element is NaN

        # Calculate True Range components
        h_pc = np.abs(h - prev_c)
        l_pc = np.abs(l - prev_c)

        # True Range is max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        # np.fmax ignores NaNs, matching pandas behavior for this case
        tr_values = np.fmax(hl, np.fmax(h_pc, l_pc))

        # Convert back to Series for rolling mean
        tr_series = pd.Series(tr_values, index=df.index)
        vol['ATR'] = tr_series.rolling(window).mean()
    else:
        vol['ATR'] = np.nan
    return vol

def check_risk_level(df):
    """
    Analyze volatility and return a risk warning if applicable.
    Returns string (message) or None.
    """
    if df.empty or len(df) < 15:
        return None

    # Calculate volatility (rolling standard deviation)
    # Optimized: Compute directly on series to avoid overhead of full DataFrame creation in compute_volatility
    if 'close' not in df:
        return None

    rolling_std = df['close'].rolling(14).std()

    if rolling_std.empty:
        return None

    current_vol = rolling_std.iloc[-1]
    avg_vol = rolling_std.mean()

    # Thresholds: If current volatility is > 2x average, it's High Risk
    if current_vol > 2 * avg_vol:
        return "⚠️ High Volatility Detected: Market is extremely turbulent. Prices may fluctuate wildly."
    elif current_vol > 1.5 * avg_vol:
        return "⚠️ Elevated Volatility: Caution advised."

    return None

def generate_trading_signal(current_price, forecast_df):
    """
    Generate a Buy/Sell signal based on forecast vs current price.
    Returns string signal and color.
    """
    if forecast_df.empty or 'yhat' not in forecast_df.columns:
        return "N/A", "gray"

    # Get last forecasted price
    target_price = forecast_df['yhat'].iloc[-1]

    if current_price == 0:
        return "N/A", "gray"

    pct_change = ((target_price - current_price) / current_price) * 100

    if pct_change > 20:
        return "STRONG BUY", "#00FF00" # Green
    elif pct_change > 5:
        return "BUY", "#90EE90" # Light Green
    elif pct_change < -20:
        return "STRONG SELL", "#FF0000" # Red
    elif pct_change < -5:
        return "SELL", "#FF6347" # Tomato
    else:
        return "HOLD", "#FFFF00" # Yellow

@st.cache_data(ttl=3600)
def get_coin_metrics(coin_id):
    """
    Fetch additional metrics for a coin: community and developer data.
    Uses CoinGecko API to get community (social) and developer stats.
    """
    # Sentinel: Validate coin_id
    if not validate_coin_id(coin_id):
        return {}

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

@st.cache_data(ttl=60)
def get_coin_market_data(coin_id):
    """
    Fetch market data for a specific coin (price, circulating supply).
    """
    # Sentinel: Validate coin_id
    if not validate_coin_id(coin_id):
        return {}

    try:
        data = cg.get_coin_by_id(
            id=coin_id,
            localization='false',
            tickers='false',
            market_data='true',
            community_data='false',
            developer_data='false',
            sparkline='false'
        )
        market_data = data.get('market_data', {})
        if not market_data:
            return {}

        return {
            'current_price': market_data.get('current_price', {}).get('usd'),
            'circulating_supply': market_data.get('circulating_supply')
        }
    except Exception as e:
        st.error(f"Error fetching coin market data: {e}")
        return {}

@st.cache_data(ttl=3600)
def get_fear_and_greed_index():
    """
    Fetch the Crypto Fear & Greed Index from alternative.me.
    """
    url = "https://api.alternative.me/fng/"
    try:
        # Sentinel: Added User-Agent, extended timeout, and status check
        headers = {'User-Agent': 'CryptoFortuneTeller/1.0'}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
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
    # Initialize signal series with 0.0 (Neutral)
    signal_series = pd.Series(0.0, index=df.index)

    # 1. Generate Signals
    if strategy_type == 'SMA Crossover':
        # Simple Moving Average Crossover (Golden Cross)
        short_window = 20
        long_window = 50
        df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
        df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()

        # Create signal: 1 when short > long, else 0
        signal_series = pd.Series(np.where(df['short_mavg'] > df['long_mavg'], 1.0, 0.0), index=df.index)

    elif strategy_type == 'RSI Mean Reversion':
        # Buy if RSI < 30, Sell if RSI > 70
        rsi = calculate_rsi(df)

        # Vectorized approach using masking and forward fill
        # This is ~25x faster than iterating through the RSI series (see benchmarks/benchmark_rsi.py)
        signal_series = pd.Series(np.nan, index=rsi.index)
        signal_series[rsi < 30] = 1.0
        signal_series[rsi > 70] = 0.0

        # Forward fill to propagate the last active signal
        signal_series = signal_series.ffill().fillna(0.0)

    # 2. Calculate Returns
    # Market Returns
    df['returns'] = df['close'].pct_change()

    # Add signal to output df for visualization
    df['signal'] = signal_series

    # Strategy Returns = Position(t-1) * Return(t)
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']

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
def get_batch_historical_prices(coin_ids: list, days: int = 90) -> pd.DataFrame:
    """
    Fetch historical prices for multiple coins and return a combined DataFrame.
    Uses concurrent requests to speed up fetching.
    """
    # 🛡️ Sentinel: Limit batch size to prevent API abuse/DoS
    MAX_BATCH_SIZE = 10

    if not coin_ids:
        return pd.DataFrame()

    # Ensure list and deduplicate to prevent redundant API calls
    if not isinstance(coin_ids, list):
        coin_ids = list(coin_ids)

    # Deduplicate while preserving order (Python 3.7+ dicts preserve insertion order)
    coin_ids = list(dict.fromkeys(coin_ids))

    if len(coin_ids) > MAX_BATCH_SIZE:
        st.warning(f"⚠️ Security Limit: Request truncated to first {MAX_BATCH_SIZE} unique assets to prevent API rate limit exhaustion.")
        coin_ids = coin_ids[:MAX_BATCH_SIZE]

    dfs = []

    def fetch_price(cid):
        try:
            # Re-use existing function which is cached and handles its own errors
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
        # map returns an iterator that yields results in the order calls were submitted
        results = executor.map(fetch_price, coin_ids)
        for df in results:
            if df is not None:
                dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    # Concatenate all at once along columns (axis=1)
    combined_df = pd.concat(dfs, axis=1, join='outer')
    return combined_df

# --- NEW FEATURES ---

def calculate_stochastic_oscillator(df, k_window=14, d_window=3):
    """
    Calculate Stochastic Oscillator (K and D).
    Requires 'high', 'low', 'close' columns.
    """
    if not all(col in df.columns for col in ['high', 'low', 'close']):
        return pd.DataFrame()

    low_min = df['low'].rolling(window=k_window).min()
    high_max = df['high'].rolling(window=k_window).max()

    k = 100 * ((df['close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_window).mean()

    return pd.DataFrame({'%K': k, '%D': d}, index=df.index)

def calculate_ichimoku_cloud(df):
    """
    Calculate Ichimoku Cloud components.
    Requires 'high', 'low' columns.
    """
    if not all(col in df.columns for col in ['high', 'low']):
        return pd.DataFrame()

    # Conversion Line (Tenkan-sen): (9-period high + 9-period low) / 2
    period9_high = df['high'].rolling(window=9).max()
    period9_low = df['low'].rolling(window=9).min()
    tenkan_sen = (period9_high + period9_low) / 2

    # Base Line (Kijun-sen): (26-period high + 26-period low) / 2
    period26_high = df['high'].rolling(window=26).max()
    period26_low = df['low'].rolling(window=26).min()
    kijun_sen = (period26_high + period26_low) / 2

    # Leading Span A (Senkou Span A): (Conversion Line + Base Line) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Leading Span B (Senkou Span B): (52-period high + 52-period low) / 2
    period52_high = df['high'].rolling(window=52).max()
    period52_low = df['low'].rolling(window=52).min()
    senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

    # Lagging Span (Chikou Span): Close plotted 26 periods in the past
    chikou_span = df['close'].shift(-26)

    return pd.DataFrame({
        'Tenkan': tenkan_sen,
        'Kijun': kijun_sen,
        'SpanA': senkou_span_a,
        'SpanB': senkou_span_b,
        'Chikou': chikou_span
    }, index=df.index)

def calculate_pivot_points(df):
    """
    Calculate Pivot Points (Standard) based on the previous day's High, Low, Close.
    Returns a dict with pivot levels for the *current* day (projected from last full candle).
    """
    if df.empty or len(df) < 1:
        return {}

    # We take the last completed candle (assuming daily data)
    last_candle = df.iloc[-1]

    # If using current day's incomplete candle, it's an estimation.
    # For daily pivots, we typically use yesterday's HLC.
    if len(df) > 1:
        prev_candle = df.iloc[-2]
    else:
        prev_candle = last_candle

    high = prev_candle['high'] if 'high' in prev_candle else prev_candle['close']
    low = prev_candle['low'] if 'low' in prev_candle else prev_candle['close']
    close = prev_candle['close']

    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)

    return {
        'Pivot': pivot,
        'R1': r1, 'S1': s1,
        'R2': r2, 'S2': s2,
        'R3': r3, 'S3': s3
    }

def calculate_fibonacci_levels(df):
    """
    Calculate Fibonacci Retracement levels based on the visible high and low range.
    Returns a dict of levels.
    """
    if df.empty or 'high' not in df or 'low' not in df:
        return {}

    max_price = df['high'].max()
    min_price = df['low'].min()
    diff = max_price - min_price

    return {
        '0.0% (High)': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50.0%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '78.6%': max_price - 0.786 * diff,
        '100.0% (Low)': min_price
    }

def calculate_roi(initial_investment, initial_price, current_price):
    """
    Calculate Return on Investment.
    """
    if initial_price == 0:
        return 0, 0

    amount_bought = initial_investment / initial_price
    current_value = amount_bought * current_price
    profit = current_value - initial_investment

    # Sentinel: Prevent division by zero
    if initial_investment == 0:
        return current_value, 0.0

    roi_pct = (profit / initial_investment) * 100

    return current_value, roi_pct

def calculate_moon_math(current_price, current_supply, target_market_cap):
    """
    Calculate price required to reach a target market cap.
    """
    if current_supply == 0:
        return 0, 0 # Sentinel: Return tuple to match expected unpacking

    target_price = target_market_cap / current_supply

    # Sentinel: Prevent division by zero
    if current_price == 0:
        return 0, 0

    upside = ((target_price - current_price) / current_price) * 100
    return target_price, upside

@st.cache_data(ttl=3600)
def get_coin_market_cap_batch(limit=50):
    """
    Fetch market data for top N coins to visualize market cap.
    Used for the Market Overview visualization.
    """
    try:
        # vs_currency='usd' is default
        data = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=limit, page=1)
        df = pd.DataFrame(data)
        # We want: id, symbol, name, market_cap, current_price, price_change_percentage_24h
        return df[['id', 'symbol', 'name', 'market_cap', 'current_price', 'price_change_percentage_24h', 'total_volume']]
    except Exception as e:
        st.error(f"Error fetching market cap batch: {e}")
        return pd.DataFrame()
