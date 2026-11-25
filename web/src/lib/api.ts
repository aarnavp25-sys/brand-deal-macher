import "server-only";
import { NextResponse } from "next/server";
import { currentBrand, type Brand } from "@/lib/auth";
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

/** Wraps an API handler: 401 without a login, clean JSON errors, no internal details leaked. */
export async function handle(fn: (brand: Brand) => Promise<unknown>): Promise<NextResponse> {
  try {
    const brand = await currentBrand();
    if (!brand) return NextResponse.json({ error: "Please sign in again." }, { status: 401 });
    const out = await fn(brand);
    return NextResponse.json(out ?? { ok: true }, { headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    if (e instanceof UserError) return NextResponse.json({ error: e.message }, { status: e.status });
    console.error(e);
    return NextResponse.json({ error: "Something went wrong on our side. Please try again." }, { status: 500 });
  }
}
