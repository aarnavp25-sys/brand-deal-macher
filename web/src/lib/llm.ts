import "server-only";
import { admin } from "@/lib/supabase/admin";

/*
  The website's only door to an LLM: Claude Haiku 5.5 through OpenRouter (chosen 2026-11-20 on a 20-creator test,
  re-checked 2026-11-26: cheapest model with strict JSON output, $0.10 / $0.50 per million tokens).

  Guards (lessons from 2026-11-20, when an exhausted budget silently produced wrong results):
  - LLM_ENABLED=false turns every AI step off at once; callers then fall back and say so on the page.
  - A site-wide TOTAL spend cap (LLM_TOTAL_CAP_USD, default $1; user, 2026-11-26: "us pe $1 ka cap rakhna"), summed
    from llm_calls (every call ever, tests included) before every call and before a new search starts. A search costs
    about $0.0055, so it stops one search's worth (CAP_MARGIN) early instead of overshooting.
  - Strict JSON schema answers only; one retry on network/5xx; 30 s timeout; every call logged with its real cost.
*/

export const MODEL = "anthropic/claude-haiku-5.5";
// Haiku 5.5 endpoints that enforce strict JSON schemas (same list as pipeline/llm_classify.py, checked 2026-11-20)
const PROVIDERS = ["anthropic", "azure", "google-vertex"];

export class LLMUnavailable extends Error {}

export function llmEnabled(): boolean {
  return process.env.LLM_ENABLED !== "false" && Boolean(process.env.OPENROUTER_API_KEY);
}

const CAP_MARGIN = 0.01;

export function totalCap(): number {
  const n = Number(process.env.LLM_TOTAL_CAP_USD ?? "1");
  return Number.isFinite(n) && n >= 0 ? n : 1;
}

/** Everything the site's AI has ever spent, USD (real costs from OpenRouter, logged in llm_calls). */
export async function spentTotal(): Promise<number> {
  const { data, error } = await admin().from("llm_calls").select("cost").limit(100000);
  if (error) throw new LLMUnavailable(`spend check failed: ${error.message}`);
  return (data ?? []).reduce((a, r) => a + Number(r.cost ?? 0), 0);
}

/** True when the total AI budget is used up (or cannot be checked): new searches must not start. */
export async function budgetReached(): Promise<boolean> {
  try {
    return (await spentTotal()) >= totalCap() - CAP_MARGIN;
  } catch {
    return true;
  }
}

type Call = {
  kind: "product" | "review";
  system: string;
  user: string;
  schemaName: string;
  schema: Record<string, unknown>;
  maxTokens: number;
  userId?: string | null;
  searchId?: string | null;
};

async function log(c: Call, ok: boolean, cost: number, tin?: number, tout?: number) {
  await admin()
    .from("llm_calls")
    .insert({ kind: c.kind, ok, cost, tokens_in: tin ?? null, tokens_out: tout ?? null, user_id: c.userId ?? null, search_id: c.searchId ?? null });
}

/** One structured call. Returns the parsed JSON object, or throws LLMUnavailable. */
export async function callJSON<T>(c: Call): Promise<T> {
  if (!llmEnabled()) throw new LLMUnavailable("AI is switched off");
  if (await budgetReached()) throw new LLMUnavailable("AI budget used up");

  const body = {
    model: MODEL,
    max_tokens: c.maxTokens,
    reasoning: { enabled: false }, // Haiku 5.5 thinks by default; thinking tokens bill as output
    messages: [
      { role: "system", content: [{ type: "text", text: c.system, cache_control: { type: "ephemeral" } }] },
      { role: "user", content: c.user },
    ],
    response_format: { type: "json_schema", json_schema: { name: c.schemaName, strict: true, schema: c.schema } },
    provider: { require_parameters: true, only: PROVIDERS, order: PROVIDERS },
    usage: { include: true },
  };

  let lastErr = "";
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const r = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(30_000),
      });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) {
        lastErr = `HTTP ${r.status}: ${JSON.stringify(j).slice(0, 200)}`;
        if (r.status < 500 && r.status !== 429) break; // bad request, no credit, workspace budget: do not retry
        continue;
      }
      const u = j.usage ?? {};
      const text: string = j.choices?.[0]?.message?.content ?? "";
      try {
        const out = JSON.parse(text) as T;
        await log(c, true, Number(u.cost ?? 0), u.prompt_tokens, u.completion_tokens);
        return out;
      } catch {
        await log(c, false, Number(u.cost ?? 0), u.prompt_tokens, u.completion_tokens);
        lastErr = "answer was not valid JSON";
      }
    } catch (e) {
      lastErr = (e as Error).message;
    }
  }
  await log(c, false, 0);
  console.error(`LLM ${c.kind} failed: ${lastErr}`);
  throw new LLMUnavailable(lastErr);
}
