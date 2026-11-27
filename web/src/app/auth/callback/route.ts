import { NextResponse } from "next/server";
import { createAuthClient } from "@/lib/supabase/server";
import { safeNext } from "@/lib/auth";

/**
 * GET /auth/callback?code=...&next=...
 * Google sends the brand back here (through Supabase) after sign-in. The one-time code is exchanged for a
 * session, which Supabase stores in http cookies, then the brand goes on to the page it asked for.
 */
export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const next = safeNext(url.searchParams.get("next"));
  if (code) {
    const supabase = await createAuthClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) return NextResponse.redirect(new URL(next, url.origin));
  }
  return NextResponse.redirect(new URL("/login?error=signin", url.origin));
}
