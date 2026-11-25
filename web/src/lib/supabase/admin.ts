import "server-only";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Server-only Supabase client with the secret key. It bypasses RLS, so every caller must first check the
 * signed-in user (lib/auth.ts) and filter by that user's id. Never import this from a Client Component:
 * the `server-only` import above makes such a build fail.
 */
let client: SupabaseClient | null = null;

export function admin(): SupabaseClient {
  if (!client) {
    const key = process.env.SUPABASE_SECRET_KEY;
    if (!key) throw new Error("SUPABASE_SECRET_KEY is not set");
    client = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, key, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }
  return client;
}
