import "server-only";
import { admin } from "@/lib/supabase/admin";
import { type Brief, LANGUAGES } from "@/lib/brief";
import { type Facet, passes } from "@/lib/filters";

/*
  Results for now (user, 2026-11-26): the creators that pass the brand's choices in the chat (categories, who buys
  it, creator gender, languages; rule in lib/filters.ts). No score and no LLM yet; biggest first.

  Who counts as a creator at all: active, has an AI profile (12 reels), account type creator/professional (no shops,
  brands, personal accounts or repost pages), in India, not weak quality, not flagged brand-unsafe.
*/

export type Creator = {
  username: string;
  followers: number;
  category: string | null;
  secondary_category: string | null;
  niche: string | null;
  about: string | null;
  creator_gender: string | null;
  languages: string[];
  no_speech: boolean;
  audience_gender: string | null;
  audience_age: string | null;
  median_views: number | null;
  engagement_rate: number | null;
  engagement_estimated: boolean;
  reels_per_week: number | null;
  brand_collabs: string | null;
  collab_brands: string[];
};

export type Results = {
  version: 3;
  generated_at: string;
  creators: Creator[];
};

type Row = {
  username: string;
  followers: number;
  median_views: number | null;
  engagement_rate: number | null;
  engagement_estimated: boolean | null;
  reels_per_week: number | null;
  account_type: string | null;
  category: string | null;
  secondary_category: string | null;
  creator_gender: string | null;
  languages: Record<string, number> | null;
  main_language: string | null;
  niche: string | null;
  niche_status: string | null;
  audience_gender_est: string | null;
  audience_age_est: string | null;
  brand_collabs: string | null;
  collab_brands: string[] | null;
  what_they_do: string | null;
  quality: string | null;
  in_india: string | null;
  flags: string[] | null;
};

const SELECT =
  "username,followers,median_views,engagement_rate,engagement_estimated,reels_per_week,account_type,category," +
  "secondary_category,creator_gender,languages,main_language,niche,niche_status,audience_gender_est," +
  "audience_age_est,brand_collabs,collab_brands,what_they_do,quality,in_india,flags";

function isCreator(r: Row): boolean {
  return (
    (r.account_type === "creator" || r.account_type === "professional") &&
    r.in_india !== "no" &&
    r.quality !== "weak" &&
    !(r.flags ?? []).some((f) => f.startsWith("not brand-safe"))
  );
}

/** Spoken languages as ids of LANGUAGES (and other names as found). Hinglish counts as Hindi and English. */
function languageIds(r: Row): string[] {
  const ids = new Set<string>();
  const add = (raw: string | null | undefined) => {
    if (!raw) return;
    const k = raw.replace(/^other:/, "");
    if (k === "hindi_urdu" || k === "hindi") ids.add("hindi");
    else if (k === "hinglish") ids.add("hindi").add("english");
    else ids.add(k);
  };
  Object.keys(r.languages ?? {}).forEach(add);
  add(r.main_language);
  return [...ids];
}

type Entry = { facet: Facet; creator: Creator };
let cache: { entries: Entry[]; at: number } | null = null;
const CACHE_MS = 5 * 60 * 1000;

async function pool(): Promise<Entry[]> {
  if (cache && Date.now() - cache.at < CACHE_MS) return cache.entries;
  const { data, error } = await admin()
    .from("creator_overview")
    .select(SELECT)
    .eq("ai_status", "done")
    .eq("activity", "active")
    .order("followers", { ascending: false })
    .limit(5000);
  if (error) throw new Error(`creator data: ${error.message}`);
  const entries = (data as unknown as Row[]).filter(isCreator).map((r): Entry => {
    const ids = languageIds(r);
    return {
      facet: { c: r.category, g: r.creator_gender, l: ids, a: r.audience_gender_est },
      creator: {
        username: r.username,
        followers: r.followers,
        category: r.category,
        secondary_category: r.secondary_category,
        niche: r.niche_status === "niche" || r.niche_status === "near_niche" ? r.niche : null,
        about: r.what_they_do,
        creator_gender: r.creator_gender,
        languages: ids.map((id) => LANGUAGES.find((l) => l.id === id)?.label ?? id.charAt(0).toUpperCase() + id.slice(1)),
        no_speech: ids.length === 0,
        audience_gender: r.audience_gender_est,
        audience_age: r.audience_age_est,
        median_views: r.median_views,
        engagement_rate: r.engagement_rate,
        engagement_estimated: Boolean(r.engagement_estimated),
        reels_per_week: r.reels_per_week,
        brand_collabs: r.brand_collabs,
        collab_brands: r.collab_brands ?? [],
      },
    };
  });
  cache = { entries, at: Date.now() };
  return entries;
}

/** Creators that pass the brand's choices, biggest first. */
export async function findCreators(brief: Brief): Promise<Results> {
  const entries = await pool();
  return {
    version: 3,
    generated_at: new Date().toISOString(),
    creators: entries.filter((e) => passes(e.facet, brief)).map((e) => e.creator),
  };
}

/** Filter attributes of every creator, for the live count in the chat. No usernames. */
export async function facets(): Promise<Facet[]> {
  return (await pool()).map((e) => e.facet);
}

/** How many creators each category has (landing page, category chips). */
export async function categoryCounts(): Promise<Record<string, number>> {
  const out: Record<string, number> = {};
  for (const { facet } of await pool()) if (facet.c) out[facet.c] = (out[facet.c] ?? 0) + 1;
  return out;
}
