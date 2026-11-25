import "server-only";
import { admin } from "@/lib/supabase/admin";
import { type Category, LANGUAGES } from "@/lib/brief";

/*
  Results for now (user, 2026-11-26): the brand picks a category in the chat and sees EVERY creator whose main
  category is that one. No score, no LLM, no other filters yet; the other chat answers are saved in the brief for
  the matching that comes later.

  Who counts as a creator: active, has an AI profile (from 12 reels), account type creator/professional (no shops,
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
  version: 2;
  generated_at: string;
  category: Category;
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

/** Spoken languages as display names. Hinglish counts as Hindi and English. */
function languagesOf(r: Row): string[] {
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
  return [...ids].map((id) => LANGUAGES.find((l) => l.id === id)?.label ?? id.charAt(0).toUpperCase() + id.slice(1));
}

export async function creatorsInCategory(category: Category): Promise<Results> {
  const { data, error } = await admin()
    .from("creator_overview")
    .select(SELECT)
    .eq("ai_status", "done")
    .eq("activity", "active")
    .eq("category", category)
    .order("followers", { ascending: false })
    .limit(2000);
  if (error) throw new Error(`creator data: ${error.message}`);

  const creators = (data as unknown as Row[]).filter(isCreator).map(
    (r): Creator => ({
      username: r.username,
      followers: r.followers,
      category: r.category,
      secondary_category: r.secondary_category,
      niche: r.niche_status === "niche" || r.niche_status === "near_niche" ? r.niche : null,
      about: r.what_they_do,
      creator_gender: r.creator_gender,
      languages: languagesOf(r),
      audience_gender: r.audience_gender_est,
      audience_age: r.audience_age_est,
      median_views: r.median_views,
      engagement_rate: r.engagement_rate,
      engagement_estimated: Boolean(r.engagement_estimated),
      reels_per_week: r.reels_per_week,
      brand_collabs: r.brand_collabs,
      collab_brands: r.collab_brands ?? [],
    }),
  );
  return { version: 2, generated_at: new Date().toISOString(), category, creators };
}

/** How many creators each category has, for the category question in the chat. */
export async function categoryCounts(): Promise<Record<string, number>> {
  const { data, error } = await admin()
    .from("creator_overview")
    .select("category,account_type,in_india,quality,flags")
    .eq("ai_status", "done")
    .eq("activity", "active")
    .limit(5000);
  if (error) throw new Error(`creator data: ${error.message}`);
  const out: Record<string, number> = {};
  for (const r of data as unknown as Row[]) if (r.category && isCreator(r)) out[r.category] = (out[r.category] ?? 0) + 1;
  return out;
}
