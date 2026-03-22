import streamlit as st
from auth import authenticate_user


def show():
    st.title("🔐 User Login")

    with st.form("login_form"):
        identifier = st.text_input("Phone or Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        ok, result = authenticate_user(identifier, password)

        if ok:
            st.session_state.user_logged_in = True
            st.session_state.admin_logged_in = False
            st.session_state.user_id = result["user_id"]
            st.session_state.user_name = result["name"]
            st.session_state.user_data = result
            st.session_state.page = "Dashboard"
            st.success("Login successful")
            st.rerun()
        else:
            st.error(result)