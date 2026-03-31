# UniQueMarketing MLM Portal

A complete Multi-Level Marketing portal built with Streamlit and Supabase.

## Features

### User Features
- User registration with referral system
- Account activation via E-PIN
- Package system (Free, Starter, Growth, Pro)
- Wallet management with transaction history
- Income tracking (Direct, Level 1-3, Royalty)
- Team hierarchy visualization
- E-PIN transfer functionality
- Withdrawal request system
- Support ticket system
- Profile management with bank details

### Admin Features
- Dashboard with portal statistics
- User management
- E-PIN generation and management
- Withdrawal request approval/rejection
- Support ticket management
- Income distribution tracking

### MLM Business Logic
- Direct income on referrals
- Multi-level income distribution (up to 3 levels based on package)
- Royalty eligibility system (requires 2+ active direct referrals)
- Package-based commission structure
- Team hierarchy tracking

## Security Features
- Password hashing with bcrypt
- Row Level Security (RLS) in Supabase
- Input validation for email, phone, and passwords
- Secure session management
- Protected admin routes

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Supabase account
- pip package manager

### Installation

1. Clone the repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Supabase credentials:
     ```
     VITE_SUPABASE_URL=your_supabase_url
     VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

4. The database schema is automatically created via Supabase migration.

### Running the Application

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

**Important:** Change these credentials in production by modifying the `admin_service.py` file.

## Package Structure

- `main.py` - Main Streamlit application
- `auth_service.py` - Authentication and user management
- `mlm_service.py` - MLM business logic and income distribution
- `wallet_service.py` - Wallet and transaction management
- `support_service.py` - Support ticket system
- `admin_service.py` - Admin functionality
- `supabase_client.py` - Supabase connection handler

## Database Schema

The application uses the following main tables:
- `users` - User accounts and profile information
- `wallets` - Wallet balances and earnings
- `wallet_transactions` - Transaction history
- `activation_pins` - E-PIN management
- `team_members` - Team hierarchy
- `withdrawal_requests` - Withdrawal processing
- `support_tickets` - Support system
- `income_records` - Income tracking

## Package Rules

### Free Package
- Price: Free
- E-PINs: 0
- Direct Income: 0
- Referral Limit: 2
- Withdrawal: No

### Starter Package
- Price: ₹99
- E-PINs: 1
- Direct Income: ₹30
- Referral Limit: Unlimited
- Withdrawal: Yes

### Growth Package
- Price: ₹299
- E-PINs: 3
- Direct Income: ₹90
- Level 1 Income: ₹10
- Referral Limit: Unlimited
- Withdrawal: Yes

### Pro Package
- Price: ₹599
- E-PINs: 7
- Direct Income: ₹180
- Level 1 Income: ₹10
- Level 2 Income: ₹5
- Level 3 Income: ₹3
- Referral Limit: Unlimited
- Withdrawal: Yes

## User Workflow

1. Register with optional sponsor referral code
2. Contact admin for activation PIN
3. Login and activate account with PIN
4. Start referring users to earn commissions
5. Build team and earn level income
6. Request withdrawals (minimum ₹100)
7. Track income and team in dashboard

## Admin Workflow

1. Login to admin dashboard
2. Generate activation PINs for different packages
3. Provide PINs to users for activation
4. Monitor user registrations and activations
5. Approve/reject withdrawal requests
6. Manage support tickets
7. View portal statistics and income distribution

## Support

For support, users can create tickets through the Support section in their dashboard.

## License

This project is for educational and business purposes.