"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

/**
 * Shown once, right after Google sign-in, until the brand tells Kindred what to call them (user, 2026-11-27:
 * "Sign in aane ke baad sirf 'What is your name?' poochega ... ek pop-up type"). It cannot be skipped: every chat
 * greets the brand by this name.
 */
export function NamePopup() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    input.current?.focus();
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    const r = await fetch("/api/profile/name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok) {
      router.refresh();
      return;
    }
    setBusy(false);
    if (r.status === 401) router.replace("/login?next=/dashboard");
    else setError(j.error ?? "That didn't save. Try again?");
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-5 backdrop-blur-sm">
      <form
        onSubmit={save}
        role="dialog"
        aria-modal="true"
        aria-labelledby="name-title"
        className="card name-pop w-full max-w-md p-7 md:p-8"
      >
        <h2 id="name-title" className="display text-2xl font-extrabold md:text-3xl">
          What is your name?
        </h2>
        <p className="mt-2 text-muted">So Kindred knows what to call you.</p>
        <input
          ref={input}
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={40}
          autoComplete="given-name"
          aria-label="Your name"
          placeholder="e.g. Priya"
          className="field mt-6 h-12 w-full px-4 text-base"
        />
        {error && (
          <p role="alert" className="mt-3 text-sm text-accent-text">
            {error}
          </p>
        )}
        <button type="submit" disabled={busy || !name.trim()} className="btn btn-primary mt-6 h-12 w-full text-base">
          {busy ? "Saving..." : "Continue"}
        </button>
      </form>
    </div>
  );
}
