import "server-only";
import { admin } from "@/lib/supabase/admin";
import { type Brief, type Category, LANGUAGES } from "@/lib/brief";
import { type Facet, passes } from "@/lib/filters";
import type { ProductInfo } from "@/lib/product";
import { type Contact, contactFrom } from "@/lib/contact";

/*
  Creator data for matching (view creator_overview + per-reel notes in reel_ai, both made by the video AI from each
  creator's 12 latest reels; captions and hashtags are never used).

  The brand's chat choices are hard rules (lib/filters.ts). On top of them, code reads EVIDENCE from the reel notes:
  how many reels show this very product, how many show items from the same shopping world, how many look sponsored.
  That evidence picks the shortlist the AI reviews (lib/review.ts) and feeds the score.
*/

export type ReelNote = { reel: string; topic: string; format: string; products: { item: string; type: string }[]; sponsored: boolean; on_camera: boolean; speaks: boolean };

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
  /** mean views of the latest 12 reels (the card's "Avg views"); one viral reel can lift it */
  mean_views?: number | null;
  /** typical (median) views ÷ followers */
  reach_ratio?: number | null;
  /** mean comments per reel, latest 12 reels */
  avg_comments?: number | null;
  engagement_rate: number | null;
  engagement_estimated: boolean;
  reels_per_week: number | null;
  brand_collabs: string | null;
  collab_brands: string[];
  /** email / phone / WhatsApp the creator put in their own bio */
  contact?: Contact;
};

export type Evidence = { product_reels: string[]; related_reels: string[]; sponsored_reels: number; category_share: number };

export type Entry = {
  facet: Facet;
  creator: Creator;
  reels: ReelNote[];
  content_mix: Record<string, number>;
  reels_noted: number;
  eng_pct: number;
  reach_pct: number;
  niche_status: string | null;
  quality: string | null;
  main_language: string | null;
  sells_own_products: boolean;
  offers_services: boolean;
};

/** Results without AI (LLM off or unavailable): every creator that passes the choices, biggest first. */
export type ResultsV3 = { version: 3; generated_at: string; creators: Creator[]; notice?: string };

type Row = {
  username: string;
  followers: number;
  median_views: number | null;
  reach_ratio: number | null;
  engagement_rate: number | null;
  engagement_estimated: boolean | null;
  reels_per_week: number | null;
  account_type: string | null;
  category: string | null;
  secondary_category: string | null;
  content_mix: Record<string, number> | null;
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
  reels_noted: number | null;
  sells_own_products: boolean | null;
  offers_services: boolean | null;
};

const SELECT =
  "username,followers,median_views,reach_ratio,engagement_rate,engagement_estimated,reels_per_week,account_type,category," +
  "secondary_category,content_mix,creator_gender,languages,main_language,niche,niche_status,audience_gender_est," +
  "audience_age_est,brand_collabs,collab_brands,what_they_do,quality,in_india,flags,reels_noted,sells_own_products,offers_services";

function isCreator(r: Row): boolean {
  return (
    (r.account_type === "creator" || r.account_type === "professional") &&
    r.in_india !== "no" &&
    r.quality !== "weak" &&
    !(r.flags ?? []).some((f) => f.startsWith("not brand-safe"))
  );
}

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

function percentiles(rows: Row[], pick: (r: Row) => number | null): Map<string, number> {
  const vals = rows.map((r) => [r.username, pick(r)] as const).filter((x): x is readonly [string, number] => x[1] != null);
  vals.sort((a, b) => a[1] - b[1]);
  const out = new Map<string, number>();
  vals.forEach(([u], i) => out.set(u, vals.length > 1 ? i / (vals.length - 1) : 0.5));
  return out;
}

async function loadReelNotes(): Promise<Map<string, ReelNote[]>> {
  const out = new Map<string, ReelNote[]>();
  for (let offset = 0; ; offset += 1000) {
    const { data, error } = await admin()
      .from("reel_ai")
      .select("username,reel,topic:note->>topic,format:note->>format,products:note->products,sponsored:note->>sponsored_signs,on:note->>owner_on_screen,sp:note->>owner_speaks")
      .order("username")
      .order("reel")
      .range(offset, offset + 999);
    if (error) throw new Error(`reel notes: ${error.message}`);
    for (const r of (data ?? []) as unknown as { username: string; reel: string; topic: string | null; format: string | null; products: unknown; sponsored: string | null; on: string | null; sp: string | null }[]) {
      const products = (Array.isArray(r.products) ? r.products : [])
        .map((p) => ({ item: String((p as { item?: unknown }).item ?? ""), type: String((p as { type?: unknown }).type ?? "") }))
        .filter((p) => p.item || p.type);
      const list = out.get(r.username) ?? [];
      list.push({ reel: r.reel, topic: r.topic ?? "", format: r.format ?? "", products, sponsored: Boolean(r.sponsored && r.sponsored.trim()), on_camera: r.on === "yes", speaks: r.sp === "yes" });
      out.set(r.username, list);
    }
    if (!data || data.length < 1000) break;
  }
  return out;
}

let cache: { entries: Entry[]; at: number } | null = null;
const CACHE_MS = 5 * 60 * 1000;

/** Card numbers and bio contact per creator (view creator_card_stats, migration 003). */
async function loadCardStats(): Promise<Map<string, { mean_views: number | null; avg_comments: number | null; contact: Contact }>> {
  const { data, error } = await admin().from("creator_card_stats").select("username,mean_views,avg_comments,bio,bio_links").limit(5000);
  if (error) throw new Error(`card stats: ${error.message}`);
  const out = new Map<string, { mean_views: number | null; avg_comments: number | null; contact: Contact }>();
  for (const r of (data ?? []) as { username: string; mean_views: number | null; avg_comments: number | null; bio: string | null; bio_links: { url?: string }[] | null }[]) {
    out.set(r.username, { mean_views: r.mean_views, avg_comments: r.avg_comments, contact: contactFrom(r.bio, r.bio_links) });
  }
  return out;
}

export async function pool(): Promise<Entry[]> {
  if (cache && Date.now() - cache.at < CACHE_MS) return cache.entries;
  const [{ data, error }, notes, stats] = await Promise.all([
    admin().from("creator_overview").select(SELECT).eq("ai_status", "done").eq("activity", "active").order("followers", { ascending: false }).limit(5000),
    loadReelNotes(),
    loadCardStats(),
  ]);
  if (error) throw new Error(`creator data: ${error.message}`);
  const rows = (data as unknown as Row[]).filter(isCreator);
  const eng = percentiles(rows, (r) => r.engagement_rate);
  const reach = percentiles(rows, (r) => r.reach_ratio);
  const entries = rows.map((r): Entry => {
    const ids = languageIds(r);
    return {
      facet: { c: r.category, g: r.creator_gender, l: ids, a: r.audience_gender_est, f: r.followers ?? 0 },
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
        mean_views: stats.get(r.username)?.mean_views ?? null,
        reach_ratio: r.reach_ratio,
        avg_comments: stats.get(r.username)?.avg_comments ?? null,
        contact: stats.get(r.username)?.contact ?? {},
        engagement_rate: r.engagement_rate,
        engagement_estimated: Boolean(r.engagement_estimated),
        reels_per_week: r.reels_per_week,
        brand_collabs: r.brand_collabs,
        collab_brands: r.collab_brands ?? [],
      },
      reels: notes.get(r.username) ?? [],
      content_mix: r.content_mix ?? {},
      reels_noted: Math.max(r.reels_noted ?? 12, 1),
      eng_pct: eng.get(r.username) ?? 0.5,
      reach_pct: reach.get(r.username) ?? 0.5,
      niche_status: r.niche_status,
      quality: r.quality,
      main_language: r.main_language,
      sells_own_products: Boolean(r.sells_own_products),
      offers_services: Boolean(r.offers_services),
    };
  });
  cache = { entries, at: Date.now() };
  return entries;
}

/* ---------------- evidence from reel notes ---------------- */

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
export function wordsRegex(words: string[]): RegExp | null {
  const ws = words.map((w) => w.trim().toLowerCase()).filter(Boolean);
  if (!ws.length) return null;
  return new RegExp(`\\b(${ws.map((w) => `${esc(w)}(?:e?s)?`).join("|")})\\b`, "i");
}

export function evidence(e: Entry, p: ProductInfo, cats: string[]): Evidence {
  const prodRe = wordsRegex(p.product_words);
  const relRe = wordsRegex(p.related_words);
  const product_reels: string[] = [];
  const related_reels: string[] = [];
  let sponsored = 0;
  for (const r of e.reels) {
    const items = r.products.map((x) => `${x.item} ${x.type}`).join(" ; ");
    if (prodRe && (prodRe.test(items) || prodRe.test(r.topic))) product_reels.push(r.reel);
    else if (relRe && relRe.test(items)) related_reels.push(r.reel);
    if (r.sponsored) sponsored++;
  }
  const inCats = cats.reduce((a, c) => a + (e.content_mix[c] ?? 0), 0);
  return { product_reels, related_reels, sponsored_reels: sponsored, category_share: Math.min(1, inCats / e.reels_noted) };
}

/** Creators that pass the brand's choices, plus creators from any category who already show the product. */
export async function candidates(brief: Brief, p: ProductInfo): Promise<{ entry: Entry; ev: Evidence }[]> {
  const entries = await pool();
  const cats = [...new Set<string>([...(brief.categories.length ? brief.categories : []), p.category, ...p.close_categories])];
  const out: { entry: Entry; ev: Evidence }[] = [];
  for (const e of entries) {
    const inChoice = passes(e.facet, brief);
    const ev = evidence(e, p, cats);
    // a creator who already shows the product (2+ reels) is a specialist whatever their main category,
    // but still must match the brand's creator gender, languages and buyers
    const specialist = ev.product_reels.length >= 2 && passes(e.facet, { ...brief, categories: [] });
    if (inChoice || specialist) out.push({ entry: e, ev });
  }
  return out;
}

/** Results without AI: every creator that passes the choices, biggest first. */
export async function findCreators(brief: Brief, notice?: string): Promise<ResultsV3> {
  const entries = await pool();
  return {
    version: 3,
    generated_at: new Date().toISOString(),
    creators: entries.filter((e) => passes(e.facet, brief)).map((e) => e.creator),
    ...(notice ? { notice } : {}),
  };
}

export async function facets(): Promise<Facet[]> {
  return (await pool()).map((e) => e.facet);
}

export async function categoryCounts(): Promise<Record<string, number>> {
  const out: Record<string, number> = {};
  for (const { facet } of await pool()) if (facet.c) out[facet.c] = (out[facet.c] ?? 0) + 1;
  return out;
}

export type { Category };
