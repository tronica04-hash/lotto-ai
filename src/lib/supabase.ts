import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://jiulxmylgwaaygdytdfj.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

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
