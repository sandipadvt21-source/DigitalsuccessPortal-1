import streamlit as st
from auth import authenticate_admin


def show():
    st.title("👨‍💼 Admin Login")

    with st.form("admin_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Admin Login")

    if submit:
        ok, result = authenticate_admin(username, password)
        if ok:
            st.session_state.admin_logged_in = True
            st.session_state.admin_id = result["admin_id"]
            st.session_state.admin_name = result["username"]
            st.session_state.page = "Admin Dashboard"
            st.rerun()
        else:
            st.error(result)