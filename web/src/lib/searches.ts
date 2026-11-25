import "server-only";
import { admin } from "@/lib/supabase/admin";
import {
  BriefSchema,
  type Draft,
  INTRO,
  OUTRO,
  type StepId,
  guessCategory,
  nextStep,
  parseAnswer,
} from "@/lib/brief";
import { type Results, findCreators } from "@/lib/matching";

/*
  One row in public.brand_searches per "Find creators" chat.
  Every function takes the signed-in brand's id and only touches that brand's rows (the secret-key client
  bypasses RLS, so this filter is the access check).
*/

export type Msg = { role: "assistant" | "user"; text: string; step?: StepId; suggest?: string; at: string };
export type Status = "chatting" | "ready" | "searching" | "done" | "failed";

export type Search = {
  id: string;
  title: string | null;
  status: Status;
  messages: Msg[];
  brief: Draft | null;
  results: Results | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

const MAX_SEARCHES_PER_DAY = 25;
const MAX_MESSAGES = 40;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const COLS = "id,title,status,messages,brief,results,error,created_at,updated_at";

export class UserError extends Error {
  constructor(message: string, public status = 400) {
    super(message);
  }
}

const now = () => new Date().toISOString();

function question(draft: Draft): Msg | null {
  const step = nextStep(draft);
  if (!step) return null;
  if (step.id === "categories") {
    const guess = guessCategory(draft.product ?? "", draft.about ?? "");
    if (guess) {
      return {
        role: "assistant",
        step: step.id,
        suggest: guess,
        text: `Sounds like ${guess} to me, so I already picked it. Which creators are you vibing with? Add as many categories as you want.`,
        at: now(),
      };
    }
  }
  return { role: "assistant", step: step.id, text: step.question, at: now() };
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
      count: res?.creators?.length ?? null,
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
  const messages: Msg[] = [{ role: "assistant", text: INTRO, at: now() }, question({})!];
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

  let parsed;
  try {
    parsed = parseAnswer(step, raw);
  } catch (e) {
    const issues = (e as { issues?: { message: string }[] }).issues;
    throw new UserError(issues?.[0]?.message ?? (e as Error).message ?? "That answer did not look right.");
  }
  const draft: Draft = { ...(s.brief ?? {}), ...parsed.patch };
  const messages: Msg[] = [...s.messages, { role: "user", step: step.id, text: parsed.label, at: now() }];
  const next = question(draft);

  let update: Record<string, unknown>;
  if (next) {
    messages.push(next);
    update = { brief: draft, messages, status: "chatting" };
  } else {
    messages.push({ role: "assistant", text: OUTRO, at: now() });
    const brief = BriefSchema.parse(draft);
    let results: Results;
    try {
      results = await findCreators(brief);
    } catch (e) {
      console.error(e);
      throw new UserError("Couldn't load creators right now. Try that again in a minute.", 503);
    }
    update = { brief, messages, status: "done", results, error: null };
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
