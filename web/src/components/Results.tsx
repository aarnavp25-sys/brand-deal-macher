"use client";
import { useMemo, useState } from "react";
import { Avatar } from "@/components/Avatar";
import { CreatorStats } from "@/components/CreatorStats";
import type { Creator } from "@/lib/matching";

const SORTS = {
  followers: { label: "Followers", key: (c: Creator) => c.followers },
  views: { label: "Typical reel views", key: (c: Creator) => c.median_views ?? -1 },
  engagement: { label: "Engagement", key: (c: Creator) => c.engagement_rate ?? -1 },
  posting: { label: "Posts most often", key: (c: Creator) => c.reels_per_week ?? -1 },
} as const;
type SortId = keyof typeof SORTS;

const CREATOR: Record<string, string> = { female: "Female creator", male: "Male creator", couple: "Couple" };

export function Results({ creators, photos }: { creators: Creator[]; photos: Record<string, string> }) {
  const [sort, setSort] = useState<SortId>("followers");
  const [cat, setCat] = useState<string>("all");
  const cats = useMemo(() => {
    const m = new Map<string, number>();
    creators.forEach((c) => c.category && m.set(c.category, (m.get(c.category) ?? 0) + 1));
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  }, [creators]);
  const list = useMemo(
    () =>
      creators
        .filter((c) => cat === "all" || c.category === cat)
        .sort((a, b) => SORTS[sort].key(b) - SORTS[sort].key(a)),
    [creators, sort, cat],
  );

  if (!creators.length) {
    return (
      <div className="card mt-10 p-8">
        <p className="display text-2xl font-bold">No creators match yet</p>
        <p className="mt-2 text-muted">We add creators every week. Try more categories or any language for now.</p>
      </div>
    );
  }

  return (
    <div className="mt-8">
      {cats.length > 1 && (
        <div className="mb-4 flex flex-wrap gap-2" role="group" aria-label="Show category">
          <button type="button" aria-pressed={cat === "all"} onClick={() => setCat("all")} className="chip">
            All <span className="ml-1 opacity-70">{creators.length}</span>
          </button>
          {cats.map(([c, n]) => (
            <button key={c} type="button" aria-pressed={cat === c} onClick={() => setCat(c)} className="chip">
              {c} <span className="ml-1 opacity-70">{n}</span>
            </button>
          ))}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Sort creators">
        <span className="mr-1 text-sm text-muted">Sort by</span>
        {(Object.keys(SORTS) as SortId[]).map((id) => (
          <button key={id} type="button" aria-pressed={sort === id} onClick={() => setSort(id)} className="chip">
            {SORTS[id].label}
          </button>
        ))}
      </div>

      <ul className="mt-6 grid gap-4 md:grid-cols-2">
        {list.map((c, i) => (
          <li key={c.username} className="card rise flex flex-col p-5 md:p-6" style={{ ["--i" as string]: Math.min(i, 8) }}>
            <div className="flex items-start gap-4">
              <Avatar src={photos[c.username]} name={c.username} size={60} />
              <div className="min-w-0 flex-1">
                <a
                  href={`https://www.instagram.com/${encodeURIComponent(c.username)}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block truncate text-lg font-semibold hover:text-accent-text"
                >
                  @{c.username}
                </a>
                <p className="mt-0.5 text-sm text-muted">
                  {[CREATOR[c.creator_gender ?? ""], c.category, c.secondary_category ? `also ${c.secondary_category.toLowerCase()}` : null]
                    .filter(Boolean)
                    .join(", ")}
                </p>
              </div>
            </div>

            {c.niche && <p className="mt-4 text-sm font-semibold capitalize">{c.niche}</p>}
            {c.about && <p className="mt-2 line-clamp-3 text-[15px] leading-relaxed text-muted">{c.about}</p>}

            <CreatorStats c={c} />
          </li>
        ))}
      </ul>
    </div>
  );
}
