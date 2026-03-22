import random
import string
from database import get_connection


def generate_pin(length=6):
    return "".join(random.choices(string.digits, k=length))


def create_activation_pin(phone=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        pin = None
        for _ in range(10):
            candidate = generate_pin()
            cursor.execute("SELECT id FROM activation_pins WHERE pin_code = ?", (candidate,))
            if not cursor.fetchone():
                pin = candidate
                break

        if not pin:
            conn.close()
            return False, "Could not generate unique PIN"

        cursor.execute("""
            INSERT INTO activation_pins (pin_code, user_phone, is_used)
            VALUES (?, ?, 0)
        """, (pin, phone))

        conn.commit()
        conn.close()
        return True, pin
    except Exception as e:
        return False, str(e)


def validate_pin(pin_code, phone):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM activation_pins
            WHERE pin_code = ? AND is_used = 0
        """, (pin_code,))
        pin = cursor.fetchone()

        if not pin:
            conn.close()
            return False, "Invalid or already used PIN"

        pin_id = pin[0]

        cursor.execute("SELECT id, is_active FROM users WHERE phone = ?", (phone,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return False, "User not found"

        user_id, is_active = user

        if is_active:
            conn.close()
            return False, "Account already active"

        cursor.execute("""
            UPDATE activation_pins
            SET is_used = 1, used_at = CURRENT_TIMESTAMP, user_phone = ?
            WHERE id = ?
        """, (phone, pin_id))

        cursor.execute("""
            UPDATE users
            SET is_active = 1
            WHERE id = ?
        """, (user_id,))

        cursor.execute("""
            INSERT INTO wallet_history (user_id, transaction_type, amount, description)
            VALUES (?, 'activation', 0, 'Account activated')
        """, (user_id,))

        conn.commit()
        conn.close()
        return True, "Account activated successfully"
    except Exception as e:
        return False, str(e)


def get_all_pins():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, pin_code, user_phone, is_used, created_at, used_at
        FROM activation_pins
        ORDER BY created_at DESC
    """)
    pins = cursor.fetchall()
    conn.close()
    return pins


def get_pending_activations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, phone, email, created_at
        FROM users
        WHERE is_active = 0
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    conn.close()
    return users