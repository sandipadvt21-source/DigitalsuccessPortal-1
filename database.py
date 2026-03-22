import sqlite3
import os

DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "portal.db")


def init_db():
    """Initialize database with all required tables"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Activation PINs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activation_pins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin_code TEXT UNIQUE NOT NULL,
            user_phone TEXT,
            is_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP,
            FOREIGN KEY(user_phone) REFERENCES users(phone)
        )
    """)

    # Wallet
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Wallet History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT,
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Withdrawal Requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawal_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            bank_account TEXT,
            ifsc_code TEXT,
            account_name TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            rejected_at TIMESTAMP,
            admin_remarks TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Admins
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Login attempts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_failed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


init_db()