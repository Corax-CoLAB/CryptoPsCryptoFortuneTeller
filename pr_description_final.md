Title: 'Dev, PelleNybe/Corax CoLAB: [Optimization, Security, Fixes]'

Description:
**What:**
- Optimized iterative loops by removing `.iterrows()` and `.apply()` where applicable, using vectorized operations instead for performance.
- Removed bare `except:` statements and replaced them with `logging.error(..., exc_info=True)` to prevent swallowed errors.
- Improved security of `ExchangeManager` and `FreqtradeManager` by storing credentials using private attributes, masking sensitive information in `__repr__` and `__str__`, and stripping tokens and passwords during `__getstate__`.
- Validated no remaining mock-ups or placeholders are used, retaining purposeful stochastic simulations.
- Fixed NumPy version compatibility in `requirements.txt` to strictly use `<2.0.0` to avoid build breakages across multiple Python versions (3.11/3.12).
- Fixed `calculate_ichimoku_cloud` column requirement check to explicitly verify the presence of the `close` column.

**Why:**
- To improve frontend/backend performance via vectorization, enhance data security, and resolve anti-patterns (such as swallowing exceptions or insecure session serialization).
- To adhere to standard security best practices and ensure optimal runtime capabilities of the platform.
- Prevented pip dependency resolution errors in GitHub Actions CI where `numpy>=2.5.1,<3.0.0` was unresolvable for older Python/TensorFlow combinations.

**Impact:**
- Boosted data processing performance.
- Increased overall robustness in error reporting.
- Prevented sensitive information from being unintentionally exposed or serialized within Streamlit session states.
- Restored CI pipeline functionality.

**Measurement:**
- Verified with the health check and passing pytest suite which resulted in a 100% System Health.
