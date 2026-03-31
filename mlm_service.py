import random
from typing import Tuple, List, Dict, Optional
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


def generate_pin_code() -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def generate_activation_pins(user_id: str, package: str, count: int) -> Tuple[bool, str, List[str]]:
    try:
        rules = PACKAGE_RULES.get(package, PACKAGE_RULES["Free"])
        pins_to_generate = min(count, rules['pins'])

        if pins_to_generate == 0:
            return True, "No pins to generate for this package", []

        generated_pins = []

        for _ in range(pins_to_generate):
            attempts = 0
            while attempts < 50:
                pin_code = generate_pin_code()

                existing = supabase.table('activation_pins').select('id').eq('pin_code', pin_code).execute()

                if not existing.data:
                    pin_data = {
                        'pin_code': pin_code,
                        'package': package,
                        'generated_for_user_id': user_id,
                        'is_used': False
                    }

                    result = supabase.table('activation_pins').insert(pin_data).execute()

                    if result.data:
                        generated_pins.append(pin_code)
                        break

                attempts += 1

        if generated_pins:
            return True, f"Generated {len(generated_pins)} activation pins", generated_pins
        else:
            return False, "Failed to generate pins", []

    except Exception as e:
        return False, f"Error: {str(e)}", []


def activate_account(user_id: str, pin_code: str) -> Tuple[bool, str]:
    try:
        pin_result = supabase.table('activation_pins').select('*').eq('pin_code', pin_code).eq('is_used', False).execute()

        if not pin_result.data:
            return False, "Invalid or already used PIN"

        pin = pin_result.data[0]

        user_result = supabase.table('users').select('*').eq('id', user_id).execute()

        if not user_result.data:
            return False, "User not found"

        user = user_result.data[0]

        if user['is_active']:
            return False, "Account already active"

        package = pin['package']

        supabase.table('activation_pins').update({
            'is_used': True,
            'used_by_user_id': user_id,
            'used_at': 'now()'
        }).eq('id', pin['id']).execute()

        supabase.table('users').update({
            'is_active': True,
            'status': 'Active',
            'package': package
        }).eq('id', user_id).execute()

        supabase.table('wallet_transactions').insert({
            'user_id': user_id,
            'transaction_type': 'credit',
            'amount': 0,
            'description': f'Account activated with {package} package'
        }).execute()

        if user['sponsor_id']:
            process_activation_income(user_id, user['sponsor_id'], package)

        generate_activation_pins(user_id, package, PACKAGE_RULES[package]['pins'])

        return True, "Account activated successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


def process_activation_income(new_user_id: str, sponsor_id: str, package: str):
    try:
        rules = PACKAGE_RULES.get(package, PACKAGE_RULES["Free"])

        direct_income = rules['direct_income']
        if direct_income > 0:
            supabase.table('wallet_transactions').insert({
                'user_id': sponsor_id,
                'transaction_type': 'direct_income',
                'amount': direct_income,
                'description': f'Direct referral income from {package} package',
                'reference_id': new_user_id
            }).execute()

            supabase.table('income_records').insert({
                'user_id': sponsor_id,
                'from_user_id': new_user_id,
                'income_type': 'direct',
                'amount': direct_income,
                'package': package
            }).execute()

        supabase.table('users').update({
            'direct_referrals': supabase.table('users').select('direct_referrals').eq('id', sponsor_id).execute().data[0]['direct_referrals'] + 1,
            'active_direct_referrals': supabase.table('users').select('active_direct_referrals').eq('id', sponsor_id).execute().data[0]['active_direct_referrals'] + 1
        }).eq('id', sponsor_id).execute()

        level_income = rules.get('level_income', {})
        if level_income:
            process_level_income(new_user_id, sponsor_id, package, level_income)

        check_royalty_eligibility(sponsor_id)

    except Exception as e:
        print(f"Error processing activation income: {str(e)}")


def process_level_income(new_user_id: str, direct_sponsor_id: str, package: str, level_income: Dict[int, int]):
    try:
        current_sponsor_id = direct_sponsor_id

        for level, amount in level_income.items():
            if not current_sponsor_id:
                break

            sponsor_result = supabase.table('users').select('*').eq('id', current_sponsor_id).execute()

            if not sponsor_result.data:
                break

            sponsor = sponsor_result.data[0]

            if sponsor['is_active']:
                supabase.table('wallet_transactions').insert({
                    'user_id': current_sponsor_id,
                    'transaction_type': 'level_income',
                    'amount': amount,
                    'description': f'Level {level} income from {package} package',
                    'reference_id': new_user_id
                }).execute()

                supabase.table('income_records').insert({
                    'user_id': current_sponsor_id,
                    'from_user_id': new_user_id,
                    'income_type': f'level_{level}',
                    'amount': amount,
                    'package': package
                }).execute()

            current_sponsor_id = sponsor['sponsor_id']

    except Exception as e:
        print(f"Error processing level income: {str(e)}")


def check_royalty_eligibility(user_id: str):
    try:
        user_result = supabase.table('users').select('*').eq('id', user_id).execute()

        if not user_result.data:
            return

        user = user_result.data[0]

        if user['package'] in ['Starter', 'Growth', 'Pro'] and user['active_direct_referrals'] >= 2:
            supabase.table('users').update({'royalty_eligible': True}).eq('id', user_id).execute()
        else:
            supabase.table('users').update({'royalty_eligible': False}).eq('id', user_id).execute()

    except Exception as e:
        print(f"Error checking royalty eligibility: {str(e)}")


def get_team_members(user_id: str) -> List[Dict]:
    try:
        direct_members = supabase.table('users').select('*').eq('sponsor_id', user_id).execute()

        team = []
        if direct_members.data:
            for member in direct_members.data:
                team.append({
                    'user_id': member['user_id'],
                    'name': member['name'],
                    'package': member['package'],
                    'status': member['status'],
                    'is_active': member['is_active'],
                    'level': 1,
                    'is_direct': True,
                    'created_at': member['created_at']
                })

                sub_team = get_team_members_recursive(member['id'], 2)
                team.extend(sub_team)

        return team

    except Exception as e:
        print(f"Error getting team members: {str(e)}")
        return []


def get_team_members_recursive(user_id: str, level: int, max_level: int = 10) -> List[Dict]:
    if level > max_level:
        return []

    try:
        direct_members = supabase.table('users').select('*').eq('sponsor_id', user_id).execute()

        team = []
        if direct_members.data:
            for member in direct_members.data:
                team.append({
                    'user_id': member['user_id'],
                    'name': member['name'],
                    'package': member['package'],
                    'status': member['status'],
                    'is_active': member['is_active'],
                    'level': level,
                    'is_direct': False,
                    'created_at': member['created_at']
                })

                sub_team = get_team_members_recursive(member['id'], level + 1, max_level)
                team.extend(sub_team)

        return team

    except Exception as e:
        print(f"Error getting team members recursively: {str(e)}")
        return []


def get_team_stats(user_id: str) -> Dict:
    try:
        team = get_team_members(user_id)

        total_team = len(team)
        active_team = len([m for m in team if m['is_active']])
        direct_team = len([m for m in team if m['is_direct']])
        active_direct = len([m for m in team if m['is_direct'] and m['is_active']])

        return {
            'total_team': total_team,
            'active_team': active_team,
            'direct_team': direct_team,
            'active_direct': active_direct
        }

    except Exception as e:
        print(f"Error getting team stats: {str(e)}")
        return {
            'total_team': 0,
            'active_team': 0,
            'direct_team': 0,
            'active_direct': 0
        }


def transfer_pin(from_user_id: str, to_user_id: str, pin_code: str) -> Tuple[bool, str]:
    try:
        pin_result = supabase.table('activation_pins').select('*').eq('pin_code', pin_code).eq('generated_for_user_id', from_user_id).eq('is_used', False).execute()

        if not pin_result.data:
            return False, "PIN not found or already used"

        to_user_result = supabase.table('users').select('id').eq('user_id', to_user_id).execute()

        if not to_user_result.data:
            return False, "Recipient user not found"

        recipient_id = to_user_result.data[0]['id']

        supabase.table('activation_pins').update({
            'generated_for_user_id': recipient_id
        }).eq('pin_code', pin_code).execute()

        supabase.table('wallet_transactions').insert({
            'user_id': from_user_id,
            'transaction_type': 'debit',
            'amount': 0,
            'description': f'E-PIN {pin_code} transferred to {to_user_id}'
        }).execute()

        supabase.table('wallet_transactions').insert({
            'user_id': recipient_id,
            'transaction_type': 'credit',
            'amount': 0,
            'description': f'E-PIN {pin_code} received from transfer'
        }).execute()

        return True, "E-PIN transferred successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_user_pins(user_id: str) -> List[Dict]:
    try:
        pins_result = supabase.table('activation_pins').select('*').eq('generated_for_user_id', user_id).order('created_at', desc=True).execute()

        return pins_result.data if pins_result.data else []

    except Exception as e:
        print(f"Error getting user pins: {str(e)}")
        return []
