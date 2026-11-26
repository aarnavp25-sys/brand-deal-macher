import "server-only";
import { admin } from "@/lib/supabase/admin";
import { BriefSchema, type Draft, type StepId, nextStep, parseAnswer } from "@/lib/brief";
import { type Line, describe, lines, parseTyped } from "@/lib/conversation";
import { countMatches } from "@/lib/filters";
import { type ResultsV3, facets } from "@/lib/matching";
import { type ProductInfo, understandProduct } from "@/lib/product";
import { type ResultsV4, reviewCreators } from "@/lib/review";
import { LLMUnavailable, llmEnabled } from "@/lib/llm";
import { type ResultsV5, rankCreators } from "@/lib/rank";

export type Results = ResultsV3 | ResultsV4 | ResultsV5;
export type StoredBrief = Draft & { product_info?: ProductInfo };

/** Number of creators shown, for either kind of results. */
export function resultCount(r: Results | null | undefined): number | null {
  if (!r) return null;
  if (r.version === 4) return Object.values(r.groups).reduce((a, g) => a + g.length, 0);
  if (r.version === 5) return r.top.length;
  return r.creators?.length ?? null;
}

/*
  One row in public.brand_searches per "Find creators" chat.
  Every function takes the signed-in brand's id and only touches that brand's rows (the secret-key client
  bypasses RLS, so this filter is the access check).
*/

export type Msg = { role: "assistant" | "user"; text: string; step?: StepId; suggest?: string; suggests?: string[]; at: string };
export type Status = "chatting" | "ready" | "searching" | "done" | "failed";

export type Search = {
  id: string;
  title: string | null;
  status: Status;
  messages: Msg[];
  brief: StoredBrief | null;
  results: Results | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

const MAX_SEARCHES_PER_DAY = 25;
const MAX_MESSAGES = 60;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const COLS = "id,title,status,messages,brief,results,error,created_at,updated_at";

export class UserError extends Error {
  constructor(message: string, public status = 400) {
    super(message);
  }
}

const now = () => new Date().toISOString();

function toMsgs(ls: Line[]): Msg[] {
  const at = now();
  return ls.map((l) => ({ role: "assistant" as const, text: l.text, step: l.step, suggest: l.suggest, suggests: l.suggests, at }));
}

export async function listSearches(userId: string) {
  const { data, error } = await admin()
    .from("brand_searches")
    .select("id,title,status,brief,results,created_at")
    .eq("user_id", userId)
    .order("created_at", { ascending: false })
    .limit(50);
  if (error) throw new Error(error.message);
  return (data ?? []).map((r) => {
    const b = (r.brief ?? {}) as Draft & { category?: string };
    const res = r.results as Results | null;
    const cats = b.categories ? (b.categories.length ? b.categories.join(", ") : "All categories") : b.category ?? null;
    return {
      id: r.id as string,
      title: r.title as string | null,
      status: r.status as Status,
      categories: cats,
      count: resultCount(res),
      created_at: r.created_at as string,
    };
  });
}

export async function getSearch(userId: string, id: string): Promise<Search | null> {
  if (!UUID.test(id)) return null;
  const { data, error } = await admin().from("brand_searches").select(COLS).eq("id", id).eq("user_id", userId).maybeSingle();
  if (error) throw new Error(error.message);
  return (data as Search | null) ?? null;
}

export async function createSearch(userId: string): Promise<string> {
  const since = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
  const { count, error: cErr } = await admin()
    .from("brand_searches")
    .select("id", { count: "exact", head: true })
    .eq("user_id", userId)
    .gte("created_at", since);
  if (cErr) throw new Error(cErr.message || "could not count searches");
  if ((count ?? 0) >= MAX_SEARCHES_PER_DAY) {
    throw new UserError("You've started a lot of searches today. Come back tomorrow?", 429);
  }
  const messages: Msg[] = toMsgs(lines(null, {}, {}));
  const { data, error } = await admin().from("brand_searches").insert({ user_id: userId, messages, brief: {} }).select("id").single();
  if (error) throw new Error(error.message);
  return data.id as string;
}

/**
 * Saves the answer to the current question and adds the next question. After the last question the creators are
 * found and stored right away (status "done").
 */
export async function answer(userId: string, id: string, stepId: unknown, raw: unknown): Promise<Search> {
  const s = await getSearch(userId, id);
  if (!s) throw new UserError("Search not found.", 404);
  if (s.status !== "chatting") throw new UserError("This chat is already finished.", 409);
  if (s.messages.length >= MAX_MESSAGES) throw new UserError("This chat is too long. Start a new search.", 409);

  const step = nextStep(s.brief ?? {});
  if (!step || step.id !== stepId) throw new UserError("That question was already answered. Refresh the page.", 409);

  // A choice question can also be answered by typing ("mostly girls"); it is read with keywords, no LLM.
  const typed =
    step.kind !== "text" && raw && typeof raw === "object" && !Array.isArray(raw) && typeof (raw as { text?: unknown }).text === "string"
      ? (raw as { text: string }).text.trim().slice(0, 300)
      : null;
  let parsed;
  try {
    parsed = parseAnswer(step, typed !== null ? parseTyped(step, typed) : raw);
  } catch (e) {
    const issues = (e as { issues?: { message: string }[] }).issues;
    throw new UserError(issues?.[0]?.message ?? (e as Error).message ?? "That answer did not look right.");
  }
  const draft: StoredBrief = { ...(s.brief ?? {}), ...parsed.patch };
  // After the product answer the AI reads what the product is (lib/product.ts); keywords if AI is off or fails.
  if (step.id === "product") draft.product_info = await understandProduct(draft.about ?? "", draft.product ?? "", { userId, searchId: id });
  const messages: Msg[] = [...s.messages, { role: "user", step: step.id, text: typed || parsed.label, at: now() }];
  const ctx = { typed: typed ?? undefined, label: describe(step.id, draft) };

  let update: Record<string, unknown>;
  if (nextStep(draft)) {
    const count = step.id === "categories" ? countMatches(await facets(), draft) : undefined;
    messages.push(...toMsgs(lines(step.id, draft, { ...ctx, count })));
    update = { brief: draft, messages, status: "chatting" };
  } else {
    const brief = BriefSchema.parse(draft);
    const info = draft.product_info ?? (await understandProduct(brief.about, brief.product, { userId, searchId: id }));
    let results: Results;
    // Demo (user, 2026-11-26): top 20 by the candidate score, no LLM. The AI review runs only when LLM_REVIEW=true.
    const aiReview = process.env.LLM_REVIEW === "true" && llmEnabled();
    try {
      if (!aiReview) throw new LLMUnavailable("off");
      results = await reviewCreators(brief, info, { userId, searchId: id });
    } catch (e) {
      if (!(e instanceof LLMUnavailable)) console.error(e);
      try {
        results = await rankCreators(brief);
      } catch (e2) {
        console.error(e2);
        throw new UserError("Couldn't load creators right now. Try that again in a minute.", 503);
      }
    }
    messages.push(...toMsgs(lines(step.id, draft, { ...ctx, count: resultCount(results) ?? 0 })));
    update = { brief: { ...brief, product_info: info }, messages, status: "done", results, error: null };
  }

  const { data, error } = await admin()
    .from("brand_searches")
    .update({ ...update, title: draft.product ?? null, updated_at: now() })
    .eq("id", id)
    .eq("user_id", userId)
    .eq("status", "chatting")
    .select(COLS)
    .maybeSingle();
  if (error) throw new Error(error.message);
  if (!data) throw new UserError("That question was already answered. Refresh the page.", 409);
  return data as Search;
}

export async function deleteSearch(userId: string, id: string): Promise<void> {
  if (!UUID.test(id)) throw new UserError("Search not found.", 404);
  const { error } = await admin().from("brand_searches").delete().eq("id", id).eq("user_id", userId);
  if (error) throw new Error(error.message);
}
