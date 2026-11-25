import Link from "next/link";

/** Wordmark: "Kindred" in the wide cut of Archivo, with a small story-ring mark. */
export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-2.5" aria-label="Kindred home">
      <span className="story-ring inline-block size-7" aria-hidden>
        <span className="block size-full bg-accent" />
      </span>
      <span className="display text-xl font-extrabold">Kindred</span>
    </Link>
  );
}
