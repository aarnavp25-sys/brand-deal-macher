"use client";
import { useMemo, useState } from "react";
import { Avatar } from "@/components/Avatar";
import type { Creator } from "@/lib/matching";
import { compact, percent } from "@/lib/format";

const SORTS = {
  followers: { label: "Followers", key: (c: Creator) => c.followers },
  views: { label: "Typical reel views", key: (c: Creator) => c.median_views ?? -1 },
  engagement: { label: "Engagement", key: (c: Creator) => c.engagement_rate ?? -1 },
  posting: { label: "Posts most often", key: (c: Creator) => c.reels_per_week ?? -1 },
} as const;
type SortId = keyof typeof SORTS;

const GENDER: Record<string, string> = { women: "Mostly women", men: "Mostly men", unisex: "Men and women" };
const CREATOR: Record<string, string> = { female: "Female creator", male: "Male creator", couple: "Couple" };

export function Results({ creators, photos }: { creators: Creator[]; photos: Record<string, string> }) {
  const [sort, setSort] = useState<SortId>("followers");
  const list = useMemo(() => [...creators].sort((a, b) => SORTS[sort].key(b) - SORTS[sort].key(a)), [creators, sort]);

  if (!creators.length) {
    return (
      <div className="card mt-10 p-8">
        <p className="display text-2xl font-bold">No creators in this category yet</p>
        <p className="mt-2 text-muted">We are adding creators every week. Try a nearby category for now.</p>
      </div>
    );
  }

  return (
    <div className="mt-8">
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
                  {[CREATOR[c.creator_gender ?? ""], c.secondary_category ? `also ${c.secondary_category.toLowerCase()}` : null]
                    .filter(Boolean)
                    .join(", ")}
                </p>
              </div>
            </div>

            {c.niche && <p className="mt-4 text-sm font-semibold capitalize">{c.niche}</p>}
            {c.about && <p className="mt-2 line-clamp-3 text-[15px] leading-relaxed text-muted">{c.about}</p>}

            <dl className="mt-5 grid grid-cols-3 gap-3 border-t border-line pt-4">
              <Metric label="Followers" value={compact(c.followers)} />
              <Metric label="Typical views" value={compact(c.median_views)} />
              <Metric
                label={c.engagement_estimated ? "Engagement (est.)" : "Engagement"}
                value={percent(c.engagement_rate)}
              />
            </dl>

            <div className="mt-4 flex flex-wrap gap-x-5 gap-y-1.5 text-sm">
              {c.languages.length > 0 && <span><span className="text-muted">Speaks</span> {c.languages.join(", ")}</span>}
              {c.audience_gender && (
                <span>
                  <span className="text-muted">Audience (est.)</span> {GENDER[c.audience_gender] ?? c.audience_gender}
                  {c.audience_age && c.audience_age !== "mixed" ? `, ${c.audience_age}` : ""}
                </span>
              )}
              {c.reels_per_week != null && <span><span className="text-muted">Posts</span> {c.reels_per_week.toFixed(1)} reels a week</span>}
            </div>

            <p className="mt-4 text-sm">
              {c.brand_collabs === "yes" ? (
                <span>
                  <span className="font-semibold text-ok">Has done brand collabs</span>
                  {c.collab_brands.length > 0 && <span className="text-muted"> with {c.collab_brands.slice(0, 3).join(", ")}</span>}
                </span>
              ) : c.brand_collabs === "maybe" ? (
                <span className="text-muted">Some reels may be brand work</span>
              ) : (
                <span className="text-muted">No brand collabs seen yet</span>
              )}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="display mt-1 text-xl font-bold tabular-nums">{value}</dd>
    </div>
  );
}
