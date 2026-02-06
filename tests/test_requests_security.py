import ast
import os
import pytest
import glob

class RequestsScanner(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
            # Check if it's called on 'requests'
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'requests':
                self.check_requests_call(node)
        self.generic_visit(node)

    def check_requests_call(self, node):
        if not node.args:
            return

        url_arg = node.args[0]

        # Check if URL string contains '?'
        if isinstance(url_arg, ast.Constant) and isinstance(url_arg.value, str):
            if '?' in url_arg.value:
                self.issues.append(f"Line {node.lineno}: requests.{node.func.attr} URL contains '?'. Use 'params' argument instead.")

        # Check f-strings
        elif isinstance(url_arg, ast.JoinedStr):
            # Inspect parts of f-string
            for part in url_arg.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                     if '?' in part.value:
                        self.issues.append(f"Line {node.lineno}: requests.{node.func.attr} URL f-string contains '?'. Use 'params' argument instead.")

def test_requests_params_usage():
    """
    Sentinel Security Check:
    Scan codebase for requests.* calls that embed query parameters in the URL string.
    Enforces usage of 'params' dictionary for better security and encoding.
    """
    repo_root = os.getcwd()
    files = glob.glob(os.path.join(repo_root, '**/*.py'), recursive=True)

    all_issues = []

    for filepath in files:
        # Skip tests themselves and venv
        if 'tests/' in filepath or 'venv/' in filepath or 'site-packages' in filepath:
            continue

        with open(filepath, 'r') as f:
            try:
                tree = ast.parse(f.read())
                scanner = RequestsScanner(filepath)
                scanner.visit(tree)
                if scanner.issues:
                    all_issues.append(f"File: {filepath}")
                    all_issues.extend(scanner.issues)
            except SyntaxError:
                pass # Skip files causing syntax errors (shouldn't happen in valid project)

    if all_issues:
        pytest.fail("Found requests usage violating security best practices:\n" + "\n".join(all_issues))

if __name__ == "__main__":
    test_requests_params_usage()
