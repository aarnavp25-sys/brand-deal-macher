"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { CREATOR_GENDERS, type Draft, STEPS, type Step, answeredCount, nextStep } from "@/lib/brief";
import { type Facet, countMatches } from "@/lib/filters";
import type { ChatView } from "@/lib/chat-view";

type Props = { initial: ChatView; facets: Facet[] };

export function Chat({ initial, facets }: Props) {
  const router = useRouter();
  const [view, setView] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  const step = view.status === "chatting" ? nextStep(view.brief) : null;
  const lastAssistant = [...view.messages].reverse().find((m) => m.role === "assistant");
  const suggest = step?.id === "categories" ? lastAssistant?.suggest : undefined;
  const done = answeredCount(view.brief);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [view.messages.length, busy]);

  useEffect(() => {
    if (view.status === "done") router.push(`/results/${view.id}`);
  }, [view.status, view.id, router]);

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
      if (!r.ok) throw new Error(j.error ?? "Couldn't save that. Try again?");
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
            style={{ width: `${Math.round((done / STEPS.length) * 100)}%` }}
          />
        </div>
        <span>
          {done} of {STEPS.length}
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
        {(busy || view.status === "done") && (
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
        {step && <Answer key={step.id} step={step} draft={view.brief} facets={facets} busy={busy} suggest={suggest} onSend={send} />}
      </div>
      <div ref={bottom} />
    </div>
  );
}

/* ---------------- answering the current question ---------------- */

type AnswerProps = {
  step: Step;
  draft: Draft;
  facets: Facet[];
  busy: boolean;
  suggest?: string;
  onSend: (v: unknown) => void;
};

function Answer(props: AnswerProps) {
  if (props.step.kind === "text") return <TextAnswer {...props} />;
  if (props.step.kind === "single") return <SingleAnswer {...props} />;
  if (props.step.kind === "multi") return <CategoryAnswer {...props} />;
  return <CreatorAnswer {...props} />;
}

function TextAnswer({ step, busy, onSend }: AnswerProps) {
  const [text, setText] = useState("");
  const max = step.max ?? 160;
  const submit = () => text.trim() && onSend(text.trim());
  return (
    <form
      className="card p-3 focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-accent"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
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
            submit();
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

function MatchLine({ n }: { n: number }) {
  return (
    <p className="mt-4 text-sm" aria-live="polite">
      <span className="font-semibold">{n} creators</span> <span className="text-muted">match so far</span>
      {n === 0 && <span className="block text-accent-text">Nobody matches this combo yet. Try fewer filters.</span>}
    </p>
  );
}

function SingleAnswer({ step, draft, facets, busy, onSend }: AnswerProps) {
  return (
    <div>
      <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
        {step.options!.map((o) => {
          const n = countMatches(facets, { ...draft, [step.id]: o.value });
          return (
            <button key={o.value} type="button" disabled={busy || n === 0} onClick={() => onSend(o.value)} className="chip disabled:opacity-40">
              {o.label}
              <span className="ml-1.5 opacity-70">{n}</span>
            </button>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-muted">Numbers show how many creators you would see with each answer.</p>
    </div>
  );
}

function CategoryAnswer({ step, draft, facets, busy, suggest, onSend }: AnswerProps) {
  const any = step.anyValue!;
  const [picked, setPicked] = useState<string[]>(suggest ? [suggest] : []);
  const counts = useMemo(
    () =>
      Object.fromEntries(
        step.options!.map((o) => [
          o.value,
          o.value === any ? countMatches(facets, { ...draft, categories: [] }) : countMatches(facets, { ...draft, categories: [o.value] as never }),
        ]),
      ) as Record<string, number>,
    [step, draft, facets, any],
  );
  const ordered = useMemo(() => {
    const cats = step.options!.filter((o) => o.value !== any);
    cats.sort((a, b) => (a.value === suggest ? -1 : b.value === suggest ? 1 : counts[b.value] - counts[a.value]));
    return [...cats, step.options!.find((o) => o.value === any)!];
  }, [step, suggest, counts, any]);

  const toggle = (v: string) => {
    if (v === any) return setPicked(picked.includes(any) ? [] : [any]);
    const rest = picked.filter((p) => p !== any);
    setPicked(rest.includes(v) ? rest.filter((p) => p !== v) : [...rest, v]);
  };
  const live = picked.includes(any)
    ? counts[any]
    : picked.length
      ? countMatches(facets, { ...draft, categories: picked as never })
      : 0;

  return (
    <div>
      <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
        {ordered.map((o) => (
          <button
            key={o.value}
            type="button"
            aria-pressed={picked.includes(o.value)}
            disabled={counts[o.value] === 0}
            onClick={() => toggle(o.value)}
            className="chip disabled:opacity-40"
          >
            {o.label}
            <span className="ml-1.5 opacity-70">{counts[o.value]}</span>
          </button>
        ))}
      </div>
      <MatchLine n={live} />
      <button type="button" disabled={busy || live === 0} onClick={() => onSend(picked)} className="btn btn-primary mt-4 h-11 px-6">
        Continue
      </button>
    </div>
  );
}

function CreatorAnswer({ step, draft, facets, busy, onSend }: AnswerProps) {
  const any = step.anyValue!;
  const [gender, setGender] = useState<string | null>(null);
  const [langs, setLangs] = useState<string[]>([any]);
  const toggle = (v: string) => {
    if (v === any) return setLangs([any]);
    const rest = langs.filter((p) => p !== any);
    const next = rest.includes(v) ? rest.filter((p) => p !== v) : [...rest, v];
    setLangs(next.length ? next : [any]);
  };
  const live = countMatches(facets, {
    ...draft,
    creator_gender: (gender ?? "any") as Draft["creator_gender"],
    languages: langs.includes(any) ? [] : langs,
  });

  return (
    <div className="card grid gap-6 p-5 md:p-6">
      <fieldset>
        <legend className="mb-3 text-sm font-semibold">Creator</legend>
        <div className="flex flex-wrap gap-2">
          {CREATOR_GENDERS.map((o) => (
            <button key={o.value} type="button" aria-pressed={gender === o.value} onClick={() => setGender(o.value)} className="chip">
              {o.label}
            </button>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend className="mb-3 text-sm font-semibold">Language</legend>
        <div className="flex flex-wrap gap-2">
          {step.options!.map((o) => (
            <button key={o.value} type="button" aria-pressed={langs.includes(o.value)} onClick={() => toggle(o.value)} className="chip">
              {o.label}
            </button>
          ))}
        </div>
        <p className="mt-3 text-xs text-muted">Creators whose reels have no talking (music only) show up for every language.</p>
      </fieldset>
      <div>
        <MatchLine n={live} />
        <button
          type="button"
          disabled={busy || !gender || live === 0}
          onClick={() => onSend({ creator_gender: gender, languages: langs })}
          className="btn btn-primary mt-4 h-12 px-7 text-base"
        >
          Find my creators
        </button>
        {!gender && <p className="mt-2 text-xs text-muted">Pick female, male or either first.</p>}
      </div>
    </div>
  );
}
