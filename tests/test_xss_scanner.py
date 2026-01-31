import ast
import os
import pytest

class XSSScanner(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_Call(self, node):
        # Check if call is st.markdown
        is_markdown = False
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'markdown':
            is_markdown = True
        elif isinstance(node.func, ast.Name) and node.func.id == 'markdown':
            is_markdown = True

        if is_markdown:
            # Check for unsafe_allow_html=True
            unsafe = False
            for keyword in node.keywords:
                if keyword.arg == 'unsafe_allow_html':
                    if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        unsafe = True

            if unsafe and node.args:
                arg = node.args[0]
                self.check_unsafe_arg(arg, node.lineno)

        self.generic_visit(node)

    def check_unsafe_arg(self, arg, lineno):
        if isinstance(arg, ast.JoinedStr): # f-string
            for value in arg.values:
                if isinstance(value, ast.FormattedValue):
                    # Check if the expression is wrapped in html.escape
                    if not self.is_escaped(value.value):
                        self.issues.append(f"Line {lineno}: Unescaped variable in st.markdown(unsafe_allow_html=True)")

    def is_escaped(self, node):
        # Check if node is a call to html.escape or escape
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'escape':
                return True
            if isinstance(node.func, ast.Name) and node.func.id == 'escape':
                return True
        return False

def test_xss_prevention():
    scanner = XSSScanner()

    # Path to main app
    # Assumes we are running from repo root
    app_path = os.path.join('streamlit_app', 'cryptop_crypto_fortune_teller_main.py')

    if not os.path.exists(app_path):
        pytest.fail(f"Could not find app file at {app_path}")

    with open(app_path, 'r') as f:
        tree = ast.parse(f.read())

    scanner.visit(tree)

    if scanner.issues:
        pytest.fail("Found potential XSS vulnerabilities:\n" + "\n".join(scanner.issues))

if __name__ == "__main__":
    test_xss_prevention()
