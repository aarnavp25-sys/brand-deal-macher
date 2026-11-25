"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { type Brief, type Draft, type Step, STEPS, STEP_BY_ID, nextStep } from "@/lib/brief";
import type { ChatView } from "@/lib/chat-view";

type Props = { initial: ChatView; counts: Record<string, number> };

export function Chat({ initial, counts }: Props) {
  const router = useRouter();
  const [view, setView] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  const step = view.status === "chatting" ? nextStep(view.brief) : null;
  const lastAssistant = [...view.messages].reverse().find((m) => m.role === "assistant");
  const suggest = step?.id === "category" ? lastAssistant?.suggest : undefined;
  const answered = STEPS.filter((s) => view.brief[s.id] !== undefined).length;

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [view.messages.length, busy]);

  async function send(value: unknown) {
    if (!step || busy) return;
    setBusy(true);
    setError(null);
    try {
      const r = await fetch(`/api/searches/${view.id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: step.id, value }),
      });
      const j = await r.json().catch(() => ({}));
      if (r.status === 401) return router.replace(`/login?next=/find/${view.id}`);
      if (!r.ok) throw new Error(j.error ?? "Could not save that answer.");
      setView(j as ChatView);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center gap-3 text-sm text-muted">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full" style={{ background: "var(--line)" }}>
          <div
            className="h-full rounded-full bg-accent transition-[width] duration-500"
            style={{ width: `${Math.round((answered / STEPS.length) * 100)}%` }}
          />
        </div>
        <span>
          {answered} of {STEPS.length}
        </span>
      </div>

      <ol className="grid gap-3" aria-live="polite">
        {view.messages.map((m, i) =>
          m.role === "assistant" ? (
            <li key={i} className="rise flex max-w-[88%] items-end gap-2.5">
              <span className="story-ring mb-1 inline-block size-7 shrink-0" aria-hidden>
                <span className="block size-full bg-accent" />
              </span>
              <p className="rounded-2xl rounded-bl-md bg-surface px-4 py-3 leading-relaxed" style={{ border: "1px solid var(--line)" }}>
                <span className="sr-only">Kindred: </span>
                {m.text}
              </p>
            </li>
          ) : (
            <li key={i} className="rise max-w-[85%] justify-self-end">
              <p className="whitespace-pre-wrap rounded-2xl rounded-br-md bg-ink px-4 py-3 leading-relaxed text-bg">
                <span className="sr-only">You: </span>
                {m.text}
              </p>
            </li>
          ),
        )}
        {busy && (
          <li className="flex items-center gap-2.5" aria-label="Kindred is typing">
            <span className="story-ring inline-block size-7" aria-hidden>
              <span className="block size-full bg-accent" />
            </span>
            <span className="typing flex gap-1 rounded-2xl bg-surface px-4 py-4" style={{ border: "1px solid var(--line)" }}>
              <span className="size-1.5 rounded-full bg-muted" />
              <span className="size-1.5 rounded-full bg-muted" />
              <span className="size-1.5 rounded-full bg-muted" />
            </span>
          </li>
        )}
      </ol>

      <div className="mt-6">
        {error && (
          <p role="alert" className="mb-3 text-sm text-accent-text">
            {error}
          </p>
        )}
        {step && <Answer key={step.id} step={step} busy={busy} counts={counts} suggest={suggest} onSend={send} />}
        {!step && view.status !== "chatting" && view.status !== "done" && (
          <BriefCard id={view.id} brief={view.brief} counts={counts} />
        )}
      </div>
      <div ref={bottom} />
    </div>
  );
}

/* ---------------- answering the current question ---------------- */

function Answer({
  step,
  busy,
  counts,
  suggest,
  onSend,
}: {
  step: Step;
  busy: boolean;
  counts: Record<string, number>;
  suggest?: string;
  onSend: (v: unknown) => void;
}) {
  const [text, setText] = useState("");
  const [picked, setPicked] = useState<string[]>([]);
  const max = step.id === "about" ? 1500 : 160;

  if (step.kind === "text") {
    return (
      <form
        className="card p-3 focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-accent"
        onSubmit={(e) => {
          e.preventDefault();
          if (text.trim()) onSend(text.trim());
        }}
      >
        <label htmlFor="answer" className="sr-only">
          {step.question}
        </label>
        <textarea
          id="answer"
          autoFocus
          rows={step.id === "about" ? 4 : 2}
          maxLength={max}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (text.trim()) onSend(text.trim());
            }
          }}
          placeholder={step.placeholder}
          className="w-full resize-none bg-transparent px-2 py-2 text-base text-ink placeholder:text-muted focus:outline-none"
        />
        <div className="flex items-center justify-between gap-3 px-2 pt-1">
          <span className="text-xs text-muted">
            {text.length}/{max}. Enter to send, Shift + Enter for a new line.
          </span>
          <button type="submit" disabled={busy || text.trim().length < 2} className="btn btn-primary h-10 px-5 text-sm">
            Send
          </button>
        </div>
      </form>
    );
  }

  const options = step.options ?? [];
  const ordered =
    step.id === "category"
      ? [...options].sort((a, b) => (a.value === suggest ? -1 : b.value === suggest ? 1 : (counts[b.value] ?? 0) - (counts[a.value] ?? 0)))
      : options;

  if (step.kind === "single") {
    return (
      <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
        {ordered.map((o) => {
          const n = step.id === "category" ? counts[o.value] ?? 0 : null;
          return (
            <button
              key={o.value}
              type="button"
              disabled={busy || n === 0}
              onClick={() => onSend(o.value)}
              className="chip disabled:opacity-40"
              style={o.value === suggest ? { borderColor: "var(--accent)", background: "var(--accent-soft)" } : undefined}
            >
              {o.label}
              {n != null && <span className="ml-1.5 text-muted">{n}</span>}
              {o.value === suggest && <span className="ml-1.5 font-semibold text-accent-text">Suggested</span>}
            </button>
          );
        })}
      </div>
    );
  }

  const toggle = (v: string) => {
    if (v === step.anyValue) return setPicked(picked.includes(v) ? [] : [v]);
    const rest = picked.filter((p) => p !== step.anyValue);
    setPicked(rest.includes(v) ? rest.filter((p) => p !== v) : [...rest, v]);
  };
  return (
    <div>
      <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
        {ordered.map((o) => (
          <button key={o.value} type="button" aria-pressed={picked.includes(o.value)} onClick={() => toggle(o.value)} className="chip">
            {o.label}
          </button>
        ))}
      </div>
      <button
        type="button"
        disabled={busy || picked.length === 0}
        onClick={() => onSend(picked)}
        className="btn btn-primary mt-4 h-11 px-6"
      >
        Continue
      </button>
    </div>
  );
}

/* ---------------- summary card: edit anything, then search ---------------- */

function BriefCard({ id, brief, counts }: { id: string; brief: Draft; counts: Record<string, number> }) {
  const router = useRouter();
  const [b, setB] = useState<Draft>(brief);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = <K extends keyof Brief>(k: K, v: Brief[K]) => setB((x) => ({ ...x, [k]: v }));

  async function run() {
    setBusy(true);
    setError(null);
    try {
      const r = await fetch(`/api/searches/${id}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brief: b }),
      });
      const j = await r.json().catch(() => ({}));
      if (r.status === 401) return router.replace(`/login?next=/find/${id}`);
      if (!r.ok) throw new Error(j.error ?? "Could not load creators.");
      router.push(`/results/${id}`);
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  }

  return (
    <section className="card rise p-6 md:p-8" aria-labelledby="brief-title">
      <h2 id="brief-title" className="display text-2xl font-bold">
        Your brief
      </h2>
      <div className="mt-6 grid gap-5">
        <TextField label="About your brand" value={b.about ?? ""} rows={3} max={1500} onChange={(v) => set("about", v)} />
        <TextField label="Product to promote" value={b.product ?? ""} rows={1} max={160} onChange={(v) => set("product", v)} />
        <SelectField
          label="Category"
          help="You will see every creator whose main content is in this category."
          step={STEP_BY_ID.category}
          value={b.category ?? ""}
          counts={counts}
          onChange={(v) => set("category", v as Brief["category"])}
        />
        <div className="grid gap-5 sm:grid-cols-2">
          <SelectField label="Who buys it" step={STEP_BY_ID.customer_gender} value={b.customer_gender ?? ""} onChange={(v) => set("customer_gender", v as Brief["customer_gender"])} />
          <SelectField label="Creator" step={STEP_BY_ID.creator_gender} value={b.creator_gender ?? ""} onChange={(v) => set("creator_gender", v as Brief["creator_gender"])} />
          <SelectField label="Creator size" step={STEP_BY_ID.size} value={b.size ?? ""} onChange={(v) => set("size", v as Brief["size"])} />
          <SelectField label="Goal" step={STEP_BY_ID.goal} value={b.goal ?? ""} onChange={(v) => set("goal", v as Brief["goal"])} />
        </div>
        <MultiField label="Buyer ages" step={STEP_BY_ID.customer_ages} value={b.customer_ages ?? []} onChange={(v) => set("customer_ages", v as Brief["customer_ages"])} />
        <MultiField label="Languages" step={STEP_BY_ID.languages} value={b.languages ?? []} onChange={(v) => set("languages", v)} />
        <MultiField label="Video styles" step={STEP_BY_ID.styles} value={b.styles ?? []} onChange={(v) => set("styles", v)} />
      </div>
      <p className="mt-6 rounded-[12px] bg-surface-2 p-4 text-sm leading-relaxed text-muted">
        For now Kindred shows every creator in your category. Your other answers are saved and will be used to rank
        creators soon.
      </p>
      {error && (
        <p role="alert" className="mt-4 text-sm text-accent-text">
          {error}
        </p>
      )}
      <button type="button" onClick={run} disabled={busy} className="btn btn-primary mt-6 h-12 px-7 text-base">
        {busy ? "Loading creators..." : "Show creators"}
      </button>
    </section>
  );
}

function TextField({ label, value, rows, max, onChange }: { label: string; value: string; rows: number; max: number; onChange: (v: string) => void }) {
  const id = label.toLowerCase().replace(/\W+/g, "-");
  return (
    <div className="grid gap-2">
      <label htmlFor={id} className="text-sm font-semibold">
        {label}
      </label>
      <textarea id={id} rows={rows} maxLength={max} value={value} onChange={(e) => onChange(e.target.value)} className="field resize-y px-3 py-2.5" />
    </div>
  );
}

function SelectField({
  label,
  help,
  step,
  value,
  counts,
  onChange,
}: {
  label: string;
  help?: string;
  step: Step;
  value: string;
  counts?: Record<string, number>;
  onChange: (v: string) => void;
}) {
  const id = `f-${step.id}`;
  return (
    <div className="grid min-w-0 gap-2">
      <label htmlFor={id} className="text-sm font-semibold">
        {label}
      </label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)} className="field h-11 w-full min-w-0 px-3">
        {(step.options ?? []).map((o) => (
          <option key={o.value} value={o.value} disabled={counts ? (counts[o.value] ?? 0) === 0 : false}>
            {o.label}
            {counts ? ` (${counts[o.value] ?? 0})` : ""}
          </option>
        ))}
      </select>
      {help && <p className="text-xs text-muted">{help}</p>}
    </div>
  );
}

function MultiField({ label, step, value, onChange }: { label: string; step: Step; value: string[]; onChange: (v: string[]) => void }) {
  const any = step.anyValue!;
  const isAny = value.length === 0;
  const toggle = (v: string) => {
    if (v === any) return onChange([]);
    onChange(value.includes(v) ? value.filter((x) => x !== v) : [...value, v]);
  };
  return (
    <fieldset className="grid gap-2">
      <legend className="mb-2 text-sm font-semibold">{label}</legend>
      <div className="flex flex-wrap gap-2">
        {(step.options ?? []).map((o) => (
          <button
            key={o.value}
            type="button"
            aria-pressed={o.value === any ? isAny : value.includes(o.value)}
            onClick={() => toggle(o.value)}
            className="chip"
          >
            {o.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}
