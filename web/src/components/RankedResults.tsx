"use client";
import { Avatar } from "@/components/Avatar";
import type { ResultsV5 } from "@/lib/rank";
import { compact, percent } from "@/lib/format";

const CREATOR: Record<string, string> = { female: "Female creator", male: "Male creator", couple: "Couple" };

/** Top 20 by the candidate score (lib/rank.ts). */
export function RankedResults({ results, photos }: { results: ResultsV5; photos: Record<string, string> }) {
  if (!results.top.length) {
    return (
      <div className="card mt-10 p-8">
        <p className="display text-2xl font-bold">Nobody fits this combo yet</p>
        <p className="mt-2 text-muted">Try more categories or any language. We add creators every week.</p>
      </div>
    );
  }
  return (
    <div className="mt-8">
      <p className="text-sm text-muted">
        {results.considered} creators match your picks
        {results.relevant < results.considered && results.relevant >= 5 ? `, and ${results.relevant} of them make content close to your product` : ""}.
        These are the top {results.top.length} by Kindred Score: how close their content is to your product, how well their audience matches
        your buyers, whether they show up on camera, and their engagement and reach.
      </p>
      <ol className="mt-6 grid gap-4 md:grid-cols-2">
        {results.top.map((c, i) => (
          <li key={c.username} className="card rise flex flex-col p-5 md:p-6" style={{ ["--i" as string]: Math.min(i, 8) }}>
            <div className="flex items-start gap-4">
              <span className="w-6 pt-1 text-sm font-semibold text-muted tabular-nums">{i + 1}</span>
              <Avatar src={photos[c.username]} name={c.username} size={56} />
              <div className="min-w-0 flex-1">
                <a
                  href={`https://www.instagram.com/${encodeURIComponent(c.username)}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block truncate text-lg font-semibold hover:text-accent-text"
                >
                  @{c.username}
                </a>
                <p className="mt-0.5 text-sm text-muted">{[CREATOR[c.creator_gender ?? ""], c.category].filter(Boolean).join(", ")}</p>
              </div>
              <div className="text-right">
                <p className="display text-3xl font-extrabold tabular-nums">{c.score}</p>
                <p className="text-xs text-muted">Kindred Score</p>
              </div>
            </div>

            {c.label && (
              <p className="mt-4 rounded-[12px] bg-surface-2 px-3 py-2 text-sm text-muted">{c.label}</p>
            )}
            {c.niche && <p className="mt-4 text-sm font-semibold capitalize">{c.niche}</p>}
            {c.about && <p className="mt-2 line-clamp-2 text-[15px] leading-relaxed text-muted">{c.about}</p>}
            {c.reasons.length > 0 && (
              <ul className="mt-3 grid gap-1 text-sm">
                {c.reasons.map((r) => (
                  <li key={r} className="flex gap-2">
                    <span className="text-accent-text" aria-hidden>
                      +
                    </span>
                    {r}
                  </li>
                ))}
              </ul>
            )}

            <dl className="mt-5 grid grid-cols-3 gap-3 border-t border-line pt-4">
              <Metric label="Followers" value={compact(c.followers)} />
              <Metric label="Typical views" value={compact(c.median_views)} />
              <Metric label={c.engagement_estimated ? "Engagement (est.)" : "Engagement"} value={percent(c.engagement_rate)} />
            </dl>
            <p className="mt-3 text-sm">
              <span className="text-muted">Speaks</span> {c.languages.length ? c.languages.join(", ") : "no talking, music only"}
            </p>
          </li>
        ))}
      </ol>
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
