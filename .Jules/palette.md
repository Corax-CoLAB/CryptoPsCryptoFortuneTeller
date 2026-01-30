# Palette's Journal

## 2024-05-22 - Initial Setup
**Learning:** Journal initialized.
**Action:** Start recording learnings.

## 2024-05-22 - The Power of Tooltips
**Learning:** In complex data dashboards like this crypto fortune teller, users are often overwhelmed by options (models, parameters). Adding simple `help` tooltips to inputs provides immediate context without cluttering the UI.
**Action:** Always audit form inputs for "cognitive load" and add tooltips where the function isn't 100% self-explanatory.

## 2026-01-23 - Destructive Action Confirmation
**Learning:** For destructive actions (like clearing a portfolio), a single click is too risky. Implementing a confirmation state using session state prevents accidental data loss and improves user confidence.
**Action:** Always wrap destructive operations in a "Confirm" pattern using `st.session_state`.

## 2025-10-27 - Streamlit Expander Interaction
**Learning:** Content inside `st.expander` is completely hidden from the DOM/accessibility tree until opened. This creates friction for automation and potentially for screen reader users if the summary isn't descriptive.
**Action:** Ensure expanders defaults are set logically (open for critical paths) and use robust interaction patterns (explicit toggle) in tests.
