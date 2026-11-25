"use client";

export default function AppError({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="card mx-auto max-w-xl p-8">
      <h1 className="display text-2xl font-bold">Something went wrong</h1>
      <p className="mt-2 text-muted">We could not load this page. Please try again.</p>
      <button type="button" onClick={reset} className="btn btn-primary mt-6 h-11 px-6">Try again</button>
    </div>
  );
}
