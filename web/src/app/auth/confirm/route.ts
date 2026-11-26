import { NextResponse } from "next/server";
import type { EmailOtpType } from "@supabase/supabase-js";
import { createAuthClient } from "@/lib/supabase/server";
import { safeNext } from "@/lib/auth";

const TYPES: EmailOtpType[] = ["magiclink", "email", "signup", "invite", "recovery", "email_change"];

/**
 * GET /auth/confirm?token_hash=...&type=magiclink&next=...
 * Standard Supabase email-link sign-in. Only a token issued by Supabase itself (in an email, or by the project
 * owner with the admin API for testing) can pass verifyOtp, so this is not a way around Google sign-in.
 */
export async function GET(request: Request) {
  const url = new URL(request.url);
  const tokenHash = url.searchParams.get("token_hash");
  const type = url.searchParams.get("type") as EmailOtpType | null;
  const next = safeNext(url.searchParams.get("next"));
  if (tokenHash && type && TYPES.includes(type)) {
    const supabase = await createAuthClient();
    const { error } = await supabase.auth.verifyOtp({ type, token_hash: tokenHash });
    if (!error) return NextResponse.redirect(new URL(next, url.origin));
  }
  return NextResponse.redirect(new URL("/", url.origin));
}
