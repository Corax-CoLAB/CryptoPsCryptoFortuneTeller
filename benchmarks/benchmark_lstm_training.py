
import sys
import os
import time
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
import tensorflow as tf

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def benchmark():
    """
    Benchmark LSTM training performance with different batch sizes.
    """
    print("Preparing benchmark data...")
    dates = pd.date_range(start='2020-01-01', periods=500)
    np.random.seed(42)
    returns = np.random.normal(0, 0.02, 500)
    price = 100 * (1 + returns).cumprod()

    n_steps = 60
    series = price

    scaler = MinMaxScaler()
    series_scaled = scaler.fit_transform(series.reshape(-1,1))

    X, y = [], []
    for i in range(n_steps, len(series_scaled)):
        X.append(series_scaled[i-n_steps:i, 0])
        y.append(series_scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Warmup
    print("Warming up...")
    model = Sequential([Input(shape=(n_steps, 1)), LSTM(50), Dense(1)])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=1, batch_size=32, verbose=0)

    # Benchmark
    batch_sizes = [16, 32, 64]
    results = {}

    print("\nRunning benchmarks...")
    for bs in batch_sizes:
        tf.keras.backend.clear_session()
        model = Sequential([Input(shape=(n_steps, 1)), LSTM(50), Dense(1)])
        model.compile(optimizer='adam', loss='mse')

        start_fit = time.time()
        model.fit(X, y, epochs=5, batch_size=bs, verbose=0)
        duration = time.time() - start_fit

        results[bs] = duration
        print(f"Batch Size {bs}: {duration:.4f}s")

    print("\nSummary:")
    base = results[16]
    for bs in batch_sizes:
        speedup = (base - results[bs]) / base * 100
        print(f"Batch Size {bs}: {results[bs]:.4f}s ({speedup:.1f}% improvement)")

if __name__ == "__main__":
    benchmark()
