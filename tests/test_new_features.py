import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from streamlit_app.modules.cryptop_crypto_fortune_teller_helper import (
    calculate_backtest,
    get_trending_coins,
    get_current_price,
    get_batch_historical_prices
)

# --- Test calculate_backtest ---
def test_calculate_backtest_sma():
    # Create synthetic data
    # Short SMA (20), Long SMA (50)
    # We need at least 51 points.
    dates = pd.date_range(start='2023-01-01', periods=100)
    # Create a trend where price rises, ensuring Short > Long eventually
    close = np.linspace(100, 200, 100)
    df = pd.DataFrame({'close': close}, index=dates)

    res_df, metrics = calculate_backtest(df, strategy_type='SMA Crossover')

    assert not res_df.empty
    assert 'signal' in res_df.columns
    assert 'strategy_returns' in res_df.columns
    assert 'Total Return' in metrics
    # Since price is rising monotonically, SMA 20 should be > SMA 50 after some time
    # Check if we have positive signals
    assert res_df['signal'].sum() > 0

def test_calculate_backtest_empty():
    df = pd.DataFrame()
    res_df, metrics = calculate_backtest(df)
    assert res_df.empty
    assert metrics == {}

# --- Test get_trending_coins ---
@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.cg')
def test_get_trending_coins(mock_cg):
    # Clear cache if possible to ensure mock is called
    if hasattr(get_trending_coins, 'clear'):
        get_trending_coins.clear()

    # Mock response
    mock_cg.get_search_trending.return_value = {
        'coins': [{'item': {'id': 'bitcoin', 'name': 'Bitcoin'}}]
    }

    coins = get_trending_coins()
    assert len(coins) == 1
    assert coins[0]['item']['name'] == 'Bitcoin'

@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.cg')
def test_get_trending_coins_error(mock_cg):
    # Clear cache
    if hasattr(get_trending_coins, 'clear'):
        get_trending_coins.clear()

    mock_cg.get_search_trending.side_effect = Exception("API Error")
    coins = get_trending_coins()
    assert coins == []

# --- Test get_current_price ---
@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.cg')
def test_get_current_price(mock_cg):
    if hasattr(get_current_price, 'clear'):
        get_current_price.clear()

    mock_cg.get_price.return_value = {'bitcoin': {'usd': 50000}}

    price = get_current_price('bitcoin')
    assert price['bitcoin']['usd'] == 50000

# --- Test get_batch_historical_prices ---
@patch('streamlit_app.modules.cryptop_crypto_fortune_teller_helper.get_historical_prices')
def test_get_batch_historical_prices(mock_get_hist):
    if hasattr(get_batch_historical_prices, 'clear'):
        get_batch_historical_prices.clear()

    # Mock returning a DF for bitcoin and nothing for eth
    dates = pd.date_range(start='2023-01-01', periods=2)
    df_btc = pd.DataFrame({'close': [100, 101]}, index=dates)

    def side_effect(coin_id, days):
        if coin_id == 'bitcoin':
            return df_btc
        return pd.DataFrame()

    mock_get_hist.side_effect = side_effect

    combined = get_batch_historical_prices(['bitcoin', 'ethereum'], days=30)

    assert 'bitcoin' in combined.columns
    assert 'ethereum' not in combined.columns
    assert len(combined) == 2
