## 2025-02-18 - Automated Timeout Verification
**Vulnerability:** External API calls without timeouts can cause the application to hang indefinitely (DoS risk).
**Learning:** Manual code review missed a `requests.get` call in the main application file, highlighting the need for automated scanning.
**Prevention:** Added `tests/test_security_checks.py` to automatically scan the codebase for `requests.get` calls missing the `timeout` parameter.

## 2025-02-19 - Automated XSS Prevention in Streamlit
**Vulnerability:** Unsanitized variables in `st.markdown(..., unsafe_allow_html=True)` allow Cross-Site Scripting (XSS) if data sources are compromised.
**Learning:** Streamlit's `unsafe_allow_html=True` disables default escaping, requiring manual sanitization of all interpolated variables.
**Prevention:** Added `tests/test_xss_scanner.py` to statically enforce `html.escape()` usage in all such markdown calls using Python's `ast` module.
