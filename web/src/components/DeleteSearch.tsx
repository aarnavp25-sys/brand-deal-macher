"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function DeleteSearch({ id }: { id: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  async function remove() {
    if (!confirm("Delete this search?")) return;
    setBusy(true);
    const r = await fetch(`/api/searches/${id}`, { method: "DELETE" });
    setBusy(false);
    if (r.ok) router.refresh();
    else alert("Could not delete. Please try again.");
  }
  return (
    <button type="button" onClick={remove} disabled={busy} className="btn h-9 px-3 text-sm text-muted hover:text-ink" aria-label="Delete search">
      Delete
    </button>
  );
}
