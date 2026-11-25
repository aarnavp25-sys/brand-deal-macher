import "server-only";
import { admin } from "@/lib/supabase/admin";
import {
  BriefSchema,
  type Brief,
  type Draft,
  type StepId,
  STEP_BY_ID,
  guessCategory,
  nextStep,
  parseAnswer,
} from "@/lib/brief";
import { type Results, creatorsInCategory } from "@/lib/matching";

/*
  One row in public.brand_searches per "Find creators" conversation.
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
const MAX_MESSAGES = 60;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export class UserError extends Error {
  constructor(message: string, public status = 400) {
    super(message);
  }
}

const now = () => new Date().toISOString();

function question(draft: Draft): Msg | null {
  const step = nextStep(draft);
  if (!step) return null;
  if (step.id === "category") {
    const guess = guessCategory(`${draft.product ?? ""} ${draft.about ?? ""}`);
    return {
      role: "assistant",
      step: step.id,
      suggest: guess ?? undefined,
      text: guess ? `Looks like ${guess} to me. Is that right, or is another one closer?` : step.question,
      at: now(),
    };
  }
  return { role: "assistant", step: step.id, text: step.question, at: now() };
}

export async function listSearches(userId: string) {
  const { data, error } = await admin()
    .from("brand_searches")
    .select("id,title,status,brief,results,created_at,updated_at")
    .eq("user_id", userId)
    .order("created_at", { ascending: false })
    .limit(50);
  if (error) throw new Error(error.message);
  return (data ?? []).map((r) => {
    const res = r.results as Results | null;
    return {
      id: r.id as string,
      title: r.title as string | null,
      status: r.status as Status,
      category: ((r.brief as Draft | null)?.category ?? null) as string | null,
      count: res?.creators?.length ?? null,
      created_at: r.created_at as string,
    };
  });
}

export async function getSearch(userId: string, id: string): Promise<Search | null> {
  if (!UUID.test(id)) return null;
  const { data, error } = await admin()
    .from("brand_searches")
    .select("id,title,status,messages,brief,results,error,created_at,updated_at")
    .eq("id", id)
    .eq("user_id", userId)
    .maybeSingle();
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
  if (cErr) throw new Error(cErr.message);
  if ((count ?? 0) >= MAX_SEARCHES_PER_DAY) {
    throw new UserError("You have started a lot of searches today. Please try again tomorrow.", 429);
  }
  const messages: Msg[] = [
    {
      role: "assistant",
      text: "Hi, I am Kindred. A few quick questions about your brand, then I will show you creators.",
      at: now(),
    },
    question({})!,
  ];
  const { data, error } = await admin()
    .from("brand_searches")
    .insert({ user_id: userId, messages, brief: {} })
    .select("id")
    .single();
  if (error) throw new Error(error.message);
  return data.id as string;
}

/** Saves one answer to the current question and adds the next question (or the summary). */
export async function answer(userId: string, id: string, stepId: unknown, raw: unknown): Promise<Search> {
  const s = await getSearch(userId, id);
  if (!s) throw new UserError("Search not found.", 404);
  if (s.status !== "chatting") throw new UserError("This chat is already finished.", 409);
  if (s.messages.length >= MAX_MESSAGES) throw new UserError("This chat is too long. Start a new search.", 409);

  const draft: Draft = { ...(s.brief ?? {}) };
  const step = nextStep(draft);
  if (!step || step.id !== stepId) throw new UserError("That question was already answered. Refresh the page.", 409);

  let parsed;
  try {
    parsed = parseAnswer(STEP_BY_ID[step.id], raw);
  } catch (e) {
    const msg = e instanceof Error && "issues" in e ? (e as { issues: { message: string }[] }).issues[0]?.message : (e as Error).message;
    throw new UserError(msg || "That answer did not look right.");
  }
  (draft as Record<string, unknown>)[step.id] = parsed.value;

  const messages = [...s.messages, { role: "user" as const, step: step.id, text: parsed.label, at: now() }];
  const next = question(draft);
  let status: Status = "chatting";
  if (next) messages.push(next);
  else {
    status = "ready";
    messages.push({ role: "assistant", text: "Thanks. Here is what I understood. Change anything you like, then see the creators.", at: now() });
  }

  const { data, error } = await admin()
    .from("brand_searches")
    .update({ brief: draft, messages, status, title: draft.product ?? null, updated_at: now() })
    .eq("id", id)
    .eq("user_id", userId)
    .eq("status", "chatting")
    .select("id,title,status,messages,brief,results,error,created_at,updated_at")
    .single();
  if (error) throw new Error(error.message);
  return data as Search;
}

/** Validates the (possibly edited) brief and stores the creators of its category. */
export async function runSearch(userId: string, id: string, input: unknown): Promise<void> {
  const s = await getSearch(userId, id);
  if (!s) throw new UserError("Search not found.", 404);
  if (s.status === "chatting") throw new UserError("Answer the questions first.", 409);

  const parsed = BriefSchema.safeParse(input);
  if (!parsed.success) throw new UserError(parsed.error.issues[0]?.message ?? "Some answers are missing.");
  const brief: Brief = parsed.data;

  const db = admin();
  await db.from("brand_searches").update({ status: "searching", brief, title: brief.product, updated_at: now() })
    .eq("id", id).eq("user_id", userId);
  try {
    const results = await creatorsInCategory(brief.category);
    const { error } = await db
      .from("brand_searches")
      .update({ status: "done", results, error: null, updated_at: now() })
      .eq("id", id)
      .eq("user_id", userId);
    if (error) throw new Error(error.message);
  } catch (e) {
    await db.from("brand_searches").update({ status: "failed", error: "Could not load creators.", updated_at: now() })
      .eq("id", id).eq("user_id", userId);
    throw e;
  }
}

export async function deleteSearch(userId: string, id: string): Promise<void> {
  if (!UUID.test(id)) throw new UserError("Search not found.", 404);
  const { error } = await admin().from("brand_searches").delete().eq("id", id).eq("user_id", userId);
  if (error) throw new Error(error.message);
}
