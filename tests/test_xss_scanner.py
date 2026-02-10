import ast
import os
import pytest
import glob

class XSSScanner(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
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
        # 1. f-strings (JoinedStr)
        if isinstance(arg, ast.JoinedStr):
            for value in arg.values:
                if isinstance(value, ast.FormattedValue):
                    # Check if the expression is wrapped in html.escape
                    if not self.is_escaped(value.value):
                        self.issues.append(f"{self.filename}:{lineno}: Unescaped variable in f-string st.markdown(unsafe_allow_html=True)")

        # 2. String Concatenation (BinOp with Add)
        elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
            if not self.is_safe_concat(arg):
                 self.issues.append(f"{self.filename}:{lineno}: Potential XSS in string concatenation st.markdown(unsafe_allow_html=True)")

        # 3. .format() calls
        elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'format':
            self.issues.append(f"{self.filename}:{lineno}: Potential XSS in .format() st.markdown(unsafe_allow_html=True)")

        # 4. % formatting (BinOp with Mod)
        elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
             self.issues.append(f"{self.filename}:{lineno}: Potential XSS in % formatting st.markdown(unsafe_allow_html=True)")

        # 5. Direct Variable Usage (Name)
        elif isinstance(arg, ast.Name):
            self.issues.append(f"{self.filename}:{lineno}: Direct variable usage in st.markdown(unsafe_allow_html=True) - audit required")

    def is_safe_concat(self, node):
        # Recursively check if concatenation is only constants or escaped calls
        if isinstance(node, ast.BinOp):
            return self.is_safe_concat(node.left) and self.is_safe_concat(node.right)
        elif isinstance(node, ast.Constant): # String literal
            return True
        elif isinstance(node, ast.Call):
            return self.is_escaped(node) # Only safe if escaped
        return False

    def is_escaped(self, node):
        # Check if node is a call to html.escape or escape
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'escape':
                return True
            if isinstance(node.func, ast.Name) and node.func.id == 'escape':
                return True
        return False

def test_xss_prevention():
    # Scan all python files in streamlit_app/
    repo_root = os.getcwd()
    files = glob.glob(os.path.join(repo_root, 'streamlit_app', '**', '*.py'), recursive=True)

    all_issues = []

    for filepath in files:
        # Skip tests
        if 'tests/' in filepath:
            continue

        with open(filepath, 'r') as f:
            try:
                tree = ast.parse(f.read())
                scanner = XSSScanner(filepath)
                scanner.visit(tree)
                if scanner.issues:
                    all_issues.extend(scanner.issues)
            except SyntaxError:
                pass

    if all_issues:
        pytest.fail("Found potential XSS vulnerabilities:\n" + "\n".join(all_issues))

def test_scanner_logic():
    """
    Sentinel Self-Verification: Ensure scanner detects new patterns.
    """
    code = """
import streamlit as st
import html

# 1. Unsafe f-string
st.markdown(f"Hello {user_input}", unsafe_allow_html=True)

# 2. Unsafe Concatenation
st.markdown("Hello " + user_input, unsafe_allow_html=True)

# 3. Unsafe .format()
st.markdown("Hello {}".format(user_input), unsafe_allow_html=True)

# 4. Unsafe % formatting
st.markdown("Hello %s" % user_input, unsafe_allow_html=True)

# 5. Direct Variable
st.markdown(user_input, unsafe_allow_html=True)

# 6. Safe F-string
st.markdown(f"Hello {html.escape(user_input)}", unsafe_allow_html=True)

# 7. Safe Concatenation (Constants)
st.markdown("Hello " + "World", unsafe_allow_html=True)
"""
    scanner = XSSScanner("dummy.py")
    tree = ast.parse(code)
    scanner.visit(tree)

    issues = scanner.issues
    # We expect 5 issues (1-5 are unsafe, 6-7 are safe)
    assert len(issues) == 5, f"Expected 5 issues, found {len(issues)}: {issues}"
    assert "Unescaped variable in f-string" in issues[0]
    assert "Potential XSS in string concatenation" in issues[1]
    assert "Potential XSS in .format()" in issues[2]
    assert "Potential XSS in % formatting" in issues[3]
    assert "Direct variable usage" in issues[4]

if __name__ == "__main__":
    test_scanner_logic()
    test_xss_prevention()
