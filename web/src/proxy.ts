import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

/**
 * Runs before every page and API request:
 *  1. Blocks state-changing requests (POST/PUT/DELETE) that do not come from Kindred's own pages (CSRF).
 *  2. Refreshes the Supabase session cookies when the access token is about to expire.
 *  3. Sends /login home: there is no sign-in screen for now (user, 2026-11-26: Google sign-in comes later).
 * The private anonymous session is created only when a visitor starts a chat (POST /api/searches, lib/api.ts), never
 * on a page view, so link prefetches, bots and landing-page visits create no accounts.
 * Every API route and page checks the user again on the server before reading data.
 */
export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;

  if (request.method !== "GET" && request.method !== "HEAD") {
    const origin = request.headers.get("origin");
    if (!origin || origin !== request.nextUrl.origin) {
      return NextResponse.json({ error: "Request blocked: it did not come from this site." }, { status: 403 });
    }
  }

  // The sign-in page is switched off for now.
  if (path === "/login") return NextResponse.redirect(new URL("/", request.url));

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

  // Refreshes the session cookies if they are about to expire. Sessions are created only when a chat starts.
  await supabase.auth.getClaims();
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|icon.svg|.*\\.(?:png|jpg|jpeg|svg|ico|webp)$).*)"],
};
