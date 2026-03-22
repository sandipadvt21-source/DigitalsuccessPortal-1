import streamlit as st
from activation import create_activation_pin, get_all_pins, get_pending_activations, validate_pin


def show():
    st.title("🔑 Activation PINs")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate New PIN"):
            ok, msg = create_activation_pin()
            if ok:
                st.success(f"New PIN: {msg}")
            else:
                st.error(msg)

    with col2:
        st.write("Pending Activations")
        pending = get_pending_activations()
        for row in pending:
            st.write(row)

    st.subheader("All PINs")
    pins = get_all_pins()
    for row in pins:
        st.write(row)


def activate_account_page():
    st.title("✅ Activate Account")

    with st.form("activate_form"):
        phone = st.text_input("Phone Number")
        pin_code = st.text_input("Activation PIN")
        submit = st.form_submit_button("Activate")

    if submit:
        ok, msg = validate_pin(pin_code, phone)
        if ok:
            st.success(msg)
        else:
            st.error(msg)