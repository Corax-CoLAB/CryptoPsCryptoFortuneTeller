
import time
import functools

# Mock st.cache_data since streamlit is not available in this environment
def mock_cache_data(ttl=None):
    def decorator(func):
        cache = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        return wrapper
    return decorator

# Simulation of a technical indicator calculation
def calculate_indicator_simulated(data_size):
    # Simulate work
    total = 0
    for i in range(data_size):
        total += i * i
    return total

@mock_cache_data()
def calculate_indicator_cached_simulated(data_size):
    return calculate_indicator_simulated(data_size)

def run_benchmark():
    data_size = 10**6
    iterations = 10

    print(f"Benchmarking simulation with data_size={data_size} over {iterations} iterations...")

    # Non-cached baseline
    start_time = time.time()
    for _ in range(iterations):
        calculate_indicator_simulated(data_size)
    end_time = time.time()
    baseline_time = end_time - start_time
    print(f"Baseline (Non-cached) total time: {baseline_time:.4f}s")
    print(f"Baseline average time per call: {baseline_time/iterations:.4f}s")

    # Cached
    # First call to warm up cache
    calculate_indicator_cached_simulated(data_size)

    start_time = time.time()
    for _ in range(iterations):
        calculate_indicator_cached_simulated(data_size)
    end_time = time.time()
    cached_time = end_time - start_time
    print(f"Optimized (Cached) total time: {cached_time:.4f}s")
    print(f"Optimized average time per call: {cached_time/iterations:.4f}s")

    if cached_time > 0:
        speedup = baseline_time / cached_time
        print(f"Theoretical Speedup: {speedup:.2f}x")
    else:
        print("Optimized time is near zero, speedup is massive.")

if __name__ == "__main__":
    run_benchmark()
