import type { Metadata } from "next";
import Link from "next/link";
import { currentBrand } from "@/lib/auth";
import { listSearches } from "@/lib/searches";
import { dateShort } from "@/lib/format";
import { DeleteSearch } from "@/components/DeleteSearch";

export const metadata: Metadata = { title: "Dashboard" };

const STATUS: Record<string, string> = {
  chatting: "Chat not finished",
  ready: "Ready to search",
  searching: "Searching",
  done: "Done",
  failed: "Failed",
};

/**
 * The brand's home after Google sign-in (user, 2026-11-27: "Sign in ke baad ek user dashboard type bana de"):
 * a greeting, one way to start a new search, a few numbers about their searches, and every saved search.
 * A new chat opens only when the brand asks for it here; signing in never drops them into a chat.
 */
export default async function Dashboard() {
  const brand = await currentBrand();
  const searches = brand ? await listSearches(brand.id) : [];
  const first = (brand?.chatName || "").split(/\s+/)[0];
  const done = searches.filter((s) => s.status === "done");
  const creators = done.reduce((a, s) => a + (s.count ?? 0), 0);
  const open = searches.length - done.length;

  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-accent-text">Dashboard</p>
      <h1 className="display mt-2 text-4xl font-extrabold md:text-5xl">{first ? `Hi ${first}!` : "Welcome to Kindred"}</h1>
      <p className="mt-3 max-w-[60ch] text-lg leading-relaxed text-muted">
        Find Instagram creators who can actually sell your product.
      </p>

      <section className="card mt-8 flex flex-col gap-5 bg-accent-soft p-7 md:flex-row md:items-center md:justify-between md:p-9">
        <div>
          <h2 className="display text-2xl font-bold md:text-3xl">Start a new search</h2>
          <p className="mt-2 max-w-[52ch] leading-relaxed text-muted">
            Five quick questions about your brand and product. Kindred checks creators&rsquo; real reels and shows who fits, with the reason.
          </p>
        </div>
        <Link href="/find" className="btn btn-primary h-12 shrink-0 px-7 text-base">
          Find creators
        </Link>
      </section>

      {searches.length > 0 && (
        <dl className="mt-6 grid grid-cols-3 gap-3">
          <Stat label="Searches done" value={done.length} />
          <Stat label="Creators found" value={creators} />
          <Stat label="Chats not finished" value={open} />
        </dl>
      )}

      <h2 className="display mt-12 text-2xl font-bold">Your searches</h2>
      <p className="mt-1 text-sm text-muted">Saved to your Google account. Nobody else can see them.</p>

      {searches.length === 0 ? (
        <div className="card mt-5 p-7">
          <p className="font-semibold">No searches yet</p>
          <p className="mt-1 text-muted">Your first search will show up here, so you can open its creators again any time.</p>
        </div>
      ) : (
        <ul className="mt-5 grid gap-3">
          {searches.map((s) => {
            const href = s.status === "done" ? `/results/${s.id}` : `/find/${s.id}`;
            return (
              <li key={s.id} className="card flex items-center gap-4 p-5">
                <Link href={href} className="min-w-0 flex-1">
                  <p className="truncate text-lg font-semibold">{s.title || "Untitled search"}</p>
                  <p className="mt-1 text-sm text-muted">
                    {[s.categories, STATUS[s.status], s.count != null ? `${s.count} creators` : null, dateShort(s.created_at)]
                      .filter(Boolean)
                      .join("  /  ")}
                  </p>
                </Link>
                <Link href={href} className="btn btn-ghost hidden h-9 px-4 text-sm sm:inline-flex">
                  {s.status === "done" ? "View creators" : "Continue"}
                </Link>
                <DeleteSearch id={s.id} />
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="card p-5">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="display mt-1 text-3xl font-extrabold tabular-nums">{value}</dd>
    </div>
  );
}
