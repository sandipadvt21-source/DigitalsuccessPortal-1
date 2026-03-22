from database import get_connection


def get_wallet_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM wallet WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def add_wallet_balance(user_id, amount, description):
    try:
        if amount <= 0:
            return False, "Amount must be greater than 0"

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE wallet
            SET balance = balance + ?
            WHERE user_id = ?
        """, (amount, user_id))

        cursor.execute("""
            INSERT INTO wallet_history (user_id, transaction_type, amount, description)
            VALUES (?, 'credit', ?, ?)
        """, (user_id, amount, description))

        conn.commit()
        conn.close()
        return True, f"₹{amount} added successfully"
    except Exception as e:
        return False, str(e)


def get_wallet_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, transaction_type, amount, description, created_at
        FROM wallet_history
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    history = cursor.fetchall()
    conn.close()
    return history


def request_withdrawal(user_id, amount, bank_account, ifsc_code, account_name):
    try:
        balance = get_wallet_balance(user_id)

        if amount <= 0:
            return False, "Invalid amount"

        if balance < amount:
            return False, "Insufficient balance"

        if amount < 100:
            return False, "Minimum withdrawal amount is ₹100"

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM withdrawal_requests
            WHERE user_id = ? AND status = 'pending'
        """, (user_id,))
        pending = cursor.fetchone()

        if pending:
            conn.close()
            return False, "You already have a pending withdrawal request"

        cursor.execute("""
            INSERT INTO withdrawal_requests
            (user_id, amount, bank_account, ifsc_code, account_name, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (user_id, amount, bank_account, ifsc_code, account_name))

        conn.commit()
        conn.close()
        return True, "Withdrawal request submitted successfully"
    except Exception as e:
        return False, str(e)


def get_user_withdrawal_requests(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, status, bank_account, account_name, requested_at, admin_remarks
        FROM withdrawal_requests
        WHERE user_id = ?
        ORDER BY requested_at DESC
    """, (user_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_all_withdrawal_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wr.id, u.name, u.phone, wr.amount, wr.status,
               wr.bank_account, wr.ifsc_code, wr.account_name, wr.requested_at, wr.admin_remarks
        FROM withdrawal_requests wr
        JOIN users u ON wr.user_id = u.id
        ORDER BY wr.requested_at DESC
    """)
    requests = cursor.fetchall()
    conn.close()
    return requests


def approve_withdrawal(request_id, remarks=""):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, amount, status
            FROM withdrawal_requests
            WHERE id = ?
        """, (request_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False, "Request not found"

        user_id, amount, status = result

        if status != "pending":
            conn.close()
            return False, "Only pending requests can be approved"

        balance = get_wallet_balance(user_id)
        if balance < amount:
            conn.close()
            return False, "Insufficient wallet balance"

        cursor.execute("""
            UPDATE wallet
            SET balance = balance - ?
            WHERE user_id = ?
        """, (amount, user_id))

        cursor.execute("""
            INSERT INTO wallet_history (user_id, transaction_type, amount, description)
            VALUES (?, 'withdrawal', ?, ?)
        """, (user_id, amount, f"Withdrawal approved - Request #{request_id}"))

        cursor.execute("""
            UPDATE withdrawal_requests
            SET status = 'approved', approved_at = CURRENT_TIMESTAMP, admin_remarks = ?
            WHERE id = ?
        """, (remarks, request_id))

        conn.commit()
        conn.close()
        return True, "Withdrawal approved"
    except Exception as e:
        return False, str(e)


def reject_withdrawal(request_id, remarks=""):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status FROM withdrawal_requests
            WHERE id = ?
        """, (request_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False, "Request not found"

        if result[0] != "pending":
            conn.close()
            return False, "Only pending requests can be rejected"

        cursor.execute("""
            UPDATE withdrawal_requests
            SET status = 'rejected', rejected_at = CURRENT_TIMESTAMP, admin_remarks = ?
            WHERE id = ?
        """, (remarks, request_id))

        conn.commit()
        conn.close()
        return True, "Withdrawal rejected"
    except Exception as e:
        return False, str(e)