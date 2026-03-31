import bcrypt
import re
from typing import Tuple, Optional, Dict
from supabase_client import get_supabase_client

supabase = get_supabase_client()

PACKAGE_RULES = {
    "Free": {
        "price": 0,
        "pins": 0,
        "direct_income": 0,
        "level_income": {},
        "royalty_allowed": False,
        "referral_limit": 2,
        "withdrawal": False
    },
    "Starter": {
        "price": 99,
        "pins": 1,
        "direct_income": 30,
        "level_income": {},
        "royalty_allowed": True,
        "withdrawal": True
    },
    "Growth": {
        "price": 299,
        "pins": 3,
        "direct_income": 90,
        "level_income": {1: 10},
        "royalty_allowed": True,
        "withdrawal": True
    },
    "Pro": {
        "price": 599,
        "pins": 7,
        "direct_income": 180,
        "level_income": {1: 10, 2: 5, 3: 3},
        "royalty_allowed": True,
        "withdrawal": True
    }
}


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return len(cleaned) >= 10 and cleaned.isdigit()


def validate_password_strength(password: str) -> Tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


def register_user(name: str, email: str, phone: str, password: str,
                 package: str = "Free", sponsor_code: Optional[str] = None) -> Tuple[bool, str, Optional[Dict]]:
    try:
        if not name or not email or not phone or not password:
            return False, "All fields are required", None

        if not validate_email(email):
            return False, "Invalid email format", None

        if not validate_phone(phone):
            return False, "Invalid phone number", None

        is_strong, msg = validate_password_strength(password)
        if not is_strong:
            return False, msg, None

        if package not in PACKAGE_RULES:
            return False, "Invalid package selected", None

        sponsor_id = None
        if sponsor_code:
            sponsor_result = supabase.table('users').select('id').eq('referral_code', sponsor_code).execute()
            if not sponsor_result.data:
                return False, "Invalid sponsor referral code", None
            sponsor_id = sponsor_result.data[0]['id']

        existing = supabase.table('users').select('id').or_(f"email.eq.{email},phone.eq.{phone}").execute()
        if existing.data:
            return False, "Email or phone already registered", None

        password_hash = hash_password(password)

        user_count = supabase.table('users').select('id', count='exact').execute()
        next_num = (user_count.count or 0) + 1
        user_id = f"UQM{next_num:03d}"

        import hashlib
        referral_code = hashlib.md5(f"{email}{phone}".encode()).hexdigest()[:8].upper()

        new_user = {
            'name': name,
            'email': email,
            'phone': phone,
            'password_hash': password_hash,
            'user_id': user_id,
            'package': package,
            'status': 'Inactive',
            'sponsor_id': sponsor_id,
            'referral_code': referral_code,
            'is_active': False
        }

        result = supabase.table('users').insert(new_user).execute()

        if result.data:
            user_data = result.data[0]
            return True, f"Registration successful! Your User ID is {user_id}", user_data
        else:
            return False, "Registration failed", None

    except Exception as e:
        return False, f"Error: {str(e)}", None


def login_user(identifier: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    try:
        if not identifier or not password:
            return False, "Username and password are required", None

        result = supabase.table('users').select('*').or_(
            f"user_id.eq.{identifier},email.eq.{identifier},phone.eq.{identifier}"
        ).execute()

        if not result.data:
            return False, "Invalid credentials", None

        user = result.data[0]

        if not verify_password(password, user['password_hash']):
            return False, "Invalid credentials", None

        wallet_result = supabase.table('wallets').select('*').eq('user_id', user['id']).execute()
        if wallet_result.data:
            user['wallet'] = wallet_result.data[0]

        return True, "Login successful", user

    except Exception as e:
        return False, f"Error: {str(e)}", None


def update_user_profile(user_id: str, updates: Dict) -> Tuple[bool, str]:
    try:
        allowed_fields = ['name', 'email', 'phone', 'bank_name', 'account_number',
                         'ifsc_code', 'account_holder_name']

        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if not filtered_updates:
            return False, "No valid fields to update"

        if 'email' in filtered_updates and not validate_email(filtered_updates['email']):
            return False, "Invalid email format"

        if 'phone' in filtered_updates and not validate_phone(filtered_updates['phone']):
            return False, "Invalid phone number"

        result = supabase.table('users').update(filtered_updates).eq('id', user_id).execute()

        if result.data:
            return True, "Profile updated successfully"
        else:
            return False, "Update failed"

    except Exception as e:
        return False, f"Error: {str(e)}"


def change_password(user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    try:
        user_result = supabase.table('users').select('password_hash').eq('id', user_id).execute()

        if not user_result.data:
            return False, "User not found"

        if not verify_password(old_password, user_result.data[0]['password_hash']):
            return False, "Current password is incorrect"

        is_strong, msg = validate_password_strength(new_password)
        if not is_strong:
            return False, msg

        new_hash = hash_password(new_password)

        result = supabase.table('users').update({'password_hash': new_hash}).eq('id', user_id).execute()

        if result.data:
            return True, "Password changed successfully"
        else:
            return False, "Password change failed"

    except Exception as e:
        return False, f"Error: {str(e)}"
