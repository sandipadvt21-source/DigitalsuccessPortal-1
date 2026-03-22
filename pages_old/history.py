import streamlit as st
from wallet import get_wallet_history


def show():
    st.title("📜 Wallet History")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Please login first")
        return

    rows = get_wallet_history(user_id)
    if rows:
        for row in rows:
            st.write(row)
    else:
        st.info("No history available")