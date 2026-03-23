import re

# Fix XSS Issue
with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "r") as f:
    main_content = f.read()

# Issue is at line 117 (or nearby). It's the ticker tape html.
# The ticker tape uses f-string interpolation which the static analysis catches.
# We need to escape the symbol and percentage. Wait, no, we just need to wrap the whole ticker_html string
# generation differently or use html.escape, but it's safe because it's from coingecko API which returns numbers/letters.
# Let's just use html.escape on the variables in the f-string for the ticker to pass the AST checker.

ticker_fix_old = """        ticker_items.append(f"<span style='margin-right: 30px; font-weight: bold;'>🔥 {sym} <span style='color: {color};'>{pct:+.2f}%</span></span>")"""
ticker_fix_new = """        ticker_items.append(f"<span style='margin-right: 30px; font-weight: bold;'>🔥 {html.escape(str(sym))} <span style='color: {html.escape(str(color))}'>{html.escape(f'{pct:+.2f}%')}</span></span>")"""

ticker_fix_old2 = """        ticker_items.append(f"<span style='margin-right: 30px; font-weight: bold;'>🧊 {sym} <span style='color: {color};'>{pct:+.2f}%</span></span>")"""
ticker_fix_new2 = """        ticker_items.append(f"<span style='margin-right: 30px; font-weight: bold;'>🧊 {html.escape(str(sym))} <span style='color: {html.escape(str(color))}'>{html.escape(f'{pct:+.2f}%')}</span></span>")"""

main_content = main_content.replace(ticker_fix_old, ticker_fix_new)
main_content = main_content.replace(ticker_fix_old2, ticker_fix_new2)

with open("streamlit_app/cryptop_crypto_fortune_teller_main.py", "w") as f:
    f.write(main_content)

# Fix FnG Test Issues
# The tests mock requests.get, but in Technical Improvement 1 we changed it to use req_session.get.
# Let's patch tests/test_fng_security.py to mock req_session.get instead of requests.get.

with open("tests/test_fng_security.py", "r") as f:
    test_content = f.read()

test_content = test_content.replace(
    "@patch('modules.cryptop_crypto_fortune_teller_helper.requests.get')",
    "@patch('modules.cryptop_crypto_fortune_teller_helper.req_session.get')"
)

with open("tests/test_fng_security.py", "w") as f:
    f.write(test_content)

print("Tests Fixed")
