import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

export const isSupabaseConfigured =
  supabaseUrl.length > 0 && supabaseAnonKey.length > 0;

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

/** Lista opcional de correos permitidos (máx. 4), separados por coma en .env */
export function getAllowedEmails(): string[] | null {
  const raw = process.env.EXPO_PUBLIC_ALLOWED_EMAILS?.trim();
  if (!raw) return null;
  const emails = raw
    .split(',')
    .map((e: string) => e.trim().toLowerCase())
    .filter(Boolean);
  return emails.length > 0 ? emails : null;
}

export const FAMILY_USER_SLOTS = Number(
  process.env.EXPO_PUBLIC_FAMILY_USER_SLOTS ?? '4'
);
