import { z } from "zod";

/*
  The brand brief, asked one question at a time in the chat (user, 2026-11-26). The brand's name is NOT a chat question:
  it is asked once in a pop-up right after Google sign-in (user, 2026-11-27: "Sign in aane ke baad sirf 'What is your
  name?' poochega ... ek pop-up type") and copied into every chat's brief. Five questions:
    1. about the brand            2. product to promote          3. creator categories (several, or all)
    4. who buys it mostly         5. creator gender + language preference (one screen)
  Then the brand sees the creators. Tone: casual, fun, Gen Z (user's ask). Values match creator_overview.
  No budget/price and no city (ruled out by the user).
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

export const BUYERS: Option[] = [
  { value: "men", label: "Mostly men" },
  { value: "women", label: "Mostly women" },
  { value: "all", label: "Everyone" },
];

export const CREATOR_GENDERS: Option[] = [
  { value: "female", label: "Female creator" },
  { value: "male", label: "Male creator" },
  { value: "any", label: "Either works" },
];

export const BriefSchema = z.object({
  /** What Kindred calls the brand (typed in the name pop-up). Never sent to the AI. Optional for chats from before
   *  2026-11-27. */
  name: z.string().trim().min(1).max(40).optional(),
  about: z.string().trim().min(10, "Tell us a bit more, a sentence or two is perfect.").max(1500),
  product: z.string().trim().min(2, "Drop the product name.").max(160),
  /** Empty = all categories. */
  categories: z.array(z.enum(CATEGORIES)).max(CATEGORIES.length),
  customer_gender: z.enum(["men", "women", "all"]),
  creator_gender: z.enum(["female", "male", "any"]),
  /** Empty = any language. */
  languages: z.array(z.enum(LANG_IDS)).max(LANGUAGES.length),
});
export type Brief = z.infer<typeof BriefSchema>;

/** The rule for the name typed in the name pop-up (letters, spaces, . ' -). */
export const TypedName = z
  .string()
  .trim()
  .min(1, "What should I call you?")
  .max(40, "Just your first name is fine.")
  .regex(/^[\p{L}\p{M}][\p{L}\p{M} .'-]*$/u, "Just your name is fine, no numbers or symbols.");

/* ------------------------------------------------------------------------------------------------------------
   Questions. Fixed for now (no LLM).
------------------------------------------------------------------------------------------------------------ */

export type Option = { value: string; label: string };
export type StepId = "about" | "product" | "categories" | "customer_gender" | "creator";
export type Step = {
  id: StepId;
  /** text = type an answer; single = tap one; multi = tap several; creator = gender + languages on one screen */
  kind: "text" | "single" | "multi" | "creator";
  question: string;
  placeholder?: string;
  max?: number;
  options?: Option[];
  /** For multi steps: the option that means "no filter" (stored as an empty list). */
  anyValue?: string;
};

export const STEPS: Step[] = [
  {
    id: "about",
    kind: "text",
    question: "Tell me about your brand. What do you make, and what's the spirit behind it?",
    placeholder: "e.g. We pour small-batch soy candles with desi scents like mogra and chai. Slow, cosy, a little nostalgic.",
    max: 1500,
  },
  {
    id: "product",
    kind: "text",
    question: "Love that. Which product should creators hype first?",
    placeholder: "e.g. Mogra candle gift box",
    max: 160,
  },
  {
    id: "categories",
    kind: "multi",
    question: "Which creators are you vibing with? Pick as many categories as you want.",
    options: [...CATEGORIES.map((c) => ({ value: c, label: c })), { value: "*", label: "All of them" }],
    anyValue: "*",
  },
  {
    id: "customer_gender",
    kind: "single",
    question: "Who's actually buying it?",
    options: BUYERS,
  },
  {
    id: "creator",
    kind: "creator",
    question: "Last one. What kind of creator, and any language preference?",
    options: [...LANGUAGES.map((l) => ({ value: l.id, label: l.label })), { value: "*", label: "Any language" }],
    anyValue: "*",
  },
];

export const STEP_BY_ID = Object.fromEntries(STEPS.map((s) => [s.id, s])) as Record<StepId, Step>;

export type Draft = Partial<Brief>;

function answered(d: Draft, id: StepId): boolean {
  if (id === "creator") return d.creator_gender !== undefined && d.languages !== undefined;
  return d[id] !== undefined;
}

export function nextStep(d: Draft): Step | null {
  return STEPS.find((s) => !answered(d, s.id)) ?? null;
}

export function answeredCount(d: Draft): number {
  return STEPS.filter((s) => answered(d, s.id)).length;
}

const label = (opts: Option[], v: string) => opts.find((o) => o.value === v)!.label;

function parseMulti(step: Step, raw: unknown): { values: string[]; text: string } {
  const opts = step.options!;
  const allowed = new Set(opts.map((o) => o.value));
  if (!Array.isArray(raw) || raw.length === 0 || raw.some((v) => typeof v !== "string" || !allowed.has(v))) {
    throw new Error("Pick at least one.");
  }
  const picked = [...new Set(raw as string[])];
  if (picked.includes(step.anyValue!)) return { values: [], text: label(opts, step.anyValue!) };
  return { values: picked, text: picked.map((v) => label(opts, v)).join(", ") };
}

/** Validates one answer. Returns the fields to store and the text for the brand's chat bubble. */
export function parseAnswer(step: Step, raw: unknown): { patch: Draft; label: string } {
  if (step.kind === "text") {
    const field = BriefSchema.shape[step.id as "about" | "product"];
    const value = field.parse(typeof raw === "string" ? raw : "");
    return { patch: { [step.id]: value }, label: value };
  }
  if (step.kind === "single") {
    if (typeof raw !== "string" || !step.options!.some((o) => o.value === raw)) throw new Error("Pick one of the options.");
    return { patch: { [step.id]: raw }, label: label(step.options!, raw) };
  }
  if (step.kind === "multi") {
    const m = parseMulti(step, raw);
    return { patch: { [step.id]: m.values }, label: m.text };
  }
  // creator: { creator_gender, languages }
  const r = (raw ?? {}) as { creator_gender?: unknown; languages?: unknown };
  if (typeof r.creator_gender !== "string" || !CREATOR_GENDERS.some((o) => o.value === r.creator_gender)) {
    throw new Error("Pick female, male or either.");
  }
  const m = parseMulti(step, r.languages);
  return {
    patch: { creator_gender: r.creator_gender as Brief["creator_gender"], languages: m.values },
    label: `${label(CREATOR_GENDERS, r.creator_gender)}, ${m.text}`,
  };
}

/* Simple category guess from the brand's own words, pre-selected in question 3. Product words count first. */
export const CATEGORY_WORDS: [Category, RegExp][] = [
  ["Home Decor & Handmade", /\b(candles?|decor|handmade|pottery|ceramic|macrame|crochet|art prints?|wall art|diya|resin|terracotta)\b/i],
  ["Beauty & Skincare", /\b(skin ?care|serum|face ?wash|moisturi[sz]er|sunscreen|makeup|lipstick|kajal|hair ?(oil|care)|shampoo|soaps?|beauty|nail|perfume|fragrance|attar)\b/i],
  ["Jewelry & Accessories", /\b(jewel(le)?ry|earrings?|necklaces?|rings?|bracelets?|bangles?|anklets?|watch(es)?|handbags?|bags?|sunglasses|accessor(y|ies))\b/i],
  ["Parenting & Kids", /\b(kids?|baby|babies|toys?|children|toddlers?)\b/i],
  ["Fashion & Clothing", /\b(kurta|kurti|saree|sari|dress(es)?|clothing|apparel|t-?shirts?|shirts?|ethnic ?wear|lehenga|denim|hoodies?|footwear|sneakers?|shoes)\b/i],
  ["Food & Beverages", /\b(food|snacks?|pickles?|achaar|achar|tea|chai|coffee|spices?|masala|sweets?|mithai|chocolates?|bakery|cookies|namkeen|ghee|honey|millets?|juice)\b/i],
  ["Fitness & Wellness", /\b(protein|supplements?|yoga|gym|fitness|workout|wellness|ayurved(a|ic)|herbal|nutrition)\b/i],
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

export function guessCategory(product: string, about = ""): Category | null {
  for (const text of [product, about]) {
    for (const [cat, re] of CATEGORY_WORDS) if (re.test(text)) return cat;
  }
  return null;
}

export function shortCategory(c: string | null | undefined): string {
  return (c ?? "").split(" & ")[0];
}
