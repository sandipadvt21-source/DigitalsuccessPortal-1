import streamlit as st
from admin import get_all_users


def show():
    st.title("👥 All Users")

    rows = get_all_users()
    if rows:
        for row in rows:
            st.write(row)
    else:
        st.info("No users found")