import {
  BUYERS,
  CATEGORIES,
  CATEGORY_WORDS,
  type Category,
  CREATOR_GENDERS,
  type Draft,
  LANGUAGES,
  type Step,
  type StepId,
  guessCategory,
} from "@/lib/brief";

/*
  What Kindred says between the questions, so the chat reads like a conversation and not a form (user, 2026-11-26:
  "question-answer type nahi lagna chahiye ... proper conversation, cool conversation").
  No LLM: lines react to the brand's own words (its product name, the category its words point to, its answers),
  in short chat bubbles. Also reads typed answers ("mostly girls", "female, hindi ya english") with keywords.
*/

export type Line = { text: string; step?: StepId; suggest?: string; suggests?: string[] };

/** Short reaction to what the brand makes, chosen from the category its words point to. */
const REACTION: Partial<Record<Category, string>> = {
  "Food & Beverages": "Okay, now I'm hungry.",
  "Beauty & Skincare": "Love a good skincare story.",
  "Fashion & Clothing": "Ooh, fashion. Creators love a good fit check.",
  "Jewelry & Accessories": "Okay, shiny. I like it.",
  "Home Decor & Handmade": "Handmade stuff hits different.",
  "Home & Household": "The stuff that makes a home work. Love it.",
  "Fitness & Wellness": "Respect. The fitness crowd on Insta is huge.",
  "Parenting & Kids": "Aww. Parent creators are going to love this.",
  "Tech & Gadgets": "Gadgets! Unboxing creators, assemble.",
  "Travel & Explore": "Wanderlust brand, nice.",
  Pets: "Pets? Instant win.",
  Automobile: "Vroom. Auto creators are a fun bunch.",
  Gaming: "Gamers. Respect.",
  Sports: "Sports brands, love the energy.",
  "Education & Finance": "Smart. People love learning from creators.",
  "Music & Dance": "Music brands always have a vibe.",
};

/** The visitor's first name, for friendly lines ("" when not given). */
function firstName(d: Draft): string {
  return (d.name ?? "").trim().split(/\s+/)[0] ?? "";
}

/** The brand's product name as typed, kept short enough to fit in a sentence. */
function productName(d: Draft): string {
  const p = (d.product ?? "").trim().replace(/[.!]+$/, "");
  return p.length > 0 && p.length <= 48 ? p : "it";
}

/** Lines Kindred sends after an answer (or at the start when `answered` is null). */
type Info = { product_type: string; made_for: string; category: string; close_categories: string[]; source: string };

export function lines(answered: StepId | null, d: Draft & { product_info?: Info }, ctx: { typed?: string; label?: string; count?: number }): Line[] {
  const product = productName(d);
  const out: Line[] = [];
  switch (answered) {
    case null:
      out.push({ text: firstName(d) ? `Hey ${firstName(d)}! Let's find you some creators.` : "Hey, I'm Kindred." });
      out.push({ text: "I help brands find Instagram creators who actually fit. Not just big follower counts." });
      out.push({ text: "So tell me, what's your brand and what do you make?", step: "about" });
      break;
    case "about": {
      const cat = guessCategory("", d.about ?? "");
      out.push({ text: (cat && REACTION[cat]) || "Love that." });
      out.push({ text: "Which product should creators hype first? The one you'd put on a billboard.", step: "product" });
      break;
    }
    case "product": {
      const info = d.product_info;
      out.push({ text: product === "it" ? "Nice pick." : `${product}, nice pick.` });
      if (info && info.source === "ai") {
        const picks = [...new Set([info.category, ...info.close_categories, "Lifestyle & Daily Vlog"])];
        const forWho = info.made_for === "everyone" ? "for everyone" : `made for ${info.made_for}`;
        out.push({ text: `So it's a ${info.product_type}, ${forWho}. I'll pull creators who already show stuff like this on camera, plus a few kinds that can sell it.` });
        out.push({
          text: `I'd start with ${picks.join(", ")}. Picked those for you, change anything you like.`,
          step: "categories",
          suggest: picks[0],
          suggests: picks,
        });
        break;
      }
      const guess = guessCategory(d.product ?? "", d.about ?? "");
      if (guess) {
        out.push({ text: `Sounds like ${guess} creators to me, so I picked them already.` });
        out.push({
          text:
            guess === "Lifestyle & Daily Vlog"
              ? "Want to add any other kind of creators? Pick as many as you like."
              : "Want to add more? Lots of brands mix in lifestyle creators too.",
          step: "categories",
          suggest: guess,
        });
      } else {
        out.push({ text: "What kind of creators should we look at? Pick as many as you like.", step: "categories" });
      }
      break;
    }
    case "categories":
      if (ctx.typed) out.push({ text: `Got it: ${ctx.label}.` });
      out.push({ text: `That's ${ctx.count ?? 0} creators already. Let's narrow it down.` });
      out.push({
        text: product === "it" ? "Who's actually buying it? Mostly men, mostly women, or everyone?" : `Who's actually buying your ${product.charAt(0).toLowerCase()}${product.slice(1)}? Mostly men, mostly women, or everyone?`,
        step: "customer_gender",
      });
      break;
    case "customer_gender":
      out.push({
        text:
          d.customer_gender === "women"
            ? "Mostly women, noted."
            : d.customer_gender === "men"
              ? "Mostly men, noted."
              : "Something for everyone, love that.",
      });
      out.push({ text: "Last one. Female or male creator? And which language do your buyers scroll in?", step: "creator" });
      break;
    case "creator":
      if (ctx.typed) out.push({ text: `Got it: ${ctx.label}.` });
      out.push({ text: "Say less. Ranking the creators that fit your picks..." });
      out.push({
        text: ctx.count
          ? `Here are your top ${ctx.count}${firstName(d) ? `, ${firstName(d)}` : ""}.`
          : "Hmm, nobody fits this combo yet.",
      });
      break;
  }
  return out;
}

/* ---------------- reading typed answers to the choice questions ---------------- */

const CATEGORY_NAME_WORDS: Record<Category, RegExp> = {
  "Beauty & Skincare": /\b(beauty|skin ?care|makeup|grooming)\b/i,
  "Fashion & Clothing": /\b(fashion|clothing|clothes|outfits?|style|styling)\b/i,
  "Jewelry & Accessories": /\b(jewel(le)?ry|accessor(y|ies))\b/i,
  "Food & Beverages": /\b(food|foodies?|cooking|recipes?|chefs?|drinks?)\b/i,
  "Fitness & Wellness": /\b(fitness|gym|wellness|health|yoga)\b/i,
  "Home Decor & Handmade": /\b(home ?decor|decor|handmade|diy|crafts?)\b/i,
  "Home & Household": /\b(household|home ?care|cleaning|kitchen)\b/i,
  "Parenting & Kids": /\b(parent(ing|s)?|moms?|mommy|mothers?|dads?|kids?|baby)\b/i,
  "Tech & Gadgets": /\b(tech|gadgets?|unboxing)\b/i,
  "Travel & Explore": /\b(travel(lers?)?|trips?|explor(e|ers?))\b/i,
  "Lifestyle & Daily Vlog": /\b(lifestyle|vlog(s|gers?)?|daily|day in)\b/i,
  "Entertainment & Comedy": /\b(comedy|comedians?|funny|memes?|entertain(ment|ers?)?|skits?)\b/i,
  "Music & Dance": /\b(music|musicians?|dance|dancers?|singers?)\b/i,
  Automobile: /\b(auto(mobile)?s?|cars?|bikes?|riders?)\b/i,
  Gaming: /\b(gaming|gamers?|games?)\b/i,
  Sports: /\b(sports?|cricket|football|athletes?)\b/i,
  Pets: /\b(pets?|dogs?|cats?)\b/i,
  "Education & Finance": /\b(education|teachers?|finance|money|study)\b/i,
};

function parseCategories(text: string): string[] {
  if (/\b(all|every(thing|one)?|any(thing)?|sab)\b/i.test(text)) return ["*"];
  const found = new Set<string>();
  for (const c of CATEGORIES) if (CATEGORY_NAME_WORDS[c].test(text)) found.add(c);
  if (!found.size) for (const [c, re] of CATEGORY_WORDS) if (re.test(text)) found.add(c);
  if (!found.size) throw new Error("Hmm, I couldn't match that to a kind of creator. Tap the ones you want?");
  return [...found];
}

function parseBuyers(text: string): string {
  const women = /\b(women|woman|girls?|ladies|lady|females?|moms?|mothers?|aurat(ein)?|ladkiyan)\b/i.test(text);
  const men = /\b(men|man|guys?|boys?|males?|dads?|fathers?|ladke)\b/i.test(text);
  if (/\b(every(one|body)|all|both|any(one)?|unisex|mixed|sab)\b/i.test(text) || (women && men)) return "all";
  if (women) return "women";
  if (men) return "men";
  throw new Error("Didn't catch that. Mostly men, mostly women, or everyone?");
}

function parseCreator(text: string): { creator_gender: string; languages: string[] } {
  const anyLang = /\b(any|all|no) (language|languages|lang|preference)\b|\bany language\b/i;
  const t = text.replace(anyLang, " ");
  const female = /\b(female|girls?|woman|women|lady|ladies|she|her)\b/i.test(t);
  const male = /\b(male|guys?|man|men|boys?|he|him)\b/i.test(t);
  let gender: string | null = null;
  if (/\b(either|any(one)?|doesn'?t matter|no preference|whatever|both|koi bhi)\b/i.test(t) || (female && male)) gender = "any";
  else if (female) gender = "female";
  else if (male) gender = "male";
  if (!gender) throw new Error("Female, male, or either works? Tap one, or just type it.");
  const langs = new Set<string>();
  for (const l of LANGUAGES) if (new RegExp(`\\b${l.label}\\b`, "i").test(text)) langs.add(l.id);
  if (/\bhinglish\b/i.test(text)) langs.add("hindi").add("english");
  return { creator_gender: gender, languages: langs.size ? [...langs] : ["*"] };
}

/** Turns a typed answer to a choice question into the same value a tap would send. Throws a friendly line. */
export function parseTyped(step: Step, text: string): unknown {
  if (step.id === "categories") return parseCategories(text);
  if (step.id === "customer_gender") return parseBuyers(text);
  if (step.id === "creator") return parseCreator(text);
  return text;
}

/** Plain words for a stored answer, used in "Got it: ..." lines. */
export function describe(step: StepId, d: Draft): string {
  if (step === "categories") return d.categories?.length ? d.categories.join(", ") : "all kinds of creators";
  if (step === "customer_gender") return BUYERS.find((b) => b.value === d.customer_gender)?.label ?? "";
  if (step === "creator") {
    const g = CREATOR_GENDERS.find((x) => x.value === d.creator_gender)?.label ?? "";
    const l = d.languages?.length ? d.languages.map((x) => LANGUAGES.find((y) => y.id === x)?.label ?? x).join(", ") : "any language";
    return `${g.toLowerCase()}, ${l}`;
  }
  return "";
}
