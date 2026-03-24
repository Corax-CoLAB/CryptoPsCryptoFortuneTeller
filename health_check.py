#!/usr/bin/env python3
import sys
import subprocess
import requests
import importlib.util
import time
import os

def print_header(msg):
    print(f"\n{'='*60}")
    print(f" {msg}")
    print(f"{'='*60}")

def check_python_version():
    print_header("Python Version Check")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 10):
        print("❌ Warning: Python version is older than 3.10. Recommended: 3.11+")
        return False
    print("✅ Python version OK")
    return True

def check_dependencies():
    print_header("Dependency Check")
    critical_deps = [
        'streamlit', 'pandas', 'numpy', 'plotly', 'pycoingecko',
        'prophet', 'tensorflow', 'sklearn', 'requests', 'statsmodels', 'ccxt'
    ]
    all_ok = True
    for dep in critical_deps:
        try:
            # Handle sklearn import name mismatch
            module_name = 'sklearn' if dep == 'scikit-learn' else dep
            importlib.import_module(module_name)
            print(f"✅ {dep} found")
        except ImportError:
            print(f"❌ {dep} NOT found")
            all_ok = False

    # Check specific version constraint for numpy
    try:
        import numpy
        print(f"ℹ️  numpy version: {numpy.__version__}")
        if numpy.__version__.startswith('2.'):
             print("⚠️  Warning: numpy 2.x detected. Ensure TensorFlow/Keras compatibility.")
    except ImportError:
        pass

    return all_ok

def check_connectivity():
    print_header("Connectivity Check")

    # Check CoinGecko (Primary Data Source)
    try:
        url = "https://api.coingecko.com/api/v3/ping"
        t0 = time.time()
        resp = requests.get(url, timeout=5)
        latency = (time.time() - t0) * 1000
        if resp.status_code == 200:
            print(f"✅ CoinGecko API reachable (Latency: {latency:.0f}ms)")
        else:
            print(f"⚠️  CoinGecko returned status {resp.status_code}")
    except Exception as e:
        print(f"❌ CoinGecko connectivity failed: {e}")

def run_tests():
    print_header("Running Test Suite")
    print("Executing pytest... (this may take a minute)")

    # We run pytest via subprocess to ensure clean environment
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "benchmarks/"], capture_output=False)

    if result.returncode == 0:
        print("\n✅ All tests passed successfully!")
        return True
    else:
        print("\n❌ Tests failed.")
        return False

def main():
    print_header("CRYPTO P'S CRYPTO FORTUNE TELLER - SYSTEM HEALTH CHECK")

    steps = [
        check_python_version,
        check_dependencies,
        check_connectivity,
        run_tests
    ]

    success_count = 0
    for step in steps:
        try:
            if step() is not False:
                success_count += 1
        except Exception as e:
            print(f"❌ Unexpected error in {step.__name__}: {e}")

    print_header("Health Check Summary")
    if success_count == len(steps):
        print("🎉 SYSTEM HEALTH: 100% - Ready to Launch")
        sys.exit(0)
    else:
        print("⚠️  SYSTEM HEALTH: Issues Detected. Review logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
