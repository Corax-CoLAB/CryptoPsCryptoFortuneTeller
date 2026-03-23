with open("streamlit_app/modules/cryptop_crypto_circus_helper.py", "r") as f:
    content = f.read()

downcast_func = """
def downcast_dtypes(df):
    \"\"\"
    Technical Improvement 3: Memory Optimization
    Downcasts numerical columns to float32 to save memory, especially critical
    for large batch historical data fetching.
    \"\"\"
    fcols = df.select_dtypes('float').columns
    icols = df.select_dtypes('integer').columns
    df[fcols] = df[fcols].apply(pd.to_numeric, downcast='float')
    df[icols] = df[icols].apply(pd.to_numeric, downcast='integer')
    return df
"""

if "def downcast_dtypes" not in content:
    content = content.replace("def validate_coin_id(coin_id):", downcast_func + "\ndef validate_coin_id(coin_id):")

# Update get_batch_historical_prices
old_concat = """    combined_df = pd.concat(dfs, axis=1, join='outer')
    return combined_df"""

new_concat = """    # Technical Improvement 3: Optimize memory footprint before concatenation
    dfs = [downcast_dtypes(d) for d in dfs]
    combined_df = pd.concat(dfs, axis=1, join='outer')
    return downcast_dtypes(combined_df)"""

content = content.replace(old_concat, new_concat)

with open("streamlit_app/modules/cryptop_crypto_circus_helper.py", "w") as f:
    f.write(content)

print("Memory downcasting added")
