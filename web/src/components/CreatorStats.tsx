import { compact, percent } from "@/lib/format";
import type { Creator } from "@/lib/matching";

const AUDIENCE: Record<string, string> = { women: "mostly women", men: "mostly men", unisex: "men and women" };

/**
 * The numbers and facts every creator card shows (user, 2026-11-27): followers, average views, reach, engagement,
 * comments, languages, brand collabs, and the collab contact from the creator's own bio. Old saved searches lack
 * the newer fields; those cells then show "-".
 */
export function CreatorStats({ c }: { c: Creator }) {
  const brands = c.collab_brands ?? [];
  const shown = brands.slice(0, 8);
  const contact = c.contact ?? {};
  const hasContact = Boolean(contact.email || contact.phone || contact.whatsapp);
  return (
    <>
      <dl className="mt-5 grid grid-cols-3 gap-x-3 gap-y-4 border-t border-line pt-4 sm:grid-cols-5">
        <Metric label="Followers" value={compact(c.followers)} />
        <Metric label="Avg views" value={compact(c.mean_views ?? c.median_views)} hint="Average views of their last 12 reels" />
        <Metric label="Reach" value={percent(c.reach_ratio)} hint="Typical views as a share of followers" />
        <Metric
          label="Engagement"
          value={percent(c.engagement_rate)}
          note={c.engagement_estimated ? "est." : undefined}
          hint={c.engagement_estimated ? "Likes and comments per view; estimated, many of their reels hide likes" : "Likes and comments per view"}
        />
        <Metric label="Avg comments" value={compact(c.avg_comments)} hint="Average comments per reel, last 12 reels" />
      </dl>

      <p className="mt-4 flex flex-wrap gap-x-5 gap-y-1 text-sm">
        <span>
          <span className="text-muted">Speaks</span> {c.languages.length ? c.languages.join(", ") : "no talking, music only"}
        </span>
        {c.audience_gender && (
          <span>
            <span className="text-muted">Audience (est.)</span> {AUDIENCE[c.audience_gender] ?? c.audience_gender}
          </span>
        )}
      </p>

      <p className="mt-3 text-sm">
        <span className="text-muted">Brand collabs</span>{" "}
        {shown.length ? (
          <span className="font-semibold text-ok">
            {shown.join(", ")}
            {brands.length > shown.length ? ` +${brands.length - shown.length} more` : ""}
          </span>
        ) : c.brand_collabs === "yes" ? (
          <span className="font-semibold text-ok">yes, brands not named</span>
        ) : (
          <span className="text-muted">none seen yet</span>
        )}
      </p>

      {hasContact && (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
          <span className="text-muted">Contact (from their bio)</span>
          {contact.email && (
            <a href={`mailto:${contact.email}`} className="chip break-all hover:text-accent-text">
              {contact.email}
            </a>
          )}
          {contact.phone && (
            <a href={`tel:${contact.phone.replace(/\s/g, "")}`} className="chip tabular-nums hover:text-accent-text">
              {contact.phone}
            </a>
          )}
          {contact.whatsapp && (
            <a href={contact.whatsapp} target="_blank" rel="noopener noreferrer" className="chip hover:text-accent-text">
              WhatsApp
            </a>
          )}
        </div>
      )}
    </>
  );
}

function Metric({ label, value, hint, note }: { label: string; value: string; hint?: string; note?: string }) {
  return (
    <div title={hint}>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="display mt-1 text-xl font-bold tabular-nums">
        {value}
        {note && <span className="ml-1 align-middle text-xs font-normal text-muted">{note}</span>}
      </dd>
    </div>
  );
}
