/*
  # MLM Portal Database Schema

  1. New Tables
    - `users`
      - `id` (uuid, primary key)
      - `name` (text)
      - `email` (text, unique)
      - `phone` (text, unique)
      - `password_hash` (text) - bcrypt hashed password
      - `user_id` (text, unique) - display ID like UQM001
      - `package` (text) - Free, Starter, Growth, Pro
      - `status` (text) - Active, Inactive
      - `sponsor_id` (uuid, foreign key)
      - `referral_code` (text, unique)
      - `is_active` (boolean)
      - `created_at` (timestamptz)
      - Bank details: bank_name, account_number, ifsc_code, account_holder_name
    
    - `wallets`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key, unique)
      - `balance` (numeric)
      - `total_earned` (numeric)
      - `updated_at` (timestamptz)
    
    - `wallet_transactions`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `transaction_type` (text) - credit, debit, direct_income, level_income, royalty, withdrawal
      - `amount` (numeric)
      - `description` (text)
      - `reference_id` (uuid) - reference to related record
      - `created_at` (timestamptz)
    
    - `activation_pins`
      - `id` (uuid, primary key)
      - `pin_code` (text, unique)
      - `package` (text)
      - `generated_for_user_id` (uuid, foreign key)
      - `used_by_user_id` (uuid, foreign key)
      - `is_used` (boolean)
      - `created_at` (timestamptz)
      - `used_at` (timestamptz)
    
    - `team_members`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `sponsor_id` (uuid, foreign key)
      - `level` (integer) - depth in the tree
      - `is_direct` (boolean)
      - `created_at` (timestamptz)
    
    - `withdrawal_requests`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `amount` (numeric)
      - `status` (text) - pending, approved, rejected
      - `bank_account` (text)
      - `ifsc_code` (text)
      - `account_holder_name` (text)
      - `admin_remarks` (text)
      - `requested_at` (timestamptz)
      - `processed_at` (timestamptz)
    
    - `support_tickets`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `subject` (text)
      - `message` (text)
      - `status` (text) - open, in_progress, resolved, closed
      - `admin_response` (text)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)
    
    - `income_records`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `from_user_id` (uuid, foreign key) - who generated this income
      - `income_type` (text) - direct, level_1, level_2, level_3, royalty
      - `amount` (numeric)
      - `package` (text)
      - `created_at` (timestamptz)

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users to access their own data
    - Add policies for admin access
*/

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  email text UNIQUE NOT NULL,
  phone text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  user_id text UNIQUE NOT NULL,
  package text DEFAULT 'Free',
  status text DEFAULT 'Inactive',
  sponsor_id uuid REFERENCES users(id),
  referral_code text UNIQUE NOT NULL,
  is_active boolean DEFAULT false,
  bank_name text,
  account_number text,
  ifsc_code text,
  account_holder_name text,
  direct_referrals integer DEFAULT 0,
  active_direct_referrals integer DEFAULT 0,
  total_team integer DEFAULT 0,
  active_team integer DEFAULT 0,
  royalty_eligible boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Wallets table
CREATE TABLE IF NOT EXISTS wallets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  balance numeric DEFAULT 0,
  total_earned numeric DEFAULT 0,
  updated_at timestamptz DEFAULT now()
);

-- Wallet transactions table
CREATE TABLE IF NOT EXISTS wallet_transactions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  transaction_type text NOT NULL,
  amount numeric NOT NULL,
  description text,
  reference_id uuid,
  created_at timestamptz DEFAULT now()
);

-- Activation pins table
CREATE TABLE IF NOT EXISTS activation_pins (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pin_code text UNIQUE NOT NULL,
  package text NOT NULL,
  generated_for_user_id uuid REFERENCES users(id),
  used_by_user_id uuid REFERENCES users(id),
  is_used boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  used_at timestamptz
);

-- Team members table (for hierarchy tracking)
CREATE TABLE IF NOT EXISTS team_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  sponsor_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  level integer NOT NULL,
  is_direct boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  UNIQUE(user_id, sponsor_id)
);

-- Withdrawal requests table
CREATE TABLE IF NOT EXISTS withdrawal_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount numeric NOT NULL,
  status text DEFAULT 'pending',
  bank_account text,
  ifsc_code text,
  account_holder_name text,
  admin_remarks text,
  requested_at timestamptz DEFAULT now(),
  processed_at timestamptz
);

-- Support tickets table
CREATE TABLE IF NOT EXISTS support_tickets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject text NOT NULL,
  message text NOT NULL,
  status text DEFAULT 'open',
  admin_response text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Income records table
CREATE TABLE IF NOT EXISTS income_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  from_user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  income_type text NOT NULL,
  amount numeric NOT NULL,
  package text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_sponsor ON users(sponsor_id);
CREATE INDEX IF NOT EXISTS idx_users_referral ON users(referral_code);
CREATE INDEX IF NOT EXISTS idx_wallets_user ON wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON wallet_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created ON wallet_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pins_code ON activation_pins(pin_code);
CREATE INDEX IF NOT EXISTS idx_team_user ON team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_team_sponsor ON team_members(sponsor_id);
CREATE INDEX IF NOT EXISTS idx_withdrawals_user ON withdrawal_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON withdrawal_requests(status);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_income_user ON income_records(user_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE activation_pins ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawal_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE income_records ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- RLS Policies for wallets table
CREATE POLICY "Users can view own wallet"
  ON wallets FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for wallet_transactions table
CREATE POLICY "Users can view own transactions"
  ON wallet_transactions FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for activation_pins table
CREATE POLICY "Users can view pins generated for them"
  ON activation_pins FOR SELECT
  TO authenticated
  USING (auth.uid() = generated_for_user_id);

-- RLS Policies for team_members table
CREATE POLICY "Users can view their own team"
  ON team_members FOR SELECT
  TO authenticated
  USING (auth.uid() = sponsor_id);

-- RLS Policies for withdrawal_requests table
CREATE POLICY "Users can view own withdrawal requests"
  ON withdrawal_requests FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own withdrawal requests"
  ON withdrawal_requests FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for support_tickets table
CREATE POLICY "Users can view own support tickets"
  ON support_tickets FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own support tickets"
  ON support_tickets FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for income_records table
CREATE POLICY "Users can view own income records"
  ON income_records FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- Create function to auto-generate user_id
CREATE OR REPLACE FUNCTION generate_user_id()
RETURNS text AS $$
DECLARE
  next_num integer;
  new_id text;
BEGIN
  SELECT COUNT(*) + 1 INTO next_num FROM users;
  new_id := 'UQM' || LPAD(next_num::text, 3, '0');
  RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate referral code
CREATE OR REPLACE FUNCTION generate_referral_code()
RETURNS text AS $$
BEGIN
  RETURN UPPER(substring(md5(random()::text) from 1 for 8));
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-create wallet for new users
CREATE OR REPLACE FUNCTION create_wallet_for_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO wallets (user_id, balance, total_earned)
  VALUES (NEW.id, 0, 0);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_wallet
  AFTER INSERT ON users
  FOR EACH ROW
  EXECUTE FUNCTION create_wallet_for_user();

-- Create function to update wallet balance
CREATE OR REPLACE FUNCTION update_wallet_balance()
RETURNS trigger AS $$
BEGIN
  IF NEW.transaction_type IN ('credit', 'direct_income', 'level_income', 'royalty') THEN
    UPDATE wallets
    SET balance = balance + NEW.amount,
        total_earned = total_earned + NEW.amount,
        updated_at = now()
    WHERE user_id = NEW.user_id;
  ELSIF NEW.transaction_type IN ('debit', 'withdrawal') THEN
    UPDATE wallets
    SET balance = balance - NEW.amount,
        updated_at = now()
    WHERE user_id = NEW.user_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_wallet
  AFTER INSERT ON wallet_transactions
  FOR EACH ROW
  EXECUTE FUNCTION update_wallet_balance();