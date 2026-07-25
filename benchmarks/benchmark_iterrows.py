import pandas as pd
import numpy as np
import time

# Create a sample DataFrame
n = 10000
df = pd.DataFrame({
    'open': np.random.rand(n),
    'close': np.random.rand(n)
})

# Iterrows
start = time.time()
colors_iter = ['green' if row['open'] - row['close'] >= 0 else 'red' for index, row in df.iterrows()]
end = time.time()
print(f"Iterrows: {end - start:.4f} seconds")

# np.where
start = time.time()
colors_vec = np.where(df['open'] >= df['close'], 'green', 'red')
end = time.time()
print(f"Vectorized: {end - start:.4f} seconds")

assert list(colors_iter) == list(colors_vec)
