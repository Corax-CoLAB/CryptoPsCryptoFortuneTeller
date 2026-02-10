## 2025-02-18 - Automated Timeout Verification
**Vulnerability:** External API calls without timeouts can cause the application to hang indefinitely (DoS risk).
**Learning:** Manual code review missed a `requests.get` call in the main application file, highlighting the need for automated scanning.
**Prevention:** Added `tests/test_security_checks.py` to automatically scan the codebase for `requests.get` calls missing the `timeout` parameter.

## 2025-02-19 - Automated XSS Prevention in Streamlit
**Vulnerability:** Unsanitized variables in `st.markdown(..., unsafe_allow_html=True)` allow Cross-Site Scripting (XSS) if data sources are compromised.
**Learning:** Streamlit's `unsafe_allow_html=True` disables default escaping, requiring manual sanitization of all interpolated variables.
**Prevention:** Added `tests/test_xss_scanner.py` to statically enforce `html.escape()` usage in all such markdown calls using Python's `ast` module.

## 2026-02-01 - [DoS Risk] Implicit API Timeouts
**Vulnerability:** The `pycoingecko` library's wrapper class `CoinGeckoAPI` has a default timeout of 120 seconds, which is too long for a user-facing application and can lead to resource exhaustion if the API hangs.
**Learning:** Third-party wrappers often abstract away low-level configuration like timeouts, leading to hidden availability risks. Explicitly inspecting and overriding these defaults is crucial.
**Prevention:** Always verify default timeouts for 3rd party API clients and explicitly set them to fail fast (e.g., 20s) to prevent hanging processes.

## 2026-02-02 - [DoS Risk] Unbounded Batch Processing
**Vulnerability:** The `get_batch_historical_prices` function processed all input assets without a limit. A malicious actor (or user error) could request hundreds of assets, triggering API rate limits and exhausting application resources (threads/connections).
**Learning:** Functions that accept list inputs and trigger external API calls for each item must have explicit upper bounds on the input size, independent of UI limits.
**Prevention:** Enforced a strict limit (10 items) in the logic layer (`cryptop_crypto_fortune_teller_helper.py`) and added a warning when truncation occurs.

## 2026-05-21 - [High Risk] Disabled XSRF Protection
**Vulnerability:** `enableXsrfProtection` was explicitly set to `false` in `.streamlit/config.toml`, leaving the application vulnerable to Cross-Site Request Forgery attacks, which could allow attackers to perform actions on behalf of authenticated users (e.g., clearing portfolios).
**Learning:** Security defaults in frameworks like Streamlit are there for a reason. Explicitly disabling them (often for "convenience" during dev) creates a persistent vulnerability if carried to production.
**Prevention:** Added `tests/test_config_security.py` to enforce that critical security flags (`enableXsrfProtection`, `enableCORS`) are not disabled in the configuration.

## 2026-06-15 - [DoS Risk] Unbounded Model Forecasting
**Vulnerability:** Forecasting models (LSTM, ARIMA, Prophet) accepted unbounded `periods` and `history` length. A malicious or accidental request with extremely large values (e.g., 10,000 days forecast) caused excessive computation time (DoS) and potential memory exhaustion.
**Learning:** Data science models are often computationally expensive. Always enforce strict limits on input dimensions (e.g., history length, forecast horizon) at the model function level, regardless of UI constraints.
**Prevention:** Implemented `MAX_FORECAST_HORIZON` (365) and `MAX_HISTORY_LENGTH` (2000) constants in `cryptop_crypto_fortune_teller_models.py` and enforced them in all forecasting functions.

## 2026-07-01 - [High Risk] Insecure URL Construction
**Vulnerability:** User input (`coin_id`) was directly interpolated into a `requests.get` URL string. While the input source (CoinGecko list) is currently trusted, this pattern allows for potential injection or path traversal if the source is compromised or the logic changes.
**Learning:** Never trust input when constructing URLs, even if it comes from an API. F-string interpolation for URLs bypasses standard encoding mechanisms.
**Prevention:** Refactored to use `requests.get(..., params=params)` for query parameters and added strict regex validation (`^[a-z0-9\-\.]+$`) for path parameters. Added `tests/test_requests_security.py` to statically detect literal query strings in `requests` calls.

## 2026-08-01 - [DoS Risk] Timedelta Overflow
**Vulnerability:** User-controlled `days` parameter in historical data fetching caused a `pd.errors.OutOfBoundsTimedelta` exception (DoS) when exceeding pandas' timestamp limits (~106k days).
**Learning:** Libraries like pandas have internal limits (e.g., Timestamp range) that are not always obvious. Input validation must account for these library-specific constraints, not just logical business rules.
**Prevention:** Introduced `MAX_HISTORY_DAYS` constant and wrapped `pd.Timedelta` calculations in `try...except` blocks to handle overflows gracefully.

## 2026-09-01 - [High Risk] Incomplete XSS Scanning
**Vulnerability:** The existing XSS scanner only detected unsafe f-strings in `st.markdown`, missing string concatenation, `.format()`, `%` formatting, and direct variable usage, which could allow XSS if developers used older string formatting methods.
**Learning:** Security tools must account for all valid Python syntax for string construction, not just the most common ones. Gaps in static analysis create a false sense of security.
**Prevention:** Enhanced `tests/test_xss_scanner.py` to detect `ast.BinOp` (concatenation/modulo), `ast.Call` (.format), and `ast.Name` (variables) in sensitive sinks, preventing these bypasses.
