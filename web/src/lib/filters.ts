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
*/

/** The few attributes the filter needs. Sent to the browser for the live count (no usernames). */
export type Facet = { c: string | null; g: string | null; l: string[]; a: string | null };

export function passes(f: Facet, b: Draft): boolean {
  if (b.categories?.length && !(b.categories as string[]).includes(f.c ?? "")) return false;
  if (b.creator_gender && b.creator_gender !== "any" && f.g !== b.creator_gender) return false;
  if (b.languages?.length && f.l.length && !b.languages.some((x) => f.l.includes(x))) return false;
  if (b.customer_gender === "men" && f.a === "women") return false;
  if (b.customer_gender === "women" && f.a === "men") return false;
  return true;
}

export function countMatches(facets: Facet[], b: Draft): number {
  let n = 0;
  for (const f of facets) if (passes(f, b)) n++;
  return n;
}
