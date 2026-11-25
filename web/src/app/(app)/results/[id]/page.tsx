import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { requireBrand } from "@/lib/auth";
import { getSearch } from "@/lib/searches";
import { admin } from "@/lib/supabase/admin";
import { Results } from "@/components/Results";
import type { Results as ResultsData } from "@/lib/matching";
import { BUYERS, CREATOR_GENDERS, type Draft, LANGUAGES } from "@/lib/brief";

export const metadata: Metadata = { title: "Creators" };

/** Profile photos live in a private bucket; signed links work for one hour and only reach signed-in brands. */
async function photoLinks(usernames: string[]): Promise<Record<string, string>> {
  if (!usernames.length) return {};
  const { data } = await admin()
    .storage.from("creator-photos")
    .createSignedUrls(usernames.map((u) => `${u}.jpg`), 3600);
  const out: Record<string, string> = {};
  (data ?? []).forEach((d, i) => {
    if (d.signedUrl && !d.error) out[usernames[i]] = d.signedUrl;
  });
  return out;
}

function choices(b: Draft): string[] {
  const out: string[] = [];
  out.push(b.categories?.length ? b.categories.join(", ") : "All categories");
  if (b.customer_gender) out.push(`Buyers: ${BUYERS.find((x) => x.value === b.customer_gender)?.label.toLowerCase()}`);
  if (b.creator_gender) out.push(CREATOR_GENDERS.find((x) => x.value === b.creator_gender)!.label);
  if (b.languages) out.push(b.languages.length ? b.languages.map((l) => LANGUAGES.find((x) => x.id === l)?.label ?? l).join(", ") : "Any language");
  return out;
}

export default async function ResultsPage({ params }: PageProps<"/results/[id]">) {
  const { id } = await params;
  const brand = await requireBrand(`/results/${id}`);
  const search = await getSearch(brand.id, id);
  if (!search) notFound();
  if (search.status !== "done" || !search.results) redirect(`/find/${id}`);

  const results = search.results as ResultsData;
  const photos = await photoLinks(results.creators.map((c) => c.username));
  const brief = (search.brief ?? {}) as Draft;

  return (
    <div>
      <Link href="/dashboard" className="text-sm text-muted hover:text-ink">
        My searches
      </Link>
      <h1 className="display mt-3 text-3xl font-extrabold md:text-4xl">
        {results.creators.length} creators for {search.title}
      </h1>
      <ul className="mt-4 flex flex-wrap gap-2" aria-label="Your choices">
        {choices(brief).map((c) => (
          <li key={c} className="rounded-full border border-line px-3 py-1 text-sm text-muted">
            {c}
          </li>
        ))}
      </ul>
      <p className="mt-4 text-sm text-muted">
        Want different creators?{" "}
        <Link href="/find" className="font-semibold text-accent-text hover:underline">
          Start a new search
        </Link>
      </p>
      <Results creators={results.creators} photos={photos} />
    </div>
  );
}
