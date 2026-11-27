import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

/** Pages that need a Google sign-in (user, 2026-11-27: "google se sign in ke baad hi kuch bhii search kar sakta hai").
 *  The home page stays public. */
const PROTECTED = ["/dashboard", "/find", "/results"];

/**
 * Runs before every page and API request:
 *  1. Blocks state-changing requests (POST/PUT/DELETE) that do not come from Kindred's own pages (CSRF).
 *  2. Refreshes the Supabase session cookies when the access token is about to expire.
 *  3. Sends visitors without a Google sign-in to /login (then back), and signed-in brands from /login to /find.
 *     An old anonymous session (before 2026-11-27) counts as signed out.
 * This is the quick check. Every API route and page checks the user again on the server before reading data.
 */
export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;

  if (request.method !== "GET" && request.method !== "HEAD") {
    const origin = request.headers.get("origin");
    if (!origin || origin !== request.nextUrl.origin) {
      return NextResponse.json({ error: "Request blocked: it did not come from this site." }, { status: 403 });
    }
  }

  let response = NextResponse.next({ request });
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(toSet, headers) {
          toSet.forEach(({ name, value }) => request.cookies.set(name, value));
          response = NextResponse.next({ request });
          toSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
          Object.entries(headers ?? {}).forEach(([k, v]) => response.headers.set(k, v));
        },
      },
    },
  );

  // Refreshes the session cookies if they are about to expire.
  const { data } = await supabase.auth.getClaims();
  const signedIn = Boolean(data?.claims?.sub) && data?.claims?.is_anonymous !== true;

  const redirectTo = (to: string) => {
    const r = NextResponse.redirect(new URL(to, request.url));
    response.cookies.getAll().forEach((c) => r.cookies.set(c));
    return r;
  };
  if (!signedIn && PROTECTED.some((p) => path === p || path.startsWith(p + "/"))) {
    return redirectTo(`/login?next=${encodeURIComponent(path)}`);
  }
  if (signedIn && path === "/login") return redirectTo("/find");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|icon.svg|.*\\.(?:png|jpg|jpeg|svg|ico|webp)$).*)"],
};
