from typing import Tuple, List, Dict
from supabase_client import get_supabase_client

supabase = get_supabase_client()


def create_support_ticket(user_id: str, subject: str, message: str) -> Tuple[bool, str]:
    try:
        if not subject or not message:
            return False, "Subject and message are required"

        ticket_data = {
            'user_id': user_id,
            'subject': subject,
            'message': message,
            'status': 'open'
        }

        result = supabase.table('support_tickets').insert(ticket_data).execute()

        if result.data:
            return True, "Support ticket created successfully"
        else:
            return False, "Failed to create support ticket"

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_user_tickets(user_id: str) -> List[Dict]:
    try:
        tickets_result = supabase.table('support_tickets').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()

        return tickets_result.data if tickets_result.data else []

    except Exception as e:
        print(f"Error getting user tickets: {str(e)}")
        return []


def get_all_tickets() -> List[Dict]:
    try:
        tickets_result = supabase.table('support_tickets').select('*, users(name, user_id, email, phone)').order('created_at', desc=True).execute()

        return tickets_result.data if tickets_result.data else []

    except Exception as e:
        print(f"Error getting all tickets: {str(e)}")
        return []


def update_ticket_status(ticket_id: str, status: str, admin_response: str = "") -> Tuple[bool, str]:
    try:
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']

        if status not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

        update_data = {
            'status': status,
            'updated_at': 'now()'
        }

        if admin_response:
            update_data['admin_response'] = admin_response

        result = supabase.table('support_tickets').update(update_data).eq('id', ticket_id).execute()

        if result.data:
            return True, "Ticket updated successfully"
        else:
            return False, "Failed to update ticket"

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_ticket_stats() -> Dict:
    try:
        all_tickets = supabase.table('support_tickets').select('status').execute()

        stats = {
            'total': 0,
            'open': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0
        }

        if all_tickets.data:
            stats['total'] = len(all_tickets.data)

            for ticket in all_tickets.data:
                status = ticket['status']
                if status in stats:
                    stats[status] += 1

        return stats

    except Exception as e:
        print(f"Error getting ticket stats: {str(e)}")
        return {
            'total': 0,
            'open': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0
        }
