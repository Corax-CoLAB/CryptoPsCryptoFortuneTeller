import time
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def build_model(n_steps):
    model = Sequential([
        Input(shape=(n_steps, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def benchmark():
    n_steps = 60
    periods = 100 # Number of prediction steps

    # Create dummy data and model
    print("Building model...")
    model = build_model(n_steps)

    # Create a random input sequence
    initial_input = np.random.rand(1, n_steps, 1).astype(np.float32)

    # Warmup
    print("Warming up...")
    model.predict_on_batch(initial_input)

    print(f"\nRunning benchmarks for {periods} prediction steps...")

    # --- 2. predict_on_batch() with list append (Current Code) ---
    forecast_input = initial_input.copy()
    start_time = time.time()
    preds_list = []
    for _ in range(periods):
        pred = model.predict_on_batch(forecast_input)[0][0]
        preds_list.append(pred)
        # In-place update
        forecast_input[:, :-1, :] = forecast_input[:, 1:, :]
        forecast_input[0, -1, 0] = pred
    # Final conversion
    _ = np.array(preds_list)
    end_time = time.time()
    time_batch = end_time - start_time
    print(f"2. predict_on_batch + list append: {time_batch:.4f}s")

    # --- 5. predict_on_batch() with pre-allocated array (Potential Optimization) ---
    forecast_input = initial_input.copy()
    start_time = time.time()
    preds_array = np.zeros(periods, dtype=np.float32)
    for i in range(periods):
        pred = model.predict_on_batch(forecast_input)[0][0]
        preds_array[i] = pred
        # In-place update
        forecast_input[:, :-1, :] = forecast_input[:, 1:, :]
        forecast_input[0, -1, 0] = pred
    end_time = time.time()
    time_prealloc = end_time - start_time
    print(f"5. predict_on_batch + pre-alloc: {time_prealloc:.4f}s")

    # Comparisons
    print("\nResults:")
    if time_prealloc > 0:
        print(f"Speedup Pre-alloc vs List: {time_batch / time_prealloc:.2f}x")

if __name__ == "__main__":
    benchmark()
