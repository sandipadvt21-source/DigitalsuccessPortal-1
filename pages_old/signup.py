import streamlit as st
from auth import create_user


def show():
    st.title("📝 User Signup")

    with st.form("signup_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Create Account")

    if submit:
        if not all([name, phone, email, password]):
            st.error("All fields are required")
            return

        ok, msg = create_user(name, phone, email, password)
        if ok:
            st.success(msg)
        else:
            st.error(msg)