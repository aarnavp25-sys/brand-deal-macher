import "server-only";
import { redirect } from "next/navigation";
import { createAuthClient } from "./supabase/server";

/**
 * name = for the account menu (Google's name, else the email); chatName = the name the brand TYPED in the chat
 * (user_metadata.kindred_name). They are kept apart because Google fills `name` / `full_name` itself, and the user
 * wants the chat to ask the name anyway (2026-11-27: "Naam phir bhi poochho").
 */
export type Brand = { id: string; email: string; name: string; chatName: string; avatar: string | null };

/** The signed-in brand, checked with the Supabase Auth server (not only the cookie). Null when signed out or when the
 *  session is an old anonymous one (anonymous sessions were used until 2026-11-27). */
export async function currentBrand(): Promise<Brand | null> {
  const supabase = await createAuthClient();
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user || data.user.is_anonymous) return null;
  const u = data.user;
  const meta = (u.user_metadata ?? {}) as Record<string, unknown>;
  const name = (meta.full_name as string) || (meta.name as string) || (u.email ?? "").split("@")[0] || "";
  const chatName = typeof meta.kindred_name === "string" ? meta.kindred_name : "";
  return { id: u.id, email: u.email ?? "", name, chatName, avatar: ((meta.avatar_url ?? meta.picture) as string) ?? null };
}

/** For pages: the signed-in brand, or a redirect to Google sign-in that comes back to `next`. */
export async function requireBrand(next = "/dashboard"): Promise<Brand> {
  const brand = await currentBrand();
  if (!brand) redirect(`/login?next=${encodeURIComponent(next)}`);
  return brand;
}

/** Only same-site relative paths are allowed after sign-in (no open redirects). */
export function safeNext(raw: string | null | undefined, fallback = "/dashboard"): string {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//") || raw.startsWith("/\\")) return fallback;
  return raw;
}
