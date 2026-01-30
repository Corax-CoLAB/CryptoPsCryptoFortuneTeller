## 2025-02-18 - Automated Timeout Verification
**Vulnerability:** External API calls without timeouts can cause the application to hang indefinitely (DoS risk).
**Learning:** Manual code review missed a `requests.get` call in the main application file, highlighting the need for automated scanning.
**Prevention:** Added `tests/test_security_checks.py` to automatically scan the codebase for `requests.get` calls missing the `timeout` parameter.
