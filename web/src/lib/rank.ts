import "server-only";
import { type Brief, type Category, LANGUAGES, guessCategory, shortCategory } from "@/lib/brief";
import { passes } from "@/lib/filters";
import { type Creator, type Entry, pool, wordsRegex } from "@/lib/matching";

/*
  Demo ranking (user, 2026-11-26): from the creators that pass the brand's chat choices, the top 20 by a candidate
  score. No LLM: same choices and same data always give the same list.

  Relevance to the PRODUCT leads, not the category label (2026-11-26: a nail-art studio reached a watch brand's top
  20 because the brand had ticked Beauty; on 2026-11-20 a dermatology page passed as "Beauty" the same way).
  The chosen categories only decide where to look.

  Candidate score, 0-100:
    product relevance 35  share of their 12 reels in the product's own category (x1), a close category (x0.8,
                          the fixed neighbours agreed on 2026-11-20) or Lifestyle (x0.5); + reels that show the
                          product itself. Below 0.2 = no link to the product: never in the top 20 (if at least 5 have one).
    audience fit      15  their audience (estimated) vs the brand's buyers
    engagement        15  percentile on Kindred
    reach             10  percentile of median views / followers
    on camera         10  share of reels where the creator is on screen or speaks (a portfolio of clients' looks
                          or a studio page scores low here and gets a label; portfolio pages are never in the top 20)
    language           5  chosen language is their main one (1), one they also speak (0.7), no talking (0.6)
    regularity         4  reels per week, 3+ = full
    brand ready        3  brand collabs or sponsored reels seen
    quality            3  AI content quality good / ok
  Unknown product category (no keyword match): relevance = share of reels in the chosen categories.
*/

export type Ranked = Creator & { score: number; reasons: string[]; label: string | null };
export type ResultsV5 = { version: 5; generated_at: string; considered: number; relevant: number; top: Ranked[] };

const TOP = 20;
const MIN_RELEVANCE = 0.2;
const LIFESTYLE: Category = "Lifestyle & Daily Vlog";

/** Close categories whose creators naturally show the product (fixed list, agreed 2026-11-20). */
const NEIGHBOURS: Partial<Record<Category, Category[]>> = {
  "Jewelry & Accessories": ["Fashion & Clothing"],
  "Fashion & Clothing": ["Jewelry & Accessories", "Beauty & Skincare"],
  "Beauty & Skincare": ["Fashion & Clothing"],
  "Fitness & Wellness": ["Sports"],
  Sports: ["Fitness & Wellness"],
  "Tech & Gadgets": ["Gaming"],
  Gaming: ["Tech & Gadgets"],
  "Home Decor & Handmade": ["Home & Household"],
  "Home & Household": ["Home Decor & Handmade"],
};

// Words that describe a product but are not the product (they would match unrelated reels).
const STOP = new Set(
  ("the and for with from box pack packs set kit gift new our jar bottle men mens women womens kids girls boys size small large " +
    "starter premium natural organic minimal festive classic fresh pure homemade handmade original special combo best daily " +
    "edition range collection style plain brand brands sell sells selling midpremium").split(" "),
);

function productWords(product: string): string[] {
  const ws = (product.toLowerCase().match(/[a-z][a-z'-]{3,}/g) ?? []).map((w) => w.replace(/'s$/, "")).filter((w) => !STOP.has(w));
  return [...new Set(ws)].slice(0, 5);
}

const AUDIENCE: Record<string, string> = { women: "mostly women", men: "mostly men", unisex: "men and women" };

type Ctx = { b: Brief; prodRe: RegExp | null; productCat: Category | null; close: Category[] };

function relevance(e: Entry, c: Ctx): { rel: number; seen: number; line: string | null } {
  const reels = e.reels_noted;
  const seen = c.prodRe ? e.reels.filter((r) => c.prodRe!.test(`${r.topic} ${r.products.map((p) => `${p.item} ${p.type}`).join(" ")}`)).length : 0;
  if (!c.productCat) {
    const n = c.b.categories.length ? c.b.categories.reduce((a, k) => a + (e.content_mix[k] ?? 0), 0) : reels * 0.6;
    const rel = Math.min(1, n / reels + 0.15 * Math.min(seen, 3));
    return { rel, seen, line: c.b.categories.length && n > 0 ? `${Math.min(n, reels)} of their last ${reels} reels are in your categories` : null };
  }
  const own = e.content_mix[c.productCat] ?? 0;
  const close = c.close.reduce((a, k) => a + (e.content_mix[k] ?? 0), 0);
  const life = c.productCat === LIFESTYLE ? 0 : e.content_mix[LIFESTYLE] ?? 0;
  const rel = Math.min(1, (own + 0.8 * close + 0.5 * life) / reels + 0.15 * Math.min(seen, 3));
  const parts: string[] = [];
  if (own) parts.push(`${own} ${shortCategory(c.productCat).toLowerCase()}`);
  if (close) parts.push(`${close} ${c.close.map((k) => shortCategory(k).toLowerCase()).join("/")}`);
  if (life && !own && !close) parts.push(`${life} lifestyle`);
  return { rel, seen, line: parts.length ? `Of their last ${reels} reels: ${parts.join(", ")}` : null };
}

function score(e: Entry, c: Ctx): { score: number; rel: number; reasons: string[]; label: string | null } {
  const { b } = c;
  const reasons: string[] = [];
  const { rel, seen, line } = relevance(e, c);
  if (seen > 0) reasons.push(`Products like yours on camera in ${seen} of their last ${e.reels_noted} reels`);
  if (line) reasons.push(line);

  const aud = e.creator.audience_gender;
  const audFit = b.customer_gender === "all" ? (aud === "unisex" ? 1 : 0.8) : aud === b.customer_gender ? 1 : aud === "unisex" ? 0.7 : 0.2;
  if (aud && (b.customer_gender === "all" || aud === b.customer_gender)) reasons.push(`Audience ${AUDIENCE[aud] ?? aud} (estimated)`);

  const n = Math.max(e.reels.length, 1);
  const present = e.reels.filter((r) => r.on_camera || r.speaks).length / n;
  const onScreen = e.reels.filter((r) => r.on_camera).length;
  const showcase = e.reels.filter((r) => r.format === "work_showcase").length;
  let label: string | null = null;
  if ((e.sells_own_products || e.offers_services) && onScreen < n / 2 && showcase >= 3) label = "Portfolio page: mostly shows clients' looks or their own work, rarely on camera";
  else if (e.sells_own_products && e.offers_services) label = "Runs their own studio or business";

  const main = e.main_language === "hindi" || e.main_language === "hindi_urdu" ? "hindi" : (e.main_language ?? "").replace(/^other:/, "");
  const langFit = !b.languages.length ? 1 : e.facet.l.length === 0 ? 0.6 : b.languages.includes(main) ? 1 : 0.7;
  if (b.languages.length && langFit === 1) reasons.push(`Talks mainly in ${LANGUAGES.find((l) => l.id === main)?.label ?? main}`);

  const regular = Math.min(1, (e.creator.reels_per_week ?? 0) / 3);
  const ready = e.creator.brand_collabs === "yes" ? 1 : e.creator.brand_collabs === "maybe" ? 0.6 : 0.4;
  const quality = e.quality === "good" ? 1 : 0.6;
  if (e.eng_pct >= 0.75) reasons.push(`Engagement in the top ${Math.max(1, Math.round((1 - e.eng_pct) * 100))}% on Kindred`);
  if (e.reach_pct >= 0.75) reasons.push("Reels reach well beyond their followers");
  if (e.creator.brand_collabs === "yes") reasons.push(e.creator.collab_brands.length ? `Has worked with ${e.creator.collab_brands.slice(0, 2).join(", ")}` : "Has done brand collabs");

  const total =
    35 * rel + 15 * audFit + 15 * e.eng_pct + 10 * e.reach_pct + 10 * present + 5 * langFit + 4 * regular + 3 * ready + 3 * quality;
  return { score: Math.round(total), rel, reasons: reasons.slice(0, 4), label };
}

export async function rankCreators(b: Brief): Promise<ResultsV5> {
  const entries = (await pool()).filter((e) => passes(e.facet, b));
  const productCat = guessCategory(b.product, b.about);
  const ctx: Ctx = { b, prodRe: wordsRegex(productWords(b.product)), productCat, close: productCat ? NEIGHBOURS[productCat] ?? [] : [] };
  const scored = entries
    .map((e) => {
      const s = score(e, ctx);
      return { ...e.creator, score: s.score, reasons: s.reasons, label: s.label, rel: s.rel };
    })
    .sort((a, x) => x.score - a.score || x.followers - a.followers || a.username.localeCompare(x.username));
  // Portfolio pages (clients' looks / own work, owner rarely on camera) are not creators for a brand reel:
  // never in the top 20 (user, 2026-11-26, about a designer's showcase page in a watch search).
  const usable = scored.filter((x) => !x.label?.startsWith("Portfolio"));
  const related = usable.filter((x) => x.rel >= MIN_RELEVANCE);
  const pick = related.length >= 5 ? related : usable;
  return {
    version: 5,
    generated_at: new Date().toISOString(),
    considered: entries.length,
    relevant: related.length,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    top: pick.slice(0, TOP).map(({ rel, ...x }) => x),
  };
}
