import Link from "next/link";
import { Logo } from "@/components/Logo";
import { categoryCounts } from "@/lib/matching";
import { CATEGORIES } from "@/lib/brief";

// Real numbers from the creator database, refreshed at most once an hour.
export const revalidate = 3600;

async function stats() {
  try {
    const counts = await categoryCounts();
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    const top = CATEGORIES.map((c) => ({ c, n: counts[c] ?? 0 }))
      .filter((x) => x.n > 0)
      .sort((a, b) => b.n - a.n);
    return { total, categories: top.length, top, food: counts["Food & Beverages"] ?? 0 };
  } catch {
    return null;
  }
}

export default async function Home() {
  const s = await stats();

  return (
    <div className="min-h-[100dvh]">
      <header className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 md:px-8">
        <Logo />
        <Link href="/login" prefetch={false} className="btn btn-ghost h-10 px-5 text-sm">
          Sign in
        </Link>
      </header>

      {/* Hero: message left, a real piece of the product right */}
      <section className="mx-auto grid max-w-6xl items-center gap-12 px-5 pb-20 pt-10 md:grid-cols-[1.1fr_1fr] md:px-8 md:pt-16">
        <div>
          <h1 className="display rise text-4xl font-extrabold md:text-[2.6rem] lg:text-[3.2rem]">
            Find creators who already talk to your buyers.
          </h1>
          <p className="rise mt-6 max-w-[46ch] text-lg leading-relaxed text-muted" style={{ ["--i" as string]: 1 }}>
            Answer a few questions about your brand. See creators with 10K to 100K followers who post in your category.
          </p>
          <div className="rise mt-9 flex flex-wrap items-center gap-3" style={{ ["--i" as string]: 2 }}>
            <Link href="/find" prefetch={false} className="btn btn-primary h-12 px-7 text-base">
              Find creators
            </Link>
            <a href="#how" className="btn btn-ghost h-12 px-6 text-base">
              How it works
            </a>
          </div>
        </div>

        <ChatPreview foodCount={s?.food ?? null} />
      </section>

      {/* How it works: one large tile and two smaller ones */}
      <section id="how" className="mx-auto max-w-6xl px-5 py-20 md:px-8">
        <h2 className="display max-w-[20ch] text-3xl font-bold md:text-4xl">Three minutes from brand to shortlist.</h2>
        <div className="mt-10 grid gap-4 md:grid-cols-[1.4fr_1fr] md:grid-rows-2">
          <div className="card flex flex-col justify-between p-7 md:row-span-2 md:p-9">
            <p className="display text-5xl font-extrabold text-accent-text md:text-6xl">Chat</p>
            <div className="mt-10">
              <p className="text-xl font-semibold">Tell us what you sell and who buys it.</p>
              <p className="mt-2 max-w-[52ch] leading-relaxed text-muted">
                Five quick questions, one at a time: your brand, the product, who buys it, the creators and the language you want. Type or tap.
              </p>
            </div>
          </div>
          <div className="card p-7" style={{ background: "var(--accent-soft)" }}>
            <p className="text-xl font-semibold">Pick your categories</p>
            <p className="mt-2 leading-relaxed text-muted">
              One, a few or all of them. We suggest one from your answers, then you choose the creator and language.
            </p>
          </div>
          <div className="card p-7">
            <p className="text-xl font-semibold">See who fits</p>
            <p className="mt-2 leading-relaxed text-muted">
              Followers, typical reel views, engagement, languages and past brand work, side by side.
            </p>
          </div>
        </div>
      </section>

      {/* What we know: real numbers from the database */}
      <section className="mx-auto max-w-6xl px-5 py-20 md:px-8">
        <h2 className="display max-w-[24ch] text-3xl font-bold md:text-4xl">
          We watch their reels so you do not have to.
        </h2>
        <p className="mt-4 max-w-[60ch] leading-relaxed text-muted">
          Every creator on Kindred was profiled from their 12 latest reels: what they make, who it is for, the
          languages they speak and whether they already work with brands.
        </p>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat value={s ? String(s.total) : "-"} label="active creators profiled" accent />
          <Stat value="12" label="recent reels watched per creator" />
          <Stat value={s ? String(s.categories) : "-"} label="content categories" />
          <Stat value="10K to 100K" label="followers, the size small brands can work with" />
        </div>
        {s && (
          <ul className="mt-8 flex flex-wrap gap-2" aria-label="Creators per category">
            {s.top.slice(0, 10).map(({ c, n }) => (
              <li key={c} className="chip">
                {c} <span className="ml-1 text-muted">{n}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mx-auto max-w-6xl px-5 pb-24 pt-10 md:px-8">
        <div className="card flex flex-col items-start gap-6 p-8 md:flex-row md:items-center md:justify-between md:p-12">
          <p className="display max-w-[22ch] text-2xl font-bold md:text-3xl">
            Start with one product. See who already makes content for it.
          </p>
          <Link href="/find" prefetch={false} className="btn btn-primary h-12 px-7 text-base">
            Find creators
          </Link>
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-8 text-sm text-muted md:flex-row md:justify-between md:px-8">
          <p>Kindred. Made for small Indian brands.</p>
          <p>Creator data comes from public Instagram profiles. Audience details are estimates.</p>
        </div>
      </footer>
    </div>
  );
}

function Stat({ value, label, accent = false }: { value: string; label: string; accent?: boolean }) {
  return (
    <div className="card p-6" style={accent ? { background: "var(--ink)", color: "var(--bg)", borderColor: "var(--ink)" } : undefined}>
      <p className="display text-4xl font-extrabold">{value}</p>
      <p className={`mt-2 text-sm leading-snug ${accent ? "opacity-75" : "text-muted"}`}>{label}</p>
    </div>
  );
}

/** A real, static rendering of the chat UI (not a screenshot), showing how a search starts. */
function ChatPreview({ foodCount }: { foodCount: number | null }) {
  return (
    <div className="card rise relative p-5 md:p-6" style={{ ["--i" as string]: 2 }} aria-label="Example of a Kindred chat">
      <div className="flex items-center gap-2 border-b border-line pb-4 text-sm text-muted">
        <span className="story-ring inline-block size-6" aria-hidden>
          <span className="block size-full bg-accent" />
        </span>
        Kindred
      </div>
      <div className="grid gap-3 pt-5 text-[15px] leading-relaxed">
        <p className="max-w-[85%] justify-self-end rounded-2xl rounded-br-md bg-ink px-4 py-2.5 text-bg">
          We make small-batch mango and lime pickles in Pune.
        </p>
        <p className="max-w-[85%] rounded-2xl rounded-bl-md bg-surface-2 px-4 py-2.5">
          Looks like Food & Beverages to me. Is that right, or is another one closer?
        </p>
        <div className="flex flex-wrap gap-2 pt-1">
          <span className="chip" aria-pressed="true">Food & Beverages</span>
          <span className="chip">Home & Household</span>
          <span className="chip">Lifestyle & Daily Vlog</span>
        </div>
        <div className="mt-3 flex items-center gap-4 rounded-2xl border border-line p-4">
          <div className="flex -space-x-3" aria-hidden>
            {["A", "R", "S", "M"].map((l, i) => (
              <span key={l} className="story-ring inline-block size-11" style={{ zIndex: 4 - i }}>
                <span className="flex size-full items-center justify-center bg-surface-2 text-sm font-bold text-muted">{l}</span>
              </span>
            ))}
          </div>
          <p className="text-sm">
            <span className="font-semibold">{foodCount ?? "Every"} food creators</span>
            <span className="block text-muted">ready to compare</span>
          </p>
        </div>
      </div>
    </div>
  );
}
