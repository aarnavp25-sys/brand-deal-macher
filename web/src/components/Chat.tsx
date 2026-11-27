"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { CREATOR_GENDERS, type Draft, LANGUAGES, type Step, followersLabel, kFormat, nextStep } from "@/lib/brief";
import { FOLLOWERS_MAX, FOLLOWERS_MIN, FOLLOWERS_STEP, type Facet, countMatches } from "@/lib/filters";
import type { ChatView } from "@/lib/chat-view";

/*
  The "Find creators" chat. It should feel like texting, not filling a form (user, 2026-11-26):
  Kindred's lines arrive one by one after a short typing pause, the brand's own message shows at once,
  every question can be answered by tapping or by typing, and problems come back as a Kindred line, not a red error.
*/

type Props = { initial: ChatView; facets: Facet[] };
type Send = (value: unknown, label: string) => void;

const reduceMotion = () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function Chat({ initial, facets }: Props) {
  const router = useRouter();
  const [view, setView] = useState(initial);
  // A brand-new chat plays Kindred's opening lines; a reopened chat shows its history at once.
  const [shown, setShown] = useState(initial.messages.some((m) => m.role === "user") ? initial.messages.length : 0);
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  const revealing = shown < view.messages.length;
  const step = view.status === "chatting" && !revealing ? nextStep(view.brief) : null;
  const lastAssistant = [...view.messages].reverse().find((m) => m.role === "assistant");
  const suggest = step?.id === "categories" ? lastAssistant?.suggest : undefined;
  const suggests = step?.id === "categories" ? (lastAssistant?.suggests ?? (suggest ? [suggest] : [])) : [];
  const visible = view.messages.slice(0, shown);
  const typing = busy || revealing || (view.status === "done" && !revealing);

  // Reveal Kindred's new lines one at a time, with a typing pause that grows a little with the line's length.
  useEffect(() => {
    if (!revealing) return;
    const next = view.messages[shown];
    const delay = next.role === "user" || reduceMotion() ? 0 : Math.min(500 + next.text.length * 11, 1400);
    const t = setTimeout(() => setShown((n) => n + 1), delay);
    return () => clearTimeout(t);
  }, [revealing, shown, view.messages]);

  useEffect(() => {
    if (view.status === "done" && !revealing) {
      const t = setTimeout(() => router.push(`/results/${view.id}`), reduceMotion() ? 0 : 700);
      return () => clearTimeout(t);
    }
  }, [view.status, view.id, revealing, router]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: reduceMotion() ? "auto" : "smooth", block: "end" });
  }, [shown, pending, note, step?.id]);

  const send: Send = async (value, label) => {
    if (!step || busy) return;
    setBusy(true);
    setNote(null);
    setPending(label);
    try {
      const r = await fetch(`/api/searches/${view.id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: step.id, value }),
      });
      const j = await r.json().catch(() => ({}));
      if (r.status === 401) return router.replace(`/login?next=/find/${view.id}`);
      if (!r.ok) throw new Error(j.error ?? "Hmm, that didn't go through. Try again?");
      const before = view.messages.length;
      setView(j as ChatView);
      setShown(before + 1); // the brand's own message shows at once; Kindred's lines follow one by one
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setPending(null);
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      <ol className="grid gap-1.5" aria-live="polite">
        {visible.map((m, i) => {
          const nextMsg = visible[i + 1];
          const lastOfGroup = !nextMsg || nextMsg.role !== m.role;
          const firstOfGroup = i === 0 || visible[i - 1].role !== m.role;
          return m.role === "assistant" ? (
            <Kindred key={i} text={m.text} avatar={lastOfGroup && !(typing && i === visible.length - 1)} gap={firstOfGroup && i > 0} />
          ) : (
            <Me key={i} text={m.text} gap={firstOfGroup} />
          );
        })}
        {pending && <Me text={pending} gap />}
        {note && <Kindred text={note} avatar gap />}
        {typing && !note && (
          <li className="mt-3 flex items-center gap-2.5" aria-label="Kindred is typing">
            <Mark />
            <span className="typing flex gap-1 rounded-2xl rounded-bl-md bg-surface px-4 py-4" style={{ border: "1px solid var(--line)" }}>
              <span className="size-1.5 rounded-full bg-muted" />
              <span className="size-1.5 rounded-full bg-muted" />
              <span className="size-1.5 rounded-full bg-muted" />
            </span>
          </li>
        )}
      </ol>

      {step && !busy && (
        <div className="rise mt-6">
          <Answer key={step.id} step={step} draft={view.brief} facets={facets} suggest={suggest} suggests={suggests} onSend={send} />
        </div>
      )}
      <div ref={bottom} className="h-4" />
    </div>
  );
}

function Mark() {
  return (
    <span className="story-ring inline-block size-7 shrink-0" aria-hidden>
      <span className="block size-full bg-accent" />
    </span>
  );
}

function Kindred({ text, avatar, gap }: { text: string; avatar: boolean; gap: boolean }) {
  return (
    <li className={`rise flex max-w-[88%] items-end gap-2.5 ${gap ? "mt-3" : ""}`}>
      {avatar ? <Mark /> : <span className="inline-block size-7 shrink-0" aria-hidden />}
      <p className="rounded-2xl rounded-bl-md bg-surface px-4 py-2.5 leading-relaxed" style={{ border: "1px solid var(--line)" }}>
        <span className="sr-only">Kindred: </span>
        {text}
      </p>
    </li>
  );
}

function Me({ text, gap }: { text: string; gap: boolean }) {
  return (
    <li className={`rise max-w-[85%] justify-self-end ${gap ? "mt-3" : ""}`}>
      <p className="whitespace-pre-wrap rounded-2xl rounded-br-md bg-ink px-4 py-2.5 leading-relaxed text-bg">
        <span className="sr-only">You: </span>
        {text}
      </p>
    </li>
  );
}

/* ---------------- replying ---------------- */

type AnswerProps = { step: Step; draft: Draft; facets: Facet[]; suggest?: string; suggests?: string[]; onSend: Send };

function Answer(props: AnswerProps) {
  if (props.step.kind === "text") return <Composer step={props.step} onSend={(t) => props.onSend(t, t)} big={props.step.id === "about" || props.step.id === "more"} />;
  if (props.step.kind === "choice") return <ChoiceAnswer {...props} />;
  if (props.step.kind === "single") return <BuyerAnswer {...props} />;
  if (props.step.kind === "multi") return <CategoryAnswer {...props} />;
  if (props.step.kind === "range") return <RangeAnswer {...props} />;
  return <CreatorAnswer {...props} />;
}

/** The message box. On choice questions it is the "or just type it" option. */
function Composer({ step, onSend, big = false, placeholder }: { step: Step; onSend: (t: string) => void; big?: boolean; placeholder?: string }) {
  const [text, setText] = useState("");
  const max = step.max ?? 300;
  const submit = () => {
    const t = text.trim();
    if (t.length >= 2) onSend(t);
  };
  return (
    <form
      className="flex items-end gap-2 rounded-[22px] border border-line bg-surface p-2 pl-4 shadow-[var(--shadow)] focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-accent"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <label htmlFor={`msg-${step.id}`} className="sr-only">
        Your reply
      </label>
      <textarea
        id={`msg-${step.id}`}
        autoFocus={step.kind === "text"}
        rows={big ? 3 : 1}
        maxLength={max}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        placeholder={placeholder ?? step.placeholder ?? "Type a message"}
        className="composer-input max-h-40 min-h-10 flex-1 resize-none bg-transparent py-2 text-base text-ink placeholder:text-muted"
      />
      <button type="submit" disabled={text.trim().length < 2} className="btn btn-primary h-10 shrink-0 px-5 text-sm" aria-label="Send">
        Send
      </button>
    </form>
  );
}

function Fit({ n }: { n: number }) {
  return (
    <p className="mt-3 text-sm text-muted" aria-live="polite">
      {n === 0 ? (
        <span className="text-accent-text">Nobody fits this combo yet. Try loosening something.</span>
      ) : (
        <>
          <span className="font-semibold text-ink">{n} creators</span> fit so far
        </>
      )}
    </p>
  );
}

/** Two plain options: "Is this what you mean?" (Yes / No) and "a particular product or your brand in general?". */
function ChoiceAnswer({ step, onSend }: AnswerProps) {
  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
      {step.options!.map((o, i) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onSend(o.value, o.label)}
          className={i === 0 ? "btn btn-primary h-11 px-5 text-sm" : "btn btn-ghost h-11 px-5 text-sm"}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/**
 * Follower range with two handles, like a shop filter (user, 2026-11-27: "dono side se ... scroll karke kam-jyada").
 * Two native range inputs on one track, so both handles work with mouse, touch and arrow keys. The live count uses
 * the same filter as the results.
 */
function RangeAnswer({ step, draft, facets, onSend }: AnswerProps) {
  const [min, setMin] = useState(draft.followers_min ?? FOLLOWERS_MIN);
  const [max, setMax] = useState(draft.followers_max ?? FOLLOWERS_MAX);
  const n = useMemo(() => countMatches(facets, { ...draft, followers_min: min, followers_max: max }), [facets, draft, min, max]);
  const pct = (v: number) => ((v - FOLLOWERS_MIN) / (FOLLOWERS_MAX - FOLLOWERS_MIN)) * 100;
  return (
    <div className="grid gap-3">
      <div className="rounded-[22px] border border-line bg-surface p-5 shadow-[var(--shadow)]">
        <div className="flex items-baseline justify-between gap-3">
          <p className="display text-2xl font-extrabold tabular-nums" aria-live="polite">
            {kFormat(min)} – {kFormat(max)}
          </p>
          <p className="text-sm text-muted">{followersLabel(min, max)}</p>
        </div>
        <div className="range2 relative mt-5 h-8" role="group" aria-label={step.question}>
          <div className="absolute inset-x-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-surface-2" />
          <div
            className="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-accent"
            style={{ left: `${pct(min)}%`, width: `${pct(max) - pct(min)}%` }}
          />
          <input
            type="range"
            aria-label="Minimum followers"
            aria-valuetext={`${kFormat(min)} followers`}
            min={FOLLOWERS_MIN}
            max={FOLLOWERS_MAX}
            step={FOLLOWERS_STEP}
            value={min}
            onChange={(e) => setMin(Math.min(Number(e.target.value), max - FOLLOWERS_STEP))}
            style={{ zIndex: min > FOLLOWERS_MAX - 2 * FOLLOWERS_STEP ? 4 : 3 }}
          />
          <input
            type="range"
            aria-label="Maximum followers"
            aria-valuetext={`${kFormat(max)} followers`}
            min={FOLLOWERS_MIN}
            max={FOLLOWERS_MAX}
            step={FOLLOWERS_STEP}
            value={max}
            onChange={(e) => setMax(Math.max(Number(e.target.value), min + FOLLOWERS_STEP))}
          />
        </div>
        <div className="mt-1 flex justify-between text-xs text-muted">
          <span>10K</span>
          <span>100K</span>
        </div>
        <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
          <Fit n={n} />
          <button
            type="button"
            disabled={n === 0}
            onClick={() => onSend({ min, max }, followersLabel(min, max))}
            className="btn btn-primary h-11 px-6 text-sm"
          >
            Continue
          </button>
        </div>
      </div>
      <Composer step={step} placeholder="Or type it, like “20k to 50k”" onSend={(t) => onSend({ text: t }, t)} />
    </div>
  );
}

function BuyerAnswer({ step, draft, facets, onSend }: AnswerProps) {
  return (
    <div className="grid gap-3">
      <div className="flex flex-wrap gap-2" role="group" aria-label={step.question}>
        {step.options!.map((o) => {
          const n = countMatches(facets, { ...draft, [step.id]: o.value });
          return (
            <button key={o.value} type="button" disabled={n === 0} onClick={() => onSend(o.value, o.label)} className="chip disabled:opacity-40">
              {o.label}
              <span className="ml-1.5 opacity-60">{n}</span>
            </button>
          );
        })}
      </div>
      <Composer step={step} placeholder="Or just type it, like “mostly girls in college”" onSend={(t) => onSend({ text: t }, t)} />
    </div>
  );
}

function CategoryAnswer({ step, draft, facets, suggest, suggests = [], onSend }: AnswerProps) {
  const any = step.anyValue!;
  const [picked, setPicked] = useState<string[]>(suggests.length ? suggests : suggest ? [suggest] : []);
  const counts = useMemo(
    () =>
      Object.fromEntries(
        step.options!.map((o) => [
          o.value,
          countMatches(facets, { ...draft, categories: o.value === any ? [] : ([o.value] as never) }),
        ]),
      ) as Record<string, number>,
    [step, draft, facets, any],
  );
  const ordered = useMemo(() => {
    const cats = step.options!.filter((o) => o.value !== any);
    const rank = (v: string) => (suggests.includes(v) ? suggests.indexOf(v) : v === suggest ? 0 : 99);
    cats.sort((a, b) => rank(a.value) - rank(b.value) || counts[b.value] - counts[a.value]);
    return [...cats, step.options!.find((o) => o.value === any)!];
  }, [step, suggest, suggests, counts, any]);

  const toggle = (v: string) => {
    if (v === any) return setPicked(picked.includes(any) ? [] : [any]);
    const rest = picked.filter((p) => p !== any);
    setPicked(rest.includes(v) ? rest.filter((p) => p !== v) : [...rest, v]);
  };
  const live = picked.includes(any) ? counts[any] : picked.length ? countMatches(facets, { ...draft, categories: picked as never }) : 0;
  const label = picked.includes(any) ? "All of them" : picked.join(", ");

  return (
    <div className="grid gap-3">
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
            <span className="ml-1.5 opacity-60">{counts[o.value]}</span>
          </button>
        ))}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Fit n={live} />
        <button type="button" disabled={live === 0} onClick={() => onSend(picked, label)} className="btn btn-primary h-10 px-5 text-sm">
          Lock these in
        </button>
      </div>
      <Composer step={step} placeholder="Or type it, like “food and lifestyle creators”" onSend={(t) => onSend({ text: t }, t)} />
    </div>
  );
}

function CreatorAnswer({ step, draft, facets, onSend }: AnswerProps) {
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
  const label = gender
    ? `${CREATOR_GENDERS.find((g) => g.value === gender)!.label}, ${langs.includes(any) ? "any language" : langs.map((l) => LANGUAGES.find((x) => x.id === l)!.label).join(", ")}`
    : "";

  return (
    <div className="grid gap-3">
      <div className="card grid gap-5 p-5">
        <div className="flex flex-wrap gap-2" role="group" aria-label="Creator">
          {CREATOR_GENDERS.map((o) => (
            <button key={o.value} type="button" aria-pressed={gender === o.value} onClick={() => setGender(o.value)} className="chip">
              {o.label}
            </button>
          ))}
        </div>
        <div>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Language">
            {step.options!.map((o) => (
              <button key={o.value} type="button" aria-pressed={langs.includes(o.value)} onClick={() => toggle(o.value)} className="chip">
                {o.label}
              </button>
            ))}
          </div>
          <p className="mt-3 text-xs text-muted">Creators whose reels have no talking (music only) show up for every language.</p>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Fit n={live} />
          <button
            type="button"
            disabled={!gender || live === 0}
            onClick={() => onSend({ creator_gender: gender, languages: langs }, label)}
            className="btn btn-primary h-11 px-6"
          >
            {gender ? "Find my creators" : "Pick female, male or either"}
          </button>
        </div>
      </div>
      <Composer step={step} placeholder="Or type it, like “female, hindi or english”" onSend={(t) => onSend({ text: t }, t)} />
    </div>
  );
}
