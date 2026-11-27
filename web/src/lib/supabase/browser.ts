"use client";
import { createBrowserClient } from "@supabase/ssr";

/** Browser client (publishable key). Used only to start Google sign-in; it reads no data. */
export function browserClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
  );
}
