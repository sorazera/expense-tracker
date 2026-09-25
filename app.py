from datetime import date

import streamlit as st

import db

db.init_db()

st.title("Add transaction")

kind = st.radio("Type", ["Expense", "Income"], horizontal=True).lower()

accounts = {row["id"]: row["name"] for row in db.get_accounts()}
categories = {row["id"]: row["name"] for row in db.get_categories(kind)}

with st.form("add_transaction"):
    tx_date = st.date_input("Date", value=date.today())
    account_id = st.selectbox("Account", accounts, format_func=accounts.get)
    category_id = st.selectbox("Category", categories, format_func=categories.get)
    amount = st.number_input("Amount (₱)", min_value=0.0, step=1.0, format="%.2f")
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Save")

if submitted:
    if amount <= 0:
        st.error("Amount must be greater than ₱0.00.")
    else:
        db.add_transaction(
            tx_date.isoformat(),
            account_id,
            category_id,
            db.to_centavos(amount),
            note.strip(),
        )
        st.success(
            f"Saved {kind} of ₱{amount:,.2f} to {accounts[account_id]} "
            f"({categories[category_id]})."
        )
