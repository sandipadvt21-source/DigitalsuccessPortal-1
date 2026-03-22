import streamlit as st
from admin import get_portal_stats


def show():
    st.title("🛠 Admin Dashboard")

    stats = get_portal_stats()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", stats["total_users"])
    col2.metric("Active Users", stats["active_users"])
    col3.metric("Inactive Users", stats["inactive_users"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Wallet", f"₹{stats['total_balance']:.2f}")
    col5.metric("Pending Withdrawals", stats["pending_withdrawals"])
    col6.metric("Pending Activations", stats["pending_activations"])