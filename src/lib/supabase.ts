import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://jiulxmylgwaaygdytdfj.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppdWx4bXlsZ3dhYXlnZHl0ZGZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAzMDEzNjMsImV4cCI6MjA5NTg3NzM2M30.UZ7mndrVgOTiKDJRsOqRl57EsEG9q5B98c3j0JLuvns';

const createSafeClient = (url: string, key: string): SupabaseClient | null => {
  if (!url || !key) return null;
  try {
    return createClient(url, key);
  } catch {
    return null;
  }
};

export const supabase: SupabaseClient | null = createSafeClient(supabaseUrl, supabaseAnonKey);

const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
export const supabaseAdmin: SupabaseClient | null = supabaseServiceKey
  ? createSafeClient(supabaseUrl, supabaseServiceKey)
  : null;
