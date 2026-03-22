import streamlit as st
from wallet import get_all_withdrawal_requests, approve_withdrawal, reject_withdrawal


def show():
    st.title("💸 Withdrawal Requests")

    rows = get_all_withdrawal_requests()

    if not rows:
        st.info("No withdrawal requests found")
        return

    for row in rows:
        request_id = row[0]
        name = row[1]
        phone = row[2]
        amount = row[3]
        status = row[4]
        bank = row[5]
        ifsc = row[6]
        account_name = row[7]
        requested_at = row[8]

        st.markdown("---")
        st.write(f"Request ID: {request_id}")
        st.write(f"Name: {name}")
        st.write(f"Phone: {phone}")
        st.write(f"Amount: ₹{amount}")
        st.write(f"Status: {status}")
        st.write(f"Bank: {bank}")
        st.write(f"IFSC: {ifsc}")
        st.write(f"Account Name: {account_name}")
        st.write(f"Requested At: {requested_at}")

        if status == "pending":
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Approve #{request_id}"):
                    ok, msg = approve_withdrawal(request_id, "Approved by admin")
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            with col2:
                if st.button(f"Reject #{request_id}"):
                    ok, msg = reject_withdrawal(request_id, "Rejected by admin")
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)