import "server-only";
import { NextResponse } from "next/server";
import { currentBrand, type Brand } from "@/lib/auth";
import { createAuthClient } from "@/lib/supabase/server";
import { UserError } from "@/lib/searches";

const MAX_BODY = 8_000; // bytes; the longest answer is 1,500 characters

/** Reads a small JSON body. Anything else is a 400. */
export async function jsonBody(req: Request): Promise<Record<string, unknown>> {
  const text = await req.text();
  if (text.length > MAX_BODY) throw new UserError("Request too large.", 413);
  if (!text) return {};
  try {
    const v = JSON.parse(text);
    if (v && typeof v === "object" && !Array.isArray(v)) return v as Record<string, unknown>;
  } catch {}
  throw new UserError("Bad request.");
}

/**
 * Wraps an API handler: clean JSON errors, no internal details leaked. Without a session it answers 401, except
 * where `startSession` is set (starting a chat): there it creates the visitor's private anonymous session first.
 */
export async function handle(fn: (brand: Brand) => Promise<unknown>, startSession = false): Promise<NextResponse> {
  try {
    let brand = await currentBrand();
    if (!brand && startSession) {
      const supabase = await createAuthClient();
      const { data, error } = await supabase.auth.signInAnonymously();
      if (error || !data.user) {
        return NextResponse.json(
          { error: "Lots of people are using Kindred from your network right now. Try again in a few minutes." },
          { status: 429 },
        );
      }
      brand = { id: data.user.id, email: "", name: "", avatar: null };
    }
    if (!brand) return NextResponse.json({ error: "Your session ended. Refresh the page to keep going." }, { status: 401 });
    const out = await fn(brand);
    return NextResponse.json(out ?? { ok: true }, { headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    if (e instanceof UserError) return NextResponse.json({ error: e.message }, { status: e.status });
    console.error(e);
    return NextResponse.json({ error: "Something went wrong on our side. Please try again." }, { status: 500 });
  }
}
