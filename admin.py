from database import get_connection


def get_portal_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    inactive_users = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(balance), 0) FROM wallet")
    total_balance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM withdrawal_requests WHERE status = 'pending'")
    pending_withdrawals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    pending_activations = cursor.fetchone()[0]

    conn.close()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_balance": total_balance,
        "pending_withdrawals": pending_withdrawals,
        "pending_activations": pending_activations
    }


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, phone, email, is_active, created_at
        FROM users
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    conn.close()
    return users