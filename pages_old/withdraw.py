import streamlit as st
from wallet import request_withdrawal, get_user_withdrawal_requests


def show():
    st.title("🏦 Withdraw Request")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Please login first")
        return

    with st.form("withdraw_form"):
        amount = st.number_input("Amount", min_value=100.0, step=100.0)
        bank_account = st.text_input("Bank Account Number")
        ifsc_code = st.text_input("IFSC Code")
        account_name = st.text_input("Account Holder Name")
        submit = st.form_submit_button("Submit Withdrawal")

    if submit:
        ok, msg = request_withdrawal(user_id, amount, bank_account, ifsc_code, account_name)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.subheader("Your Withdrawal Requests")
    rows = get_user_withdrawal_requests(user_id)
    if rows:
        for row in rows:
            st.write(row)
    else:
        st.info("No withdrawal requests yet")