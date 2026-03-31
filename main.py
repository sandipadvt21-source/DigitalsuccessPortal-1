import streamlit as st
from datetime import datetime
import pandas as pd

from auth_service import register_user, login_user, update_user_profile, PACKAGE_RULES
from mlm_service import activate_account, get_team_members, get_team_stats, transfer_pin, get_user_pins
from wallet_service import (get_wallet_info, get_transaction_history, get_income_summary,
                            request_withdrawal, get_user_withdrawals)
from support_service import create_support_ticket, get_user_tickets
from admin_service import (verify_admin_login, get_portal_stats, get_all_users,
                           get_inactive_users, get_unused_pins, generate_admin_pin,
                           get_all_withdrawal_requests, approve_withdrawal, reject_withdrawal,
                           get_all_tickets, update_ticket_status, add_manual_credit)

st.set_page_config(
    page_title="UniQueMarketing - MLM Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "page" not in st.session_state:
    st.session_state.page = "login"

if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "user_data" not in st.session_state:
    st.session_state.user_data = None


def inject_css():
    st.markdown("""
<style>
:root {
    --primary: #2563eb;
    --secondary: #3b82f6;
}

html, body, [data-testid="stAppViewContainer"] {
    background: #ffffff !important;
    color: #111827 !important;
}

p, label, span, div, h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
}

input, textarea {
    color: #111827 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #111827 !important;
}

[data-baseweb="input"] input {
    color: #111827 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #111827 !important;
}

input::placeholder, textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

.stButton > button {
    background-color: #2563eb;
    color: #ffffff !important;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.2s;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 16px;
}

.metric-title {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 32px;
    font-weight: 800;
}

.metric-sub {
    font-size: 12px;
    opacity: 0.8;
    margin-top: 4px;
}

.package-card {
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 24px;
    background: #ffffff;
    transition: all 0.3s;
    margin-bottom: 16px;
    cursor: pointer;
}

.package-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    border-color: #2563eb;
}

.package-selected {
    background: #eff6ff;
    border-color: #2563eb;
}

.package-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.package-name {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #111827;
}

.package-price {
    font-size: 36px;
    font-weight: 800;
    color: #2563eb;
    margin-bottom: 12px;
}

.package-desc {
    color: #6b7280;
    margin-bottom: 16px;
    line-height: 1.6;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.status-active {
    background: #dcfce7;
    color: #166534;
}

.status-inactive {
    background: #fee2e2;
    color: #991b1b;
}

.status-pending {
    background: #fef3c7;
    color: #92400e;
}
</style>
""", unsafe_allow_html=True)

inject_css()


def render_sidebar():
    user = st.session_state.user_data

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 24px; font-weight: 800; color: white;">💼 UniQueMarketing</div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.9);">Premium MLM Portal</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div style="padding: 16px; background: #f9fafb; border-radius: 8px; margin-bottom: 20px;">
        <div style="font-size: 11px; color: #6b7280; margin-bottom: 4px;">LOGGED IN AS</div>
        <div style="font-size: 16px; font-weight: 700; color: #111827;">{user.get("name", "User")}</div>
        <div style="font-size: 12px; color: #6b7280;">{user.get("user_id", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    if user and not user.get('is_active'):
        menu_items = [
            ("activate_account", "Activate Account"),
        ]
    else:
        menu_items = [
            ("dashboard", "Dashboard"),
            ("profile", "Profile"),
            ("wallet", "Wallet"),
            ("transfer_epin", "Transfer E-PIN"),
            ("withdraw", "Withdraw"),
            ("income_reports", "Income Reports"),
            ("team", "My Team"),
            ("support", "Support"),
        ]

    for key, label in menu_items:
        if st.sidebar.button(label, key=f"menu_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state.user_logged_in = False
        st.session_state.user_data = None
        st.session_state.page = "login"
        st.rerun()


def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div style="text-align: center; margin: 40px 0;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 42px; font-weight: 800; color: #111827;">💼 UniQueMarketing</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 16px; color: #6b7280; margin-top: 8px;">Premium MLM Portal</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        identifier = st.text_input("User ID / Email / Phone")
        password = st.text_input("Password", type="password")

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Login", use_container_width=True):
                if identifier and password:
                    success, msg, user = login_user(identifier, password)
                    if success:
                        st.session_state.user_logged_in = True
                        st.session_state.admin_logged_in = False
                        st.session_state.user_data = user
                        st.session_state.page = "dashboard"
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Please enter credentials")

        with c2:
            if st.button("Register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

        with c3:
            if st.button("Admin Login", use_container_width=True):
                st.session_state.page = "admin_login"
                st.rerun()


def show_register():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div style="text-align: center; margin: 40px 0;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 36px; font-weight: 800; color: #111827;">Register</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 14px; color: #6b7280; margin-top: 8px;">Create your new account</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password")
        sponsor_code = st.text_input("Sponsor Referral Code (optional)")
        package = st.selectbox("Select Package", list(PACKAGE_RULES.keys()))

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Create Account", use_container_width=True):
                success, msg, user = register_user(name, email, phone, password, package, sponsor_code if sponsor_code else None)
                if success:
                    st.success(msg)
                    st.info("Your account is inactive. Please contact admin for an activation PIN.")
                else:
                    st.error(msg)

        with c2:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()


def show_admin_login():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div style="text-align: center; margin: 40px 0;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 36px; font-weight: 800; color: #111827;">Admin Login</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 14px; color: #6b7280; margin-top: 8px;">Portal Management Access</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        admin_user = st.text_input("Admin Username")
        admin_pass = st.text_input("Admin Password", type="password")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Login as Admin", use_container_width=True):
                if verify_admin_login(admin_user, admin_pass):
                    st.session_state.admin_logged_in = True
                    st.session_state.user_logged_in = False
                    st.session_state.page = "admin_dashboard"
                    st.success("Admin login successful")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

        with c2:
            if st.button("Back", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()


def show_activate_account():
    user = st.session_state.user_data
    st.title("Activate Your Account")

    st.info("Enter your activation PIN to activate your account and start earning.")

    pin_code = st.text_input("Activation PIN")

    if st.button("Activate Account", use_container_width=True):
        if not pin_code:
            st.error("Please enter your activation PIN")
            return

        success, msg = activate_account(user['id'], pin_code)
        if success:
            user['is_active'] = True
            user['status'] = 'Active'
            st.session_state.user_data = user
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def show_dashboard():
    user = st.session_state.user_data
    st.title("Dashboard")

    wallet_info = get_wallet_info(user['id'])
    team_stats = get_team_stats(user['id'])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Wallet Balance</div>
            <div class="metric-value">₹{wallet_info['balance']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-title">Total Earned</div>
            <div class="metric-value">₹{wallet_info['total_earned']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-title">Team Members</div>
            <div class="metric-value">{team_stats['total_team']}</div>
            <div class="metric-sub">{team_stats['active_team']} Active</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-title">Direct Referrals</div>
            <div class="metric-value">{team_stats['direct_team']}</div>
            <div class="metric-sub">{team_stats['active_direct']} Active</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Business Packages")

    package_icons = {
        "Free": "🆓",
        "Starter": "⭐",
        "Growth": "📈",
        "Pro": "👑"
    }

    cols = st.columns(4)
    current_package = user.get("package", "Free")

    for col, (package_name, rule) in zip(cols, PACKAGE_RULES.items()):
        with col:
            icon = package_icons.get(package_name, "🔹")
            is_current = current_package == package_name
            card_class = "package-card package-selected" if is_current else "package-card"

            st.markdown(f"""
            <div class="{card_class}">
                <div class="package-icon">{icon}</div>
                <div class="package-name">{package_name}</div>
                <div class="package-price">₹{rule['price']}</div>
                <div class="package-desc">
                    • {rule['pins']} E-PINs<br>
                    • Direct Income: ₹{rule['direct_income']}<br>
                    • Withdrawal: {'Yes' if rule['withdrawal'] else 'No'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if is_current:
                st.success("Current Package")

    st.markdown("---")

    st.subheader("Your Referral Link")
    referral_link = f"https://yourdomain.com/register?ref={user.get('referral_code', '')}"
    st.code(referral_link, language="text")


def show_profile():
    user = st.session_state.user_data
    st.title("Profile")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Personal Information")
        name = st.text_input("Full Name", value=user.get("name", ""))
        user_id = st.text_input("User ID", value=user.get("user_id", ""), disabled=True)
        email = st.text_input("Email", value=user.get("email", ""))
        phone = st.text_input("Phone", value=user.get("phone", ""))

        status = "Active" if user.get("is_active") else "Inactive"
        st.text_input("Status", value=status, disabled=True)

    with c2:
        st.subheader("Bank Details")
        bank_name = st.text_input("Bank Name", value=user.get("bank_name", "") or "")
        account_number = st.text_input("Account Number", value=user.get("account_number", "") or "")
        ifsc_code = st.text_input("IFSC Code", value=user.get("ifsc_code", "") or "")
        account_holder_name = st.text_input("Account Holder Name", value=user.get("account_holder_name", "") or "")

        if st.button("Save Profile", use_container_width=True):
            updates = {
                'name': name,
                'email': email,
                'phone': phone,
                'bank_name': bank_name,
                'account_number': account_number,
                'ifsc_code': ifsc_code,
                'account_holder_name': account_holder_name
            }

            success, msg = update_user_profile(user['id'], updates)
            if success:
                st.success(msg)
                for key, value in updates.items():
                    user[key] = value
                st.session_state.user_data = user
            else:
                st.error(msg)


def show_wallet():
    user = st.session_state.user_data
    st.title("Wallet")

    wallet_info = get_wallet_info(user['id'])

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Current Balance", f"₹{wallet_info['balance']:.2f}")

    with c2:
        st.metric("Total Earned", f"₹{wallet_info['total_earned']:.2f}")

    st.markdown("---")

    st.subheader("Transaction History")

    transactions = get_transaction_history(user['id'])

    if transactions:
        df = pd.DataFrame(transactions)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        df['amount'] = df['amount'].apply(lambda x: f"₹{float(x):.2f}")
        st.dataframe(df[['created_at', 'transaction_type', 'amount', 'description']], use_container_width=True)
    else:
        st.info("No transactions yet")


def show_transfer_epin():
    user = st.session_state.user_data
    st.title("Transfer E-PIN")

    my_pins = get_user_pins(user['id'])

    unused_pins = [p for p in my_pins if not p['is_used']]

    st.info(f"You have {len(unused_pins)} unused E-PINs available for transfer")

    if unused_pins:
        st.subheader("Your Available E-PINs")
        for pin in unused_pins[:10]:
            st.code(f"PIN: {pin['pin_code']} | Package: {pin['package']}", language="text")

    st.markdown("---")

    st.subheader("Transfer E-PIN")

    recipient_user_id = st.text_input("Recipient User ID")
    pin_code = st.text_input("E-PIN Code to Transfer")

    if st.button("Transfer E-PIN", use_container_width=True):
        if not recipient_user_id or not pin_code:
            st.error("Please enter both recipient ID and PIN code")
            return

        success, msg = transfer_pin(user['id'], recipient_user_id, pin_code)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def show_withdraw():
    user = st.session_state.user_data
    st.title("Withdraw Funds")

    wallet_info = get_wallet_info(user['id'])

    st.info(f"Available Balance: ₹{wallet_info['balance']:.2f}")

    st.markdown("---")

    st.subheader("Request Withdrawal")

    amount = st.number_input("Withdrawal Amount", min_value=100, step=100)
    bank_account = st.text_input("Bank Account Number", value=user.get('account_number', '') or '')
    ifsc_code = st.text_input("IFSC Code", value=user.get('ifsc_code', '') or '')
    account_holder_name = st.text_input("Account Holder Name", value=user.get('account_holder_name', '') or '')

    if st.button("Submit Withdrawal Request", use_container_width=True):
        success, msg = request_withdrawal(user['id'], amount, bank_account, ifsc_code, account_holder_name)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    st.markdown("---")

    st.subheader("Withdrawal History")

    withdrawals = get_user_withdrawals(user['id'])

    if withdrawals:
        df = pd.DataFrame(withdrawals)
        df['requested_at'] = pd.to_datetime(df['requested_at']).dt.strftime('%Y-%m-%d %H:%M')
        df['amount'] = df['amount'].apply(lambda x: f"₹{float(x):.2f}")
        st.dataframe(df[['requested_at', 'amount', 'status', 'admin_remarks']], use_container_width=True)
    else:
        st.info("No withdrawal requests yet")


def show_income_reports():
    user = st.session_state.user_data
    st.title("Income Reports")

    income_summary = get_income_summary(user['id'])

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Direct Income", f"₹{income_summary['direct_income']:.2f}")
        st.metric("Level 1 Income", f"₹{income_summary['level_1_income']:.2f}")

    with c2:
        st.metric("Level 2 Income", f"₹{income_summary['level_2_income']:.2f}")
        st.metric("Level 3 Income", f"₹{income_summary['level_3_income']:.2f}")

    with c3:
        st.metric("Royalty Income", f"₹{income_summary['royalty_income']:.2f}")
        st.metric("Total Income", f"₹{income_summary['total_income']:.2f}")


def show_team():
    user = st.session_state.user_data
    st.title("My Team")

    team_stats = get_team_stats(user['id'])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Team", team_stats['total_team'])

    with c2:
        st.metric("Active Team", team_stats['active_team'])

    with c3:
        st.metric("Direct Referrals", team_stats['direct_team'])

    with c4:
        st.metric("Active Direct", team_stats['active_direct'])

    st.markdown("---")

    st.subheader("Team Members")

    team = get_team_members(user['id'])

    if team:
        df = pd.DataFrame(team)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        st.dataframe(df[['user_id', 'name', 'package', 'status', 'level', 'is_direct', 'created_at']], use_container_width=True)
    else:
        st.info("No team members yet. Start referring to build your team!")


def show_support():
    user = st.session_state.user_data
    st.title("Support")

    st.subheader("Create Support Ticket")

    subject = st.text_input("Subject")
    message = st.text_area("Message", height=150)

    if st.button("Submit Ticket", use_container_width=True):
        if not subject or not message:
            st.error("Please enter both subject and message")
            return

        success, msg = create_support_ticket(user['id'], subject, message)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    st.markdown("---")

    st.subheader("My Tickets")

    tickets = get_user_tickets(user['id'])

    if tickets:
        df = pd.DataFrame(tickets)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df[['created_at', 'subject', 'status', 'admin_response']], use_container_width=True)
    else:
        st.info("No support tickets yet")


def show_admin_dashboard():
    st.title("Admin Dashboard")

    stats = get_portal_stats()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Users", stats['total_users'])
        st.metric("Active Users", stats['active_users'])

    with c2:
        st.metric("Inactive Users", stats['inactive_users'])
        st.metric("Total Balance", f"₹{stats['total_balance']:.2f}")

    with c3:
        st.metric("Pending Withdrawals", stats['pending_withdrawals'])
        st.metric("Unused PINs", stats['unused_pins'])

    with c4:
        st.metric("Open Tickets", stats['open_tickets'])

    st.markdown("---")

    tabs = st.tabs(["Users", "Activation PINs", "Withdrawals", "Support Tickets"])

    with tabs[0]:
        st.subheader("All Users")

        users = get_all_users()

        if users:
            df = pd.DataFrame([{
                'user_id': u['user_id'],
                'name': u['name'],
                'email': u['email'],
                'phone': u['phone'],
                'package': u['package'],
                'status': u['status'],
                'balance': u['wallets'][0]['balance'] if u.get('wallets') else 0,
                'created_at': pd.to_datetime(u['created_at']).strftime('%Y-%m-%d')
            } for u in users])

            st.dataframe(df, use_container_width=True)

    with tabs[1]:
        st.subheader("Generate Activation PIN")

        col1, col2 = st.columns([2, 1])

        with col1:
            package = st.selectbox("Select Package", list(PACKAGE_RULES.keys()))

        with col2:
            if st.button("Generate PIN", use_container_width=True):
                success, msg, pin_code = generate_admin_pin(package)
                if success:
                    st.success(f"PIN Generated: {pin_code}")
                else:
                    st.error(msg)

        st.markdown("---")

        st.subheader("Unused PINs")

        pins = get_unused_pins()

        if pins:
            df = pd.DataFrame(pins)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df[['pin_code', 'package', 'created_at']], use_container_width=True)

    with tabs[2]:
        st.subheader("Withdrawal Requests")

        from wallet_service import get_all_withdrawal_requests

        withdrawals = get_all_withdrawal_requests()

        if withdrawals:
            for w in withdrawals:
                with st.expander(f"Request #{w['id'][:8]} - ₹{w['amount']} - {w['status']}"):
                    st.write(f"**User:** {w['users']['name']} ({w['users']['user_id']})")
                    st.write(f"**Amount:** ₹{w['amount']}")
                    st.write(f"**Status:** {w['status']}")
                    st.write(f"**Bank Account:** {w['bank_account']}")
                    st.write(f"**IFSC:** {w['ifsc_code']}")
                    st.write(f"**Account Holder:** {w['account_holder_name']}")

                    if w['status'] == 'pending':
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button(f"Approve", key=f"approve_{w['id']}"):
                                success, msg = approve_withdrawal(w['id'], "Approved by admin")
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                        with col2:
                            if st.button(f"Reject", key=f"reject_{w['id']}"):
                                success, msg = reject_withdrawal(w['id'], "Rejected by admin")
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

    with tabs[3]:
        st.subheader("Support Tickets")

        tickets = get_all_tickets()

        if tickets:
            for t in tickets:
                with st.expander(f"Ticket #{t['id'][:8]} - {t['subject']} - {t['status']}"):
                    st.write(f"**User:** {t['users']['name']} ({t['users']['user_id']})")
                    st.write(f"**Subject:** {t['subject']}")
                    st.write(f"**Message:** {t['message']}")
                    st.write(f"**Status:** {t['status']}")

                    admin_response = st.text_area("Admin Response", key=f"response_{t['id']}")
                    new_status = st.selectbox("Update Status", ['open', 'in_progress', 'resolved', 'closed'], key=f"status_{t['id']}")

                    if st.button("Update Ticket", key=f"update_{t['id']}"):
                        success, msg = update_ticket_status(t['id'], new_status, admin_response)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    st.markdown("---")

    if st.button("Logout Admin", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.session_state.page = "login"
        st.rerun()


def show_user_portal():
    render_sidebar()

    user = st.session_state.user_data

    if user and not user.get('is_active'):
        show_activate_account()
        return

    current_page = st.session_state.page

    if current_page == "dashboard":
        show_dashboard()
    elif current_page == "profile":
        show_profile()
    elif current_page == "wallet":
        show_wallet()
    elif current_page == "transfer_epin":
        show_transfer_epin()
    elif current_page == "withdraw":
        show_withdraw()
    elif current_page == "income_reports":
        show_income_reports()
    elif current_page == "team":
        show_team()
    elif current_page == "support":
        show_support()
    else:
        show_dashboard()


if st.session_state.admin_logged_in:
    show_admin_dashboard()
elif st.session_state.user_logged_in:
    show_user_portal()
else:
    if st.session_state.page == "admin_login":
        show_admin_login()
    elif st.session_state.page == "register":
        show_register()
    else:
        show_login()
