import sys
import os
import pytest

def test_streamlit_security_config():
    """
    Sentinel Security Check:
    Verify that critical Streamlit security features are NOT disabled.
    """
    config_path = os.path.join(".streamlit", "config.toml")

    if not os.path.exists(config_path):
        pytest.skip("Config file not found")

    try:
        import tomllib
        with open(config_path, "rb") as f:
            config = tomllib.load(f)

        server = config.get("server", {})

        # Check XSRF
        xsrf = server.get("enableXsrfProtection")
        assert xsrf is not False, "enableXsrfProtection is explicitly set to false. This leaves the app vulnerable to CSRF attacks."

        # Check CORS
        cors = server.get("enableCORS")
        assert cors is not False, "enableCORS is explicitly set to false. This allows cross-origin requests from any domain."

    except ImportError:
        # Fallback for older python without tomllib
        with open(config_path, "r") as f:
            content = f.read()

        # Basic string check (ignoring comments/structure for simplicity in fallback)
        import re
        # Look for enableXsrfProtection = false or enableXsrfProtection=false, case insensitive
        if re.search(r'enableXsrfProtection\s*=\s*false', content, re.IGNORECASE):
             pytest.fail("enableXsrfProtection is explicitly set to false (regex check).")

        if re.search(r'enableCORS\s*=\s*false', content, re.IGNORECASE):
             pytest.fail("enableCORS is explicitly set to false (regex check).")
