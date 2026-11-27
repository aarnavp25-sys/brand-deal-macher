import type { Draft } from "@/lib/brief";

/*
  The one filter rule, shared by the server (results) and the browser (live "N creators match" count in the chat),
  so the count the brand sees is exactly the number of creators the results page shows.

  A creator passes when:
    - categories:      its main category is one of the chosen ones (none chosen / "All" = every category)
    - creator gender:  female / male matches; "No preference" = everyone
    - languages:       it speaks at least one chosen language; creators with no speech at all (music-only reels)
                       pass every language choice, since their videos have no language
    - who buys it:     "Mostly men" hides creators whose audience is mostly women, and the other way round;
                       "Everyone" hides nobody
    - followers:       between the brand's min and max (user, 2026-11-27: a two-handle slider). The slider's ends
                       (10K, 100K) mean "no limit on this side", so the few creators who dropped just under 10K
                       since they were collected still show when the brand leaves the lower handle at 10K.
*/

export const FOLLOWERS_MIN = 10_000;
export const FOLLOWERS_MAX = 100_000;
export const FOLLOWERS_STEP = 1_000;

/** The few attributes the filter needs. Sent to the browser for the live count (no usernames). */
export type Facet = { c: string | null; g: string | null; l: string[]; a: string | null; f: number };

export function passes(f: Facet, b: Draft): boolean {
  if (b.categories?.length && !(b.categories as string[]).includes(f.c ?? "")) return false;
  if (b.creator_gender && b.creator_gender !== "any" && f.g !== b.creator_gender) return false;
  if (b.languages?.length && f.l.length && !b.languages.some((x) => f.l.includes(x))) return false;
  if (b.customer_gender === "men" && f.a === "women") return false;
  if (b.customer_gender === "women" && f.a === "men") return false;
  if (b.followers_min != null && b.followers_min > FOLLOWERS_MIN && f.f < b.followers_min) return false;
  if (b.followers_max != null && b.followers_max < FOLLOWERS_MAX && f.f > b.followers_max) return false;
  return true;
}

export function countMatches(facets: Facet[], b: Draft): number {
  let n = 0;
  for (const f of facets) if (passes(f, b)) n++;
  return n;
}
