from typing import Tuple, List, Dict, Optional
from supabase_client import get_supabase_client

supabase = get_supabase_client()


def get_wallet_balance(user_id: str) -> float:
    try:
        wallet_result = supabase.table('wallets').select('balance').eq('user_id', user_id).execute()

        if wallet_result.data:
            return float(wallet_result.data[0]['balance'])
        return 0.0

    except Exception as e:
        print(f"Error getting wallet balance: {str(e)}")
        return 0.0


def get_wallet_info(user_id: str) -> Dict:
    try:
        wallet_result = supabase.table('wallets').select('*').eq('user_id', user_id).execute()

        if wallet_result.data:
            return {
                'balance': float(wallet_result.data[0]['balance']),
                'total_earned': float(wallet_result.data[0]['total_earned']),
                'updated_at': wallet_result.data[0]['updated_at']
            }
        return {
            'balance': 0.0,
            'total_earned': 0.0,
            'updated_at': None
        }

    except Exception as e:
        print(f"Error getting wallet info: {str(e)}")
        return {
            'balance': 0.0,
            'total_earned': 0.0,
            'updated_at': None
        }


def get_transaction_history(user_id: str, limit: int = 100) -> List[Dict]:
    try:
        transactions_result = supabase.table('wallet_transactions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()

        return transactions_result.data if transactions_result.data else []

    except Exception as e:
        print(f"Error getting transaction history: {str(e)}")
        return []


def get_income_summary(user_id: str) -> Dict:
    try:
        income_result = supabase.table('income_records').select('*').eq('user_id', user_id).execute()

        summary = {
            'direct_income': 0.0,
            'level_1_income': 0.0,
            'level_2_income': 0.0,
            'level_3_income': 0.0,
            'royalty_income': 0.0,
            'total_income': 0.0
        }

        if income_result.data:
            for record in income_result.data:
                amount = float(record['amount'])
                income_type = record['income_type']

                if income_type == 'direct':
                    summary['direct_income'] += amount
                elif income_type == 'level_1':
                    summary['level_1_income'] += amount
                elif income_type == 'level_2':
                    summary['level_2_income'] += amount
                elif income_type == 'level_3':
                    summary['level_3_income'] += amount
                elif income_type == 'royalty':
                    summary['royalty_income'] += amount

                summary['total_income'] += amount

        return summary

    except Exception as e:
        print(f"Error getting income summary: {str(e)}")
        return {
            'direct_income': 0.0,
            'level_1_income': 0.0,
            'level_2_income': 0.0,
            'level_3_income': 0.0,
            'royalty_income': 0.0,
            'total_income': 0.0
        }


def request_withdrawal(user_id: str, amount: float, bank_account: str,
                      ifsc_code: str, account_holder_name: str) -> Tuple[bool, str]:
    try:
        if amount <= 0:
            return False, "Invalid withdrawal amount"

        if amount < 100:
            return False, "Minimum withdrawal amount is 100"

        balance = get_wallet_balance(user_id)

        if balance < amount:
            return False, "Insufficient wallet balance"

        pending_result = supabase.table('withdrawal_requests').select('id').eq('user_id', user_id).eq('status', 'pending').execute()

        if pending_result.data:
            return False, "You already have a pending withdrawal request"

        withdrawal_data = {
            'user_id': user_id,
            'amount': amount,
            'status': 'pending',
            'bank_account': bank_account,
            'ifsc_code': ifsc_code,
            'account_holder_name': account_holder_name
        }

        result = supabase.table('withdrawal_requests').insert(withdrawal_data).execute()

        if result.data:
            return True, "Withdrawal request submitted successfully"
        else:
            return False, "Failed to submit withdrawal request"

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_user_withdrawals(user_id: str) -> List[Dict]:
    try:
        withdrawals_result = supabase.table('withdrawal_requests').select('*').eq('user_id', user_id).order('requested_at', desc=True).execute()

        return withdrawals_result.data if withdrawals_result.data else []

    except Exception as e:
        print(f"Error getting user withdrawals: {str(e)}")
        return []


def get_all_withdrawal_requests() -> List[Dict]:
    try:
        withdrawals_result = supabase.table('withdrawal_requests').select('*, users(name, user_id, email, phone)').order('requested_at', desc=True).execute()

        return withdrawals_result.data if withdrawals_result.data else []

    except Exception as e:
        print(f"Error getting all withdrawal requests: {str(e)}")
        return []


def approve_withdrawal(withdrawal_id: str, admin_remarks: str = "") -> Tuple[bool, str]:
    try:
        withdrawal_result = supabase.table('withdrawal_requests').select('*').eq('id', withdrawal_id).execute()

        if not withdrawal_result.data:
            return False, "Withdrawal request not found"

        withdrawal = withdrawal_result.data[0]

        if withdrawal['status'] != 'pending':
            return False, "Only pending requests can be approved"

        balance = get_wallet_balance(withdrawal['user_id'])

        if balance < withdrawal['amount']:
            return False, "User has insufficient balance"

        supabase.table('wallet_transactions').insert({
            'user_id': withdrawal['user_id'],
            'transaction_type': 'withdrawal',
            'amount': withdrawal['amount'],
            'description': f"Withdrawal approved - Request #{withdrawal_id[:8]}",
            'reference_id': withdrawal_id
        }).execute()

        supabase.table('withdrawal_requests').update({
            'status': 'approved',
            'admin_remarks': admin_remarks,
            'processed_at': 'now()'
        }).eq('id', withdrawal_id).execute()

        return True, "Withdrawal approved successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


def reject_withdrawal(withdrawal_id: str, admin_remarks: str = "") -> Tuple[bool, str]:
    try:
        withdrawal_result = supabase.table('withdrawal_requests').select('status').eq('id', withdrawal_id).execute()

        if not withdrawal_result.data:
            return False, "Withdrawal request not found"

        if withdrawal_result.data[0]['status'] != 'pending':
            return False, "Only pending requests can be rejected"

        supabase.table('withdrawal_requests').update({
            'status': 'rejected',
            'admin_remarks': admin_remarks,
            'processed_at': 'now()'
        }).eq('id', withdrawal_id).execute()

        return True, "Withdrawal rejected successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


def add_manual_credit(user_id: str, amount: float, description: str) -> Tuple[bool, str]:
    try:
        if amount <= 0:
            return False, "Amount must be greater than 0"

        result = supabase.table('wallet_transactions').insert({
            'user_id': user_id,
            'transaction_type': 'credit',
            'amount': amount,
            'description': description
        }).execute()

        if result.data:
            return True, f"Amount {amount} credited successfully"
        else:
            return False, "Failed to credit amount"

    except Exception as e:
        return False, f"Error: {str(e)}"
