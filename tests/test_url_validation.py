import pytest
import sys
import os

# Add streamlit_app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../streamlit_app')))

from modules.utils import validate_url

def test_validate_url_valid():
    """Test valid URLs."""
    valid_urls = [
        "http://google.com",
        "https://google.com",
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "https://api.example.com/v1/endpoint",
        "http://user:pass@example.com"
    ]
    for url in valid_urls:
        assert validate_url(url) is True, f"Failed for {url}"

def test_validate_url_invalid_scheme():
    """Test URLs with invalid schemes."""
    invalid_schemes = [
        "ftp://example.com",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "gopher://example.com",
        "mailto:user@example.com"
    ]
    for url in invalid_schemes:
        assert validate_url(url) is False, f"Failed for {url}"

def test_validate_url_malformed():
    """Test malformed URLs."""
    malformed = [
        "not_a_url",
        "http://",  # No netloc
        "https://", # No netloc
        "",
        None,
        123
    ]
    for url in malformed:
        assert validate_url(url) is False, f"Failed for {url}"

def test_validate_url_whitespace():
    """Test URLs with whitespace (should be stripped)."""
    assert validate_url(" http://example.com ") is True
    assert validate_url("\thttps://example.com\n") is True
