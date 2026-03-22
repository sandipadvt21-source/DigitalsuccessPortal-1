import streamlit as st
import json
import os
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="UniQueMarketing - Premium MLM Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# FILES
# =========================================================
USERS_FILE = "users.json"
SUPPORT_FILE = "support.json"
PINS_FILE = "epins.json"
WITHDRAWALS_FILE = "withdrawals.json"
TRANSACTIONS_FILE = "transactions.json"
TEAM_FILE = "team.json"

# =========================================================
# DEFAULT SESSION STATE
# =========================================================

import streamlit as st
import json
import os
from datetime import datetime
import re

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="UniQueMarketing - Premium MLM Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# SESSION INITIALIZE
# =========================================

if "page" not in st.session_state:
    st.session_state.page = "home"
    st.session_state.page = "login"

if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "user_data" not in st.session_state:
    st.session_state.user_data = None

# =========================================================
# FILE HELPERS
# =========================================================
def ensure_file(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)

def load_json(file_path, default_data):
    ensure_file(file_path, default_data)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_data

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def setup_files():
    default_users = [
        {
            "user_id": "UQM001",
            "username": "demo",
            "name": "Demo User",
            "email": "demo@example.com",
            "phone": "9000000001",
            "password": "user123",
            "status": "Active",
            "join_date": str(datetime.now().date()),
            "bank_name": "",
            "account_number": "",
            "ifsc": "",
            "account_holder": "",
            "package": "Starter",
            "wallet": 0
        },
        {
            "user_id": "UQM002",
            "username": "abe",
            "name": "Abe",
            "email": "abe@example.com",
            "phone": "9000000002",
            "password": "user123",
            "status": "Active",
            "join_date": str(datetime.now().date()),
            "bank_name": "",
            "account_number": "",
            "ifsc": "",
            "account_holder": "",
            "package": "None",
            "wallet": 0
        },
        {
            "user_id": "UQM003",
            "username": "user",
            "name": "User Account",
            "email": "user@gmail.com",
            "phone": "9000000003",
            "password": "user123",
            "status": "Active",
            "join_date": str(datetime.now().date()),
            "bank_name": "",
            "account_number": "",
            "ifsc": "",
            "account_holder": "",
            "package": "None",
            "wallet": 0
        }
    ]

    ensure_file(USERS_FILE, default_users)
    ensure_file(SUPPORT_FILE, [])
    ensure_file(PINS_FILE, [])
    ensure_file(WITHDRAWALS_FILE, [])
    ensure_file(TRANSACTIONS_FILE, [])
    ensure_file(TEAM_FILE, [])

setup_files()

# =========================================================
# DATA HELPERS
# =========================================================
def load_users():
    return load_json(USERS_FILE, [])

def save_users(users):
    save_json(USERS_FILE, users)

def generate_user_id(users):
    next_num = len(users) + 1
    return f"UQM{next_num:03d}"

def find_user(identifier, password):
    users = load_users()

    if not isinstance(users, dict):
        return None

    identifier = str(identifier).strip()
    password = str(password).strip()

    for key, user in users.items():
        if not isinstance(user, dict):
            continue

        user_id = str(user.get("user_id", "")).strip()
        username = str(key).strip()
        email = str(user.get("email", "")).strip()
        phone = str(user.get("phone", "")).strip()
        user_password = str(user.get("password", "")).strip()

        if identifier in [user_id, username, email, phone] and user_password == password:
            return user

    return None


def update_current_user(updated_user):
    users = load_users()
    for i, u in enumerate(users):
        if u["user_id"] == updated_user["user_id"]:
            users[i] = updated_user
            break
    save_users(users)
    st.session_state.user_data = updated_user

# =========================================================
# GLOBAL CSS
# =========================================================
def inject_css():
    st.markdown("""
    <style>
    :root {
        --primary: #6d5dfc;
        --secondary: #8b5cf6;
        --dark1: #0b1220;
        --dark2: #16213e;
        --dark3: #1e2d4a;
        --card-border: rgba(255,255,255,0.08);
        --light: #ffffff;
        --muted: #cbd5e1;
        --success: #10b981;
    }

    .stApp {
        background: #f3f4f6;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #091226 100%);
        color: white;
    }

    .brand-box {
        padding: 18px 10px 8px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 10px;
    }

    .brand-title {
        color: #60a5fa;
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .brand-sub {
        color: #cbd5e1;
        font-size: 12px;
    }

    .user-box {
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 16px;
        margin: 14px 0 18px 0;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .user-small {
        color: #cbd5e1;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .user-name {
        color: #60a5fa;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .user-id {
        color: #cbd5e1;
        font-size: 12px;
    }

    .banner {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        padding: 22px 28px;
        border-radius: 18px;
        font-size: 24px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 26px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        margin: 8px 0 16px 0;
    }

    .card {
        background: linear-gradient(135deg, #16213e, #091a3b);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 24px;
        color: white;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        min-height: 190px;
    }

    .metric-card {
        background: linear-gradient(135deg, #16213e, #091a3b);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 22px;
        color: white;
        min-height: 170px;
    }

    .metric-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 24px;
        color: #e2e8f0;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .metric-sub {
        color: #cbd5e1;
        font-size: 14px;
    }

    .package-price {
        font-size: 28px;
        color: #10b981;
        font-weight: 800;
        margin: 10px 0;
    }

    .stTextInput > div > div > input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background: #1e2d4a !important;
        color: #ffffff !important;
        border: 1px solid #3b4d6b !important;
        border-radius: 10px !important;
    }

    .stTextInput > div > div > input:disabled,
    .stNumberInput input:disabled,
    .stTextArea textarea:disabled {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
        background: #1e2d4a !important;
    }

    label, .stTextInput label, .stNumberInput label, .stTextArea label {
        color: #111827 !important;
        font-weight: 600 !important;
    }

    input::placeholder, textarea::placeholder {
        color: #cbd5e1 !important;
        opacity: 1 !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: none !important;
    }

    .login-wrap {
        max-width: 470px;
        margin: 50px auto;
        padding: 30px;
        background: linear-gradient(135deg, #16213e, #0f3460);
        border-radius: 18px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }

    .login-title {
        text-align: center;
        font-size: 34px;
        font-weight: 800;
        color: white;
        margin-bottom: 8px;
    }

    .login-sub {
        text-align: center;
        color: #cbd5e1;
        margin-bottom: 24px;
    }

    .small-note {
        color: #cbd5e1;
        text-align: center;
        font-size: 12px;
        margin-top: 12px;
    }

    hr {
        border: none;
        border-top: 1px solid #d1d5db;
        margin: 28px 0;
    }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# =========================================================
# UI HELPERS
# =========================================================
def show_top_banner(text):
    st.markdown(f'<div class="banner">{text}</div>', unsafe_allow_html=True)

def render_sidebar():
    user = st.session_state.user_data

    st.sidebar.markdown("""
    <div class="brand-box">
        <div class="brand-title">💼 UniQueMarketing</div>
        <div class="brand-sub">Premium MLM Portal</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div class="user-box">
        <div class="user-small">LOGGED IN AS</div>
        <div class="user-name">{user.get("name", "User")}</div>
        <div class="user-id">{user.get("user_id", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("### Navigation")

    menu_items = [
        ("dashboard", "🏠 Dashboard"),
        ("profile", "👤 Profile"),
        ("transfer_epin", "🎫 Transfer E-Pin"),
        ("withdraw", "💸 Withdraw"),
        ("income_reports", "📊 Income Reports"),
        ("team", "👥 My Team"),
        ("support", "🆘 Support"),
    ]

    for key, label in menu_items:
        if st.sidebar.button(label, key=f"menu_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user_logged_in = False
        st.session_state.user_data = None
        st.session_state.page = "login"
        st.rerun()

# =========================================================
# AUTH PAGES
# =========================================================
def show_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">💼 UniQueMarketing</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Premium MLM Portal Login</div>', unsafe_allow_html=True)

    identifier = st.text_input("User ID / Username / Email / Phone")
    password = st.text_input("Password", type="password")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Login", use_container_width=True):
            user = find_user(identifier, password)
            if user:
                st.session_state.user_logged_in = True
                st.session_state.admin_logged_in = False
                st.session_state.user_data = user
                st.session_state.page = "dashboard"
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid login credentials")

    with c2:
        if st.button("Register", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

    with c3:
        if st.button("Admin Login", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()

    st.markdown('<div class="small-note">Demo User ID: UQM003 | Password: user123</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_register():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">📝 Register</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Create your new member account</div>', unsafe_allow_html=True)

    name = st.text_input("Full Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Create Account", use_container_width=True):
            users = load_users()

            for u in users:
                if u["username"] == username:
                    st.error("Username already exists")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                if u["email"] == email:
                    st.error("Email already exists")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                if u["phone"] == phone:
                    st.error("Phone already exists")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return

            if not name or not username or not email or not phone or not password:
                st.error("Please fill all fields")
            else:
                new_user = {
                    "user_id": generate_user_id(users),
                    "username": username,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password": password,
                    "status": "Active",
                    "join_date": str(datetime.now().date()),
                    "bank_name": "",
                    "account_number": "",
                    "ifsc": "",
                    "account_holder": "",
                    "package": "None",
                    "wallet": 0
                }
                users.append(new_user)
                save_users(users)
                st.success(f"Account created successfully. Your User ID is {new_user['user_id']}")
                st.info("Now go back and login.")

    with c2:
        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def show_admin_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🛠 Admin Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Portal management access</div>', unsafe_allow_html=True)

    admin_user = st.text_input("Admin Username", key="admin_user")
    admin_pass = st.text_input("Admin Password", type="password", key="admin_pass")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Login as Admin", use_container_width=True):
            if admin_user == "admin" and admin_pass == "admin123":
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

    st.markdown('<div class="small-note">Admin Username: admin | Password: admin123</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# USER PAGES
# =========================================================
def show_dashboard():
    show_top_banner("🏠 Dashboard")

    st.markdown('<div class="section-title">📦 Business Packages</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    packages = [
        ("🌟", "₹3,000", "Starter Package", "Perfect for beginners. Get started with basic benefits."),
        ("💎", "₹6,000", "Professional Package", "Premium benefits & higher earning potential."),
        ("👑", "₹15,000", "Elite Package", "Maximum benefits & exclusive rewards."),
    ]

    cols = [c1, c2, c3]
    for col, pkg in zip(cols, packages):
        icon, price, title, desc = pkg
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:34px;">{icon}</div>
                <div class="package-price">{price}</div>
                <div style="font-size:18px;font-weight:700;margin-bottom:12px;">{title}</div>
                <div style="color:#cbd5e1;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Activate", key=f"activate_{title}", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Quick Statistics</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    user = st.session_state.user_data

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👥 Team Members</div>
            <div class="metric-value">0</div>
            <div class="metric-sub">0 Active</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📊 Total Transactions</div>
            <div class="metric-value">0</div>
            <div class="metric-sub">This Month</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📅 Member Since</div>
            <div class="metric-value">{user.get("join_date","-")}</div>
            <div class="metric-sub">Account Created</div>
        </div>
        """, unsafe_allow_html=True)

def show_profile():
    user = st.session_state.user_data
    show_top_banner("👤 Your Profile")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card"><h2>Personal Information</h2></div>', unsafe_allow_html=True)
        name = st.text_input("Full Name", value=user.get("name", ""), key="profile_name")
        user_id = st.text_input("User ID", value=user.get("user_id", ""), disabled=True)
        email = st.text_input("Email", value=user.get("email", ""), key="profile_email")
        phone = st.text_input("Phone", value=user.get("phone", ""), key="profile_phone")
        status = st.text_input("Account Status", value=user.get("status", "Active"), disabled=True)
        join_date = st.text_input("Join Date", value=user.get("join_date", ""), disabled=True)

    with c2:
        st.markdown('<div class="card"><h2>Bank Details</h2></div>', unsafe_allow_html=True)
        bank_name = st.text_input("Bank Name", value=user.get("bank_name", ""), key="bank_name")
        account_number = st.text_input("Account Number", value=user.get("account_number", ""), key="account_number")
        ifsc = st.text_input("IFSC Code", value=user.get("ifsc", ""), key="ifsc")
        account_holder = st.text_input("Account Holder Name", value=user.get("account_holder", ""), key="account_holder")

        if st.button("💾 Save Bank Details", use_container_width=True):
            user["name"] = name
            user["email"] = email
            user["phone"] = phone
            user["bank_name"] = bank_name
            user["account_number"] = account_number
            user["ifsc"] = ifsc
            user["account_holder"] = account_holder
            update_current_user(user)
            st.success("Profile updated successfully")

def show_transfer_epin():
    show_top_banner("🎫 Transfer E-Pin")

    st.markdown('<div class="section-title">Transfer E-Pin to another member</div>', unsafe_allow_html=True)

    recipient = st.text_input("Recipient User ID")
    pin_code = st.text_input("E-Pin Code")

    if st.button("Transfer E-Pin", use_container_width=True):
        if recipient and pin_code:
            st.success(f"E-Pin {pin_code} transferred to {recipient}")
        else:
            st.error("Please enter recipient ID and E-Pin")

def show_withdraw():
    user = st.session_state.user_data
    show_top_banner("💸 Withdraw Funds")

    st.markdown('<div class="section-title">Request Withdrawal</div>', unsafe_allow_html=True)

    st.info(f"Available Wallet Balance: ₹{user.get('wallet', 0)}")

    amount = st.number_input("Enter Withdrawal Amount", min_value=0, step=100)

    if st.button("Submit Withdrawal Request", use_container_width=True):
        if amount <= 0:
            st.error("Enter a valid amount")
            return

        if amount > user.get("wallet", 0):
            st.error("Insufficient wallet balance")
            return

        withdrawals = load_json(WITHDRAWALS_FILE, [])
        withdrawals.append({
            "user_id": user["user_id"],
            "name": user["name"],
            "amount": amount,
            "status": "Pending",
            "date": str(datetime.now())
        })
        save_json(WITHDRAWALS_FILE, withdrawals)
        st.success("Withdrawal request submitted successfully")

def show_income_reports():
    show_top_banner("📊 Income Reports")

    st.markdown('<div class="section-title">Income Summary</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Direct Income", "₹0")
    with c2:
        st.metric("Level Income", "₹0")
    with c3:
        st.metric("Total Income", "₹0")

    st.markdown('<div class="section-title">Recent Transactions</div>', unsafe_allow_html=True)
    transactions = load_json(TRANSACTIONS_FILE, [])

    if transactions:
        st.dataframe(transactions, use_container_width=True)
    else:
        st.info("No transactions available")

def show_team():
    show_top_banner("👥 My Team")

    st.markdown('<div class="section-title">Team Overview</div>', unsafe_allow_html=True)

    team_data = load_json(TEAM_FILE, [])
    if team_data:
        st.dataframe(team_data, use_container_width=True)
    else:
        st.info("No team members added yet")

def show_support():
    user = st.session_state.user_data
    show_top_banner("🆘 Support & Help")

    subject = st.text_input("Subject")
    message = st.text_area("Describe your issue")

    if st.button("Submit Support Ticket", use_container_width=True):
        if subject and message:
            tickets = load_json(SUPPORT_FILE, [])
            tickets.append({
                "user_id": user["user_id"],
                "name": user["name"],
                "subject": subject,
                "message": message,
                "date": str(datetime.now()),
                "status": "Open"
            })
            save_json(SUPPORT_FILE, tickets)
            st.success("Support ticket submitted successfully")
        else:
            st.error("Please fill subject and message")

# =========================================================
# ADMIN PAGE
# =========================================================
def show_admin_dashboard():
    st.title("🛠 Admin Dashboard")
    st.success("Admin panel active")

    users = load_users()
    withdrawals = load_json(WITHDRAWALS_FILE, [])
    tickets = load_json(SUPPORT_FILE, [])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Users", len(users))
    with c2:
        st.metric("Withdraw Requests", len(withdrawals))
    with c3:
        st.metric("Support Tickets", len(tickets))

    if st.button("Logout Admin", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.session_state.page = "login"
        st.rerun()

    st.markdown("## Users List")
    if users:
        st.dataframe(users, use_container_width=True)
    else:
        st.info("No users found")

    st.markdown("## Withdrawal Requests")
    if withdrawals:
        st.dataframe(withdrawals, use_container_width=True)
    else:
        st.info("No withdrawal requests")

    st.markdown("## Support Tickets")
    if tickets:
        st.dataframe(tickets, use_container_width=True)
    else:
        st.info("No support tickets")

# =========================================================
# USER PORTAL ROUTER
# =========================================================
def show_user_portal():
    render_sidebar()

    current_page = st.session_state.page

    if current_page == "dashboard":
        show_dashboard()
    elif current_page == "profile":
        show_profile()
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

# =========================================================
# MAIN ROUTING
# =========================================================
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