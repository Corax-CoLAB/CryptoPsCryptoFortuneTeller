with open("tests/test_models.py", "r") as f:
    content = f.read()

monte_carlo_test = """
def test_monte_carlo():
    from modules.cryptop_crypto_fortune_teller_models import forecast_monte_carlo
    # Create synthetic daily data
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    prices = np.linspace(100, 150, 100) + np.random.normal(0, 5, 100)
    df = pd.DataFrame({'close': prices}, index=dates)

    # Test typical forecast
    res_df = forecast_monte_carlo(df, periods=30)
    assert not res_df.empty, "Monte Carlo forecast should return a dataframe"
    assert len(res_df) == 30, "Forecast length should match periods"
    assert 'yhat' in res_df.columns, "Missing 'yhat' column"
    assert 'yhat_lower' in res_df.columns, "Missing 'yhat_lower' column"
    assert 'yhat_upper' in res_df.columns, "Missing 'yhat_upper' column"

    # Check that yhat_lower <= yhat <= yhat_upper
    assert (res_df['yhat_lower'] <= res_df['yhat']).all(), "yhat_lower must be <= yhat"
    assert (res_df['yhat'] <= res_df['yhat_upper']).all(), "yhat must be <= yhat_upper"

"""

content += monte_carlo_test

with open("tests/test_models.py", "w") as f:
    f.write(content)
