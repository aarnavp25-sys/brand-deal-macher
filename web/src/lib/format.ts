/** 32157 -> "32.2K", 980 -> "980". */
export function compact(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "-";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}K`;
  return String(Math.round(n));
}

/** 0.0318 -> "3.2%". */
export function percent(x: number | null | undefined): string {
  if (x == null || !Number.isFinite(x)) return "-";
  return `${(x * 100).toFixed(1).replace(/\.0$/, "")}%`;
}

export function dateShort(iso: string): string {
  return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}
