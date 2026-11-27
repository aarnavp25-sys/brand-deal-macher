import type { Metadata } from "next";
import Link from "next/link";
import { currentBrand } from "@/lib/auth";
import { listSearches } from "@/lib/searches";
import { dateShort } from "@/lib/format";
import { DeleteSearch } from "@/components/DeleteSearch";

export const metadata: Metadata = { title: "My searches" };

const STATUS: Record<string, string> = {
  chatting: "Chat not finished",
  ready: "Ready to search",
  searching: "Searching",
  done: "Done",
  failed: "Failed",
};

export default async function Dashboard() {
  const brand = await currentBrand();
  const searches = brand ? await listSearches(brand.id) : [];

  return (
    <div>
      <h1 className="display text-3xl font-extrabold md:text-4xl">Your searches</h1>
      <p className="mt-2 text-muted">
        {brand && (brand.chatName || brand.name) ? `Hi ${(brand.chatName || brand.name).split(/\s+/)[0]}! ` : ""}
        Saved to your Google account. Nobody else can see them.
      </p>

      {searches.length === 0 ? (
        <div className="card mt-10 flex flex-col items-start gap-5 p-8 md:p-10">
          <p className="display text-2xl font-bold">No searches yet</p>
          <p className="max-w-[50ch] leading-relaxed text-muted">
            Five quick questions about your brand, then you see the creators that fit.
          </p>
          <Link href="/find" className="btn btn-primary h-11 px-6">
            Find creators
          </Link>
        </div>
      ) : (
        <ul className="mt-10 grid gap-3">
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
