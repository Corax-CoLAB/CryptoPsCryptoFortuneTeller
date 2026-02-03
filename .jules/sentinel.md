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
