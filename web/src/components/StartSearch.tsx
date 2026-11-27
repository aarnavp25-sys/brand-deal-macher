"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

/** Creates the search row once, then opens its chat. */
export function StartSearch() {
  const router = useRouter();
  const started = useRef(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setError(null);
    const r = await fetch("/api/searches", { method: "POST" });
    const j = await r.json().catch(() => ({}));
    if (r.ok && j.id) router.replace(`/find/${j.id}`);
    else if (r.status === 401) router.replace("/login?next=/dashboard");
    else if (r.status === 409) router.replace("/dashboard");
    else setError(j.error ?? "Could not start a search. Please try again.");
  }

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto max-w-2xl">
      {error ? (
        <div className="card p-8">
          <p role="alert" className="text-accent-text">{error}</p>
          <button type="button" onClick={start} className="btn btn-primary mt-5 h-11 px-6">Try again</button>
        </div>
      ) : (
        <div className="grid gap-3" aria-busy="true" aria-label="Starting your chat">
          <div className="skeleton h-12 w-3/4 rounded-2xl" />
          <div className="skeleton h-12 w-1/2 rounded-2xl" />
        </div>
      )}
    </div>
  );
}
