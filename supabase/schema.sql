-- LottoAI Database Schema
-- Run this in Supabase SQL Editor

-- Table: lotto_results (หวยรัฐบาลไทย)
CREATE TABLE IF NOT EXISTS lotto_results (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  draw_date DATE NOT NULL,
  draw_number TEXT,
  first_prize TEXT,
  second_prize JSONB DEFAULT '[]',
  third_prize JSONB DEFAULT '[]',
  two_digit TEXT,
  three_digit_first JSONB DEFAULT '[]',
  three_digit_last JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(draw_date)
);

-- Index สำหรับค้นหาตามวันที่
CREATE INDEX IF NOT EXISTS idx_lotto_draw_date ON lotto_results(draw_date DESC);
CREATE INDEX IF NOT EXISTS idx_lotto_draw_number ON lotto_results(draw_number);

-- Table: user_profiles
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'premium', 'vip')),
  queries_today INTEGER DEFAULT 0,
  queries_limit INTEGER DEFAULT 5,
  last_query_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: query_logs (บันทึกการใช้งาน)
CREATE TABLE IF NOT EXISTS query_logs (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  query_type TEXT NOT NULL,
  input_data JSONB,
  result_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: payments (ระบบเงิน)
CREATE TABLE IF NOT EXISTS payments (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  plan TEXT NOT NULL,
  amount INTEGER NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
  payment_method TEXT,
  payment_ref TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Function: reset daily query count
CREATE OR REPLACE FUNCTION reset_daily_queries()
RETURNS void AS $$
BEGIN
  UPDATE user_profiles
  SET queries_today = 0, last_query_date = CURRENT_DATE
  WHERE last_query_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Trigger: auto-create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, plan, queries_limit)
  VALUES (
    new.id,
    new.email,
    CASE
      WHEN new.email LIKE '%@test.com' THEN 'premium'
      ELSE 'free'
    END,
    CASE
      WHEN new.email LIKE '%@test.com' THEN 9999
      ELSE 5
    END
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger ถ้ามีอยู่แล้ว
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own query logs" ON query_logs
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own query logs" ON query_logs
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own payments" ON payments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own payments" ON payments
  FOR SELECT USING (auth.uid() = id);

-- lotto_results อ่านได้ทุกคน (public)
CREATE POLICY "Anyone can view lotto results" ON lotto_results
  FOR SELECT USING (true);

-- อนุญาตให้ service role insert/update lotto_results
CREATE POLICY "Service role can manage lotto results" ON lotto_results
  FOR ALL USING (true);
