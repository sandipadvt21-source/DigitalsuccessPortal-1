from typing import Dict, List, Tuple
from supabase_client import get_supabase_client
import bcrypt

supabase = get_supabase_client()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_admin_login(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH.encode('utf-8'))


def get_portal_stats() -> Dict:
    try:
        users_result = supabase.table('users').select('id, is_active, status').execute()

        total_users = 0
        active_users = 0
        inactive_users = 0

        if users_result.data:
            total_users = len(users_result.data)
            active_users = len([u for u in users_result.data if u['is_active']])
            inactive_users = total_users - active_users

        wallets_result = supabase.table('wallets').select('balance').execute()

        total_balance = 0.0
        if wallets_result.data:
            total_balance = sum(float(w['balance']) for w in wallets_result.data)

        withdrawals_result = supabase.table('withdrawal_requests').select('id, status').eq('status', 'pending').execute()

        pending_withdrawals = len(withdrawals_result.data) if withdrawals_result.data else 0

        pins_result = supabase.table('activation_pins').select('id, is_used').eq('is_used', False).execute()

        unused_pins = len(pins_result.data) if pins_result.data else 0

        tickets_result = supabase.table('support_tickets').select('id, status').eq('status', 'open').execute()

        open_tickets = len(tickets_result.data) if tickets_result.data else 0

        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'total_balance': total_balance,
            'pending_withdrawals': pending_withdrawals,
            'unused_pins': unused_pins,
            'open_tickets': open_tickets
        }

    except Exception as e:
        print(f"Error getting portal stats: {str(e)}")
        return {
            'total_users': 0,
            'active_users': 0,
            'inactive_users': 0,
            'total_balance': 0.0,
            'pending_withdrawals': 0,
            'unused_pins': 0,
            'open_tickets': 0
        }


def get_all_users() -> List[Dict]:
    try:
        users_result = supabase.table('users').select('*, wallets(balance, total_earned)').order('created_at', desc=True).execute()

        return users_result.data if users_result.data else []

    except Exception as e:
        print(f"Error getting all users: {str(e)}")
        return []


def get_inactive_users() -> List[Dict]:
    try:
        users_result = supabase.table('users').select('*').eq('is_active', False).order('created_at', desc=True).execute()

        return users_result.data if users_result.data else []

    except Exception as e:
        print(f"Error getting inactive users: {str(e)}")
        return []


def get_unused_pins() -> List[Dict]:
    try:
        pins_result = supabase.table('activation_pins').select('*').eq('is_used', False).order('created_at', desc=True).execute()

        return pins_result.data if pins_result.data else []

    except Exception as e:
        print(f"Error getting unused pins: {str(e)}")
        return []


def get_all_pins() -> List[Dict]:
    try:
        pins_result = supabase.table('activation_pins').select('*').order('created_at', desc=True).execute()

        return pins_result.data if pins_result.data else []

    except Exception as e:
        print(f"Error getting all pins: {str(e)}")
        return []


def generate_admin_pin(package: str) -> Tuple[bool, str, str]:
    try:
        import random

        attempts = 0
        while attempts < 50:
            pin_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            existing = supabase.table('activation_pins').select('id').eq('pin_code', pin_code).execute()

            if not existing.data:
                pin_data = {
                    'pin_code': pin_code,
                    'package': package,
                    'is_used': False
                }

                result = supabase.table('activation_pins').insert(pin_data).execute()

                if result.data:
                    return True, "PIN generated successfully", pin_code

            attempts += 1

        return False, "Failed to generate unique PIN", ""

    except Exception as e:
        return False, f"Error: {str(e)}", ""


def get_user_details(user_id: str) -> Dict:
    try:
        user_result = supabase.table('users').select('*, wallets(*)').eq('id', user_id).execute()

        if user_result.data:
            return user_result.data[0]
        return {}

    except Exception as e:
        print(f"Error getting user details: {str(e)}")
        return {}


def update_user_status(user_id: str, status: str, is_active: bool) -> Tuple[bool, str]:
    try:
        result = supabase.table('users').update({
            'status': status,
            'is_active': is_active
        }).eq('id', user_id).execute()

        if result.data:
            return True, "User status updated successfully"
        else:
            return False, "Failed to update user status"

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_recent_activities(limit: int = 50) -> List[Dict]:
    try:
        transactions = supabase.table('wallet_transactions').select('*, users(name, user_id)').order('created_at', desc=True).limit(limit).execute()

        return transactions.data if transactions.data else []

    except Exception as e:
        print(f"Error getting recent activities: {str(e)}")
        return []


def get_income_distribution_stats() -> Dict:
    try:
        income_result = supabase.table('income_records').select('income_type, amount').execute()

        stats = {
            'direct_income': 0.0,
            'level_income': 0.0,
            'royalty_income': 0.0,
            'total_distributed': 0.0
        }

        if income_result.data:
            for record in income_result.data:
                amount = float(record['amount'])
                income_type = record['income_type']

                if income_type == 'direct':
                    stats['direct_income'] += amount
                elif income_type.startswith('level_'):
                    stats['level_income'] += amount
                elif income_type == 'royalty':
                    stats['royalty_income'] += amount

                stats['total_distributed'] += amount

        return stats

    except Exception as e:
        print(f"Error getting income distribution stats: {str(e)}")
        return {
            'direct_income': 0.0,
            'level_income': 0.0,
            'royalty_income': 0.0,
            'total_distributed': 0.0
        }
