import type { Metadata } from "next";
import { Logo } from "@/components/Logo";
import { GoogleButton } from "@/components/GoogleButton";
import { safeNext } from "@/lib/auth";

export const metadata: Metadata = { title: "Sign in" };

const ERRORS: Record<string, string> = {
  signin: "Google sign-in did not finish. Please try again.",
  link: "That sign-in link has expired or was already used. Please sign in again.",
};

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const sp = await searchParams;
  const next = safeNext(typeof sp.next === "string" ? sp.next : null, "/find");
  const error = typeof sp.error === "string" ? ERRORS[sp.error] : undefined;

  return (
    <div className="grid min-h-[100dvh] md:grid-cols-[1fr_1.1fr]">
      <div className="flex flex-col px-6 py-6 md:px-12">
        <Logo />
        <div className="my-auto w-full max-w-sm py-16">
          <h1 className="display text-3xl font-extrabold md:text-4xl">Sign in to find creators</h1>
          <p className="mt-3 leading-relaxed text-muted">
            Use your Google account. Your searches stay private to you.
          </p>
          <div className="mt-8">
            <GoogleButton next={next} />
          </div>
          {error && (
            <p role="alert" className="mt-4 rounded-[12px] border border-line bg-surface p-3 text-sm text-accent-text">
              {error}
            </p>
          )}
          <p className="mt-8 text-sm leading-relaxed text-muted">
            We only read your name, email and profile photo from Google. We never post anything.
          </p>
        </div>
      </div>
      <aside
        className="relative hidden overflow-hidden md:block"
        style={{ background: "conic-gradient(from 210deg at 70% 40%, var(--ring-a), var(--ring-b), var(--ring-c), var(--ring-a))" }}
        aria-hidden
      >
        <div className="absolute inset-0 flex items-end p-12">
          <p className="display max-w-[16ch] text-4xl font-extrabold text-[#141417] lg:text-5xl">
            Small brands, the right small creators.
          </p>
        </div>
      </aside>
    </div>
  );
}
