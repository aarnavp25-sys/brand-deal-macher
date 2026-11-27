"use client";
import { Avatar } from "@/components/Avatar";
import { CreatorStats } from "@/components/CreatorStats";
import type { GroupId, Match, ResultsV4 } from "@/lib/review";

const CREATOR: Record<string, string> = { female: "Female creator", male: "Male creator", couple: "Couple" };

function groupTitle(id: GroupId, r: ResultsV4): { title: string; sub: string } {
  if (id === "specialists") return { title: "Already showing products like yours", sub: `Your kind of product is on camera in two or more of their last 12 reels.` };
  if (id === "category") {
    const cats = [r.product.category, ...r.product.close_categories].join(", ");
    return { title: `${cats} creators`, sub: "Their regular content is where your product belongs." };
  }
  return { title: "Lifestyle and more", sub: "Everyday creators with a natural spot for your product in what they already film." };
}

export function MatchResults({ results, photos }: { results: ResultsV4; photos: Record<string, string> }) {
  const total = Object.values(results.groups).reduce((a, g) => a + g.length, 0);
  const order: GroupId[] = ["specialists", "category", "lifestyle"];

  return (
    <div className="mt-8 grid gap-12">
      <p className="text-sm text-muted">
        We checked {results.checked} creators against their last 12 reels for your {results.product.product_type}
        {results.product.made_for !== "everyone" ? ` (made for ${results.product.made_for})` : ""}.{" "}
        {results.hidden_weak > 0 && `${results.hidden_weak} had no natural spot for it and are hidden. `}
        Kindred Score mixes how well they can sell it with their engagement and reach.
      </p>
      {total === 0 && (
        <div className="card p-8">
          <p className="display text-2xl font-bold">No creator fits well yet</p>
          <p className="mt-2 text-muted">Try more categories or any language. We add creators every week.</p>
        </div>
      )}
      {order.map((id) =>
        results.groups[id].length ? (
          <section key={id} aria-labelledby={`g-${id}`}>
            <h2 id={`g-${id}`} className="display text-2xl font-bold">
              {groupTitle(id, results).title} <span className="text-muted">{results.groups[id].length}</span>
            </h2>
            <p className="mt-1 text-sm text-muted">{groupTitle(id, results).sub}</p>
            <ul className="mt-5 grid gap-4 md:grid-cols-2">
              {results.groups[id].map((m, i) => (
                <MatchCard key={m.username} m={m} photo={photos[m.username]} i={i} />
              ))}
            </ul>
          </section>
        ) : id === "specialists" ? (
          <section key={id}>
            <h2 className="display text-2xl font-bold">Already showing products like yours</h2>
            <p className="mt-1 text-sm text-muted">None of our creators shows this kind of product on camera yet. The creators below can still sell it.</p>
          </section>
        ) : null,
      )}
    </div>
  );
}

function MatchCard({ m, photo, i }: { m: Match; photo?: string; i: number }) {
  return (
    <li className="card rise flex flex-col p-5 md:p-6" style={{ ["--i" as string]: Math.min(i, 8) }}>
      <div className="flex items-start gap-4">
        <Avatar src={photo} name={m.username} size={60} />
        <div className="min-w-0 flex-1">
          <a
            href={`https://www.instagram.com/${encodeURIComponent(m.username)}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="block truncate text-lg font-semibold hover:text-accent-text"
          >
            @{m.username}
          </a>
          <p className="mt-0.5 text-sm text-muted">{[CREATOR[m.creator_gender ?? ""], m.category].filter(Boolean).join(", ")}</p>
        </div>
        <div className="text-right">
          <p className="display text-3xl font-extrabold tabular-nums">{m.score}</p>
          <p className={`text-xs font-semibold ${m.verdict === "strong" ? "text-ok" : "text-muted"}`}>{m.verdict === "strong" ? "Strong fit" : "Good fit"}</p>
        </div>
      </div>

      <p className="mt-4 leading-relaxed">{m.why}</p>
      <p className="mt-2 text-sm leading-relaxed text-muted">
        <span className="font-semibold text-ink">Reel idea:</span> {m.idea}
      </p>
      {(m.product_reels.length > 0 || m.related_reels.length > 0) && (
        <p className="mt-2 text-sm text-muted">
          {m.product_reels.length > 0 && `Your kind of product in ${m.product_reels.length} of their last 12 reels. `}
          {m.related_reels.length > 0 && `Related items in ${m.related_reels.length}.`}
        </p>
      )}

      <CreatorStats c={m} />
    </li>
  );
}
