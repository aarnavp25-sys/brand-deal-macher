import { z } from "zod";

/*
  The brand brief: everything Kindred needs to know about a brand to pick creators.
  Values match the creator profiles in the "database" project (creator_overview), so every answer maps to a
  real field. No budget/price and no city: the user ruled both out.
*/

export const CATEGORIES = [
  "Beauty & Skincare",
  "Fashion & Clothing",
  "Jewelry & Accessories",
  "Food & Beverages",
  "Fitness & Wellness",
  "Home Decor & Handmade",
  "Home & Household",
  "Parenting & Kids",
  "Tech & Gadgets",
  "Travel & Explore",
  "Lifestyle & Daily Vlog",
  "Entertainment & Comedy",
  "Music & Dance",
  "Automobile",
  "Gaming",
  "Sports",
  "Pets",
  "Education & Finance",
] as const;
export type Category = (typeof CATEGORIES)[number];

export const AGES = ["18-24", "25-34", "35+"] as const;

export const LANGUAGES = [
  { id: "hindi", label: "Hindi" },
  { id: "english", label: "English" },
  { id: "marathi", label: "Marathi" },
  { id: "gujarati", label: "Gujarati" },
  { id: "punjabi", label: "Punjabi" },
  { id: "bengali", label: "Bengali" },
  { id: "tamil", label: "Tamil" },
  { id: "telugu", label: "Telugu" },
  { id: "malayalam", label: "Malayalam" },
  { id: "kannada", label: "Kannada" },
  { id: "odia", label: "Odia" },
  { id: "assamese", label: "Assamese" },
] as const;
const LANG_IDS = LANGUAGES.map((l) => l.id) as [string, ...string[]];

/** Video styles = keys of creator_overview.format_mix (what the AI saw in each reel). */
export const STYLES = [
  { id: "review_unboxing", label: "Reviews & unboxing" },
  { id: "tutorial_howto", label: "Tutorials & how-to" },
  { id: "vlog", label: "Vlogs & day in the life" },
  { id: "aesthetic_montage", label: "Aesthetic videos" },
  { id: "talking_to_camera", label: "Talking to camera" },
  { id: "skit_comedy", label: "Comedy skits" },
  { id: "transformation_before_after", label: "Before and after" },
  { id: "recipe_cooking", label: "Recipes & cooking" },
  { id: "workout", label: "Workouts" },
  { id: "dance_lipsync", label: "Dance & lip-sync" },
  { id: "work_showcase", label: "Showing their work" },
] as const;
const STYLE_IDS = STYLES.map((s) => s.id) as [string, ...string[]];

export const SIZES = [
  { id: "10-30", label: "10K to 30K followers", min: 0, max: 30_000 },
  { id: "30-60", label: "30K to 60K followers", min: 30_000, max: 60_000 },
  { id: "60-100", label: "60K to 100K followers", min: 60_000, max: 100_001 },
  { id: "any", label: "Any size", min: 0, max: 100_001 },
] as const;

export const BriefSchema = z.object({
  about: z.string().trim().min(10, "Tell us a little more about the brand.").max(1500),
  product: z.string().trim().min(2, "Name the product.").max(160),
  category: z.enum(CATEGORIES),
  customer_gender: z.enum(["women", "men", "all"]),
  customer_ages: z.array(z.enum(AGES)).max(3),
  creator_gender: z.enum(["female", "male", "any"]),
  languages: z.array(z.enum(LANG_IDS)).max(LANGUAGES.length),
  size: z.enum(["10-30", "30-60", "60-100", "any"]),
  goal: z.enum(["sales", "reach"]),
  styles: z.array(z.enum(STYLE_IDS)).max(STYLES.length),
});
export type Brief = z.infer<typeof BriefSchema>;
export type StepId = keyof Brief;

/* ------------------------------------------------------------------------------------------------------------
   Chat questions. For now they are fixed (no LLM). Later an LLM can replace `nextStep` / `questionFor` and ask
   only what the brand has not said yet; the brief shape above stays the same.
------------------------------------------------------------------------------------------------------------ */

export type Option = { value: string; label: string };
export type Step = {
  id: StepId;
  kind: "text" | "single" | "multi";
  question: string;
  placeholder?: string;
  options?: Option[];
  /** For multi steps: the option that means "no filter" (stored as an empty list). */
  anyValue?: string;
};

export const STEPS: Step[] = [
  {
    id: "about",
    kind: "text",
    question: "Tell me about your brand. What do you make, and who usually buys it?",
    placeholder: "e.g. We make handmade soy candles in small batches and sell them on our website and Instagram.",
  },
  {
    id: "product",
    kind: "text",
    question: "Which product do you want creators to promote first?",
    placeholder: "e.g. Lavender soy candle gift box",
  },
  {
    id: "category",
    kind: "single",
    question: "Which of these is closest to that product?",
    options: CATEGORIES.map((c) => ({ value: c, label: c })),
  },
  {
    id: "customer_gender",
    kind: "single",
    question: "Who mostly buys it?",
    options: [
      { value: "women", label: "Mostly women" },
      { value: "men", label: "Mostly men" },
      { value: "all", label: "Everyone" },
    ],
  },
  {
    id: "customer_ages",
    kind: "multi",
    question: "How old are most of your buyers? Pick all that apply.",
    options: [
      { value: "18-24", label: "18 to 24" },
      { value: "25-34", label: "25 to 34" },
      { value: "35+", label: "35 and above" },
      { value: "*", label: "All ages" },
    ],
    anyValue: "*",
  },
  {
    id: "creator_gender",
    kind: "single",
    question: "Do you want a female or a male creator?",
    options: [
      { value: "female", label: "Female" },
      { value: "male", label: "Male" },
      { value: "any", label: "No preference" },
    ],
  },
  {
    id: "languages",
    kind: "multi",
    question: "Which languages do your buyers watch content in?",
    options: [...LANGUAGES.map((l) => ({ value: l.id, label: l.label })), { value: "*", label: "Any language" }],
    anyValue: "*",
  },
  {
    id: "size",
    kind: "single",
    question: "How big should the creator be?",
    options: SIZES.map((s) => ({ value: s.id, label: s.label })),
  },
  {
    id: "goal",
    kind: "single",
    question: "What matters more right now?",
    options: [
      { value: "sales", label: "Sales from people who trust the creator" },
      { value: "reach", label: "Reaching as many people as possible" },
    ],
  },
  {
    id: "styles",
    kind: "multi",
    question: "Any kind of video you would like them to make?",
    options: [...STYLES.map((s) => ({ value: s.id, label: s.label })), { value: "*", label: "No preference" }],
    anyValue: "*",
  },
];

export const STEP_BY_ID = Object.fromEntries(STEPS.map((s) => [s.id, s])) as Record<StepId, Step>;

/** Draft = answers so far. */
export type Draft = Partial<Brief>;

export function nextStep(draft: Draft): Step | null {
  return STEPS.find((s) => draft[s.id] === undefined) ?? null;
}

/** Validates one answer and returns the stored value plus the text shown in the user's chat bubble. */
export function parseAnswer(step: Step, raw: unknown): { value: Brief[StepId]; label: string } {
  if (step.kind === "text") {
    const field = BriefSchema.shape[step.id] as z.ZodString;
    const value = field.parse(typeof raw === "string" ? raw : "");
    return { value, label: value };
  }
  const allowed = new Set((step.options ?? []).map((o) => o.value));
  const labelOf = (v: string) => step.options!.find((o) => o.value === v)!.label;
  if (step.kind === "single") {
    if (typeof raw !== "string" || !allowed.has(raw)) throw new Error("Pick one of the options.");
    return { value: raw as Brief[StepId], label: labelOf(raw) };
  }
  if (!Array.isArray(raw) || raw.length === 0 || raw.some((v) => typeof v !== "string" || !allowed.has(v))) {
    throw new Error("Pick at least one option.");
  }
  const picked = [...new Set(raw as string[])];
  if (picked.includes(step.anyValue!)) return { value: [] as never, label: labelOf(step.anyValue!) };
  return { value: picked as never, label: picked.map(labelOf).join(", ") };
}

/* Simple category guess from the brand's own words, shown as a pre-selected suggestion. */
const CATEGORY_WORDS: [Category, RegExp][] = [
  ["Home Decor & Handmade", /\b(candles?|decor|handmade|pottery|ceramic|macrame|crochet|art prints?|wall art|diya|resin|terracotta)\b/i],
  ["Beauty & Skincare", /\b(skin ?care|serum|face ?wash|moisturi[sz]er|sunscreen|makeup|lipstick|kajal|hair ?(oil|care)|shampoo|soaps?|beauty|nail|perfume|fragrance|attar)\b/i],
  ["Jewelry & Accessories", /\b(jewel(le)?ry|earrings?|necklaces?|rings?|bracelets?|bangles?|anklets?|watch(es)?|handbags?|bags?|sunglasses|accessor(y|ies))\b/i],
  ["Fashion & Clothing", /\b(kurta|kurti|saree|sari|dress(es)?|clothing|apparel|t-?shirts?|shirts?|ethnic ?wear|lehenga|denim|hoodies?|footwear|sneakers?|shoes)\b/i],
  ["Food & Beverages", /\b(food|snacks?|pickles?|achaar|achar|tea|chai|coffee|spices?|masala|sweets?|mithai|chocolates?|bakery|cookies|namkeen|ghee|honey|millets?|juice)\b/i],
  ["Fitness & Wellness", /\b(protein|supplements?|yoga|gym|fitness|workout|wellness|ayurved(a|ic)|herbal|nutrition)\b/i],
  ["Parenting & Kids", /\b(kids?|baby|babies|toys?|children|toddlers?|mom|moms)\b/i],
  ["Tech & Gadgets", /\b(phones?|gadgets?|earbuds|headphones|chargers?|laptops?|smart ?watch|electronics|tech)\b/i],
  ["Home & Household", /\b(cleaning|kitchen|utensils?|cookware|appliances?|bedsheets?|storage|detergent|home care)\b/i],
  ["Travel & Explore", /\b(travel|luggage|trips?|tours?|backpacks?|homestays?|hotels?)\b/i],
  ["Pets", /\b(pets?|dogs?|cats?|puppy|kitten)\b/i],
  ["Automobile", /\b(cars?|bikes?|helmets?|motorcycles?|automobile|scooters?)\b/i],
  ["Gaming", /\b(gaming|games?|esports|console)\b/i],
  ["Education & Finance", /\b(courses?|learning|coaching|finance|investing|stocks|study|tuition)\b/i],
  ["Music & Dance", /\b(music|instruments?|guitars?|dance classes?)\b/i],
  ["Sports", /\b(cricket|football|badminton|sports?|running shoes)\b/i],
];

export function guessCategory(text: string): Category | null {
  for (const [cat, re] of CATEGORY_WORDS) if (re.test(text)) return cat;
  return null;
}

export function shortCategory(c: string | null | undefined): string {
  return (c ?? "").split(" & ")[0];
}
