import "server-only";
import { redirect } from "next/navigation";
import { createAuthClient } from "./supabase/server";

export type Brand = { id: string; email: string; name: string; avatar: string | null };

/** The signed-in brand, checked with the Supabase Auth server (not only the cookie). Null when signed out. */
export async function currentBrand(): Promise<Brand | null> {
  const supabase = await createAuthClient();
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) return null;
  const u = data.user;
  const meta = (u.user_metadata ?? {}) as Record<string, unknown>;
  const name = (meta.full_name as string) || (meta.name as string) || (u.email ?? "").split("@")[0];
  return { id: u.id, email: u.email ?? "", name, avatar: (meta.avatar_url as string) ?? null };
}

/** For pages: the signed-in brand, or a redirect to /login. */
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
