import { NextResponse } from "next/server";
import { createAuthClient } from "@/lib/supabase/server";

/** POST /auth/signout: ends the session (cookies cleared) and returns to the home page. */
export async function POST(request: Request) {
  const supabase = await createAuthClient();
  await supabase.auth.signOut();
  return NextResponse.redirect(new URL("/", request.url), { status: 303 });
}
