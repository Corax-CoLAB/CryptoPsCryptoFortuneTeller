import re
import os
import pytest

def check_file_for_requests_timeout(filepath):
    print(f"Checking {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    # Regex to find requests.get calls
    matches = re.finditer(r'requests\.get\((.*?)\)', content, re.DOTALL)

    issues = []
    for match in matches:
        args = match.group(1)
        if 'timeout=' not in args:
            issues.append(match.group(0))

    return issues

def test_requests_timeout():
    """
Ensure all requests.get calls have a timeout.
    """
    files_to_check = [
        'streamlit_app/cryptop_crypto_fortune_teller_main.py',
        'streamlit_app/modules/cryptop_crypto_fortune_teller_helper.py'
    ]

    all_issues = []

    # Check if files exist first (relative to repo root where pytest runs)
    repo_root = os.getcwd()

    for filepath in files_to_check:
        full_path = os.path.join(repo_root, filepath)
        if os.path.exists(full_path):
            issues = check_file_for_requests_timeout(full_path)
            for issue in issues:
                all_issues.append(f"File: {filepath}\nCode: {issue}")
        else:
            pytest.fail(f"File not found: {filepath}")

    if all_issues:
        pytest.fail(f"Found requests.get calls without timeout:\n\n" + "\n\n".join(all_issues))

if __name__ == "__main__":
    test_requests_timeout()
