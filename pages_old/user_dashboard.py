import streamlit as st
from wallet import get_wallet_balance


def show():
    st.title("📊 User Dashboard")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Please login first")
        return

    balance = get_wallet_balance(user_id)

    st.success(f"Welcome, {st.session_state.get('user_name', 'User')}")
    st.metric("Wallet Balance", f"₹{balance:.2f}")