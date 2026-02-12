from urllib.parse import urlparse

def validate_url(url):
    """
    Validate that the input is a valid HTTP/HTTPS URL.
    This helps prevent SSRF and other injection attacks via URL fields.
    """
    if not isinstance(url, str):
        return False

    # Strip whitespace
    url = url.strip()

    if not url:
        return False

    try:
        result = urlparse(url)
        # Check scheme
        if result.scheme not in ['http', 'https']:
            return False
        # Check netloc (domain/IP)
        if not result.netloc:
            return False
        return True
    except Exception:
        return False
