import pandas as pd
import numpy as np
import time

n = 10000
df = pd.DataFrame({
    'Alpha Potential': np.random.randn(n) * 100,
    'tvlUsd': np.random.rand(n) * 1e9,
    'apy': np.where(np.random.rand(n) > 0.1, np.random.rand(n) * 100, np.nan)
})

# Alpha Potential
start = time.time()
df['Arbitrage_apply'] = df['Alpha Potential'].apply(lambda x: '🔥 Yes' if x > 0 else 'No')
end = time.time()
print(f"Alpha apply: {end - start:.4f}")

start = time.time()
df['Arbitrage_vec'] = np.where(df['Alpha Potential'] > 0, '🔥 Yes', 'No')
end = time.time()
print(f"Alpha vec: {end - start:.4f}")

# String formatting
start = time.time()
df['tvl_apply'] = df['tvlUsd'].apply(lambda x: f"${x:,.0f}")
end = time.time()
print(f"tvl apply: {end - start:.4f}")

start = time.time()
df['tvl_map'] = df['tvlUsd'].map(lambda x: f"${x:,.0f}")
end = time.time()
print(f"tvl map: {end - start:.4f}")

start = time.time()
df['tvl_comp'] = [f"${x:,.0f}" for x in df['tvlUsd']]
end = time.time()
print(f"tvl comp: {end - start:.4f}")


start = time.time()
df['apy_apply'] = df['apy'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
end = time.time()
print(f"apy apply: {end - start:.4f}")

start = time.time()
df['apy_comp'] = [f"{x:.2f}%" if pd.notnull(x) else "N/A" for x in df['apy']]
end = time.time()
print(f"apy comp: {end - start:.4f}")
