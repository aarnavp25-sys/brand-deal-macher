import "server-only";
import { type Brief, LANGUAGES, guessCategory, shortCategory } from "@/lib/brief";
import { passes } from "@/lib/filters";
import { type Creator, type Entry, pool, wordsRegex } from "@/lib/matching";

/*
  Demo ranking (user, 2026-11-26): from the creators that pass the brand's chat choices, the top 20 by a candidate
  score built from those choices. No LLM: same choices and same data always give the same list. The AI review
  (lib/review.ts) stays in the code, off, until personalisation is designed with the user.

  Candidate score, 0-100:
    category fit 25   share of their last 12 reels in the chosen categories (all categories: in the product's own
                      category, guessed from the brand's words; no guess: how focused the creator is)
    product seen 15   reels whose products/topic name the brand's product words (from the product the brand typed)
    audience fit 15   their audience (estimated) vs the brand's buyers
    engagement   15   percentile among all creators on Kindred
    reach        10   percentile of median views / followers
    language      5   chosen language is their main one (1), one they also speak (0.7), no talking (0.6)
    regularity    5   reels per week, 3+ = full
    brand ready   5   has done brand collabs or sponsored reels (1), maybe (0.6), none seen (0.4)
    quality       5   AI content quality good (1) / ok (0.6)
*/

export type Ranked = Creator & { score: number; reasons: string[] };
export type ResultsV5 = { version: 5; generated_at: string; considered: number; top: Ranked[] };

const TOP = 20;
// Words that describe a product but are not the product (they would match unrelated reels).
const STOP = new Set(
  ("the and for with from box pack packs set kit gift new our jar bottle men mens women womens kids girls boys size small large " +
    "starter premium natural organic minimal festive classic fresh pure homemade handmade original special combo best daily " +
    "edition range collection style plain").split(" "),
);

/** The product's own words, as the brand typed them ("Mango pickle 500g jar" -> mango, pickle). */
function productWords(product: string): string[] {
  const ws = (product.toLowerCase().match(/[a-z][a-z'-]{3,}/g) ?? []).map((w) => w.replace(/'s$/, "")).filter((w) => !STOP.has(w));
  return [...new Set(ws)].slice(0, 5);
}

const AUDIENCE: Record<string, string> = { women: "mostly women", men: "mostly men", unisex: "men and women" };

function score(e: Entry, b: Brief, prodRe: RegExp | null, productCat: string | null): { score: number; reasons: string[] } {
  const reels = e.reels_noted;
  const reasons: string[] = [];

  // category fit
  let catFit: number;
  if (b.categories.length) {
    const n = b.categories.reduce((a, c) => a + (e.content_mix[c] ?? 0), 0);
    catFit = Math.min(1, n / reels);
    const main = e.creator.category ? shortCategory(e.creator.category).toLowerCase() : "";
    if (n > 0) reasons.push(`${Math.min(n, reels)} of their last ${reels} reels are ${b.categories.length === 1 ? main || "in your category" : "in your categories"}`);
  } else if (productCat) {
    // "All categories": closeness to the product's own category (filter coffee -> food creators first)
    const n = e.content_mix[productCat] ?? 0;
    catFit = Math.min(1, n / reels);
    if (n > 0) reasons.push(`${Math.min(n, reels)} of their last ${reels} reels are ${shortCategory(productCat).toLowerCase()}`);
  } else {
    catFit = e.niche_status === "niche" ? 1 : e.niche_status === "near_niche" ? 0.8 : 0.6;
  }

  // product seen on camera
  const seen = prodRe ? e.reels.filter((r) => prodRe.test(`${r.topic} ${r.products.map((p) => `${p.item} ${p.type}`).join(" ")}`)).length : 0;
  const prodFit = Math.min(seen, 3) / 3;
  if (seen > 0) reasons.unshift(`Products like yours on camera in ${seen} of their last ${reels} reels`);

  // audience fit
  const aud = e.creator.audience_gender;
  const audFit =
    b.customer_gender === "all" ? (aud === "unisex" ? 1 : 0.8) : aud === b.customer_gender ? 1 : aud === "unisex" ? 0.7 : 0.2;
  if (aud && (b.customer_gender === "all" || aud === b.customer_gender)) reasons.push(`Audience ${AUDIENCE[aud] ?? aud} (estimated)`);

  // language fit
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
    25 * catFit + 15 * prodFit + 15 * audFit + 15 * e.eng_pct + 10 * e.reach_pct + 5 * langFit + 5 * regular + 5 * ready + 5 * quality;
  return { score: Math.round(total), reasons: reasons.slice(0, 4) };
}

export async function rankCreators(b: Brief): Promise<ResultsV5> {
  const entries = (await pool()).filter((e) => passes(e.facet, b));
  const prodRe = wordsRegex(productWords(b.product));
  const productCat = b.categories.length ? null : guessCategory(b.product, b.about);
  const ranked = entries
    .map((e) => ({ ...e.creator, ...score(e, b, prodRe, productCat) }))
    .sort((a, b2) => b2.score - a.score || b2.followers - a.followers || a.username.localeCompare(b2.username));
  return { version: 5, generated_at: new Date().toISOString(), considered: entries.length, top: ranked.slice(0, TOP) };
}
