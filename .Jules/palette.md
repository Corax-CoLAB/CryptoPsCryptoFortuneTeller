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
