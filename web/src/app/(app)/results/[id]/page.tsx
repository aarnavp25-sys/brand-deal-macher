import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { requireBrand } from "@/lib/auth";
import { getSearch } from "@/lib/searches";
import { admin } from "@/lib/supabase/admin";
import { Results } from "@/components/Results";
import type { Results as ResultsData } from "@/lib/matching";

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

export default async function ResultsPage({ params }: PageProps<"/results/[id]">) {
  const { id } = await params;
  const brand = await requireBrand(`/results/${id}`);
  const search = await getSearch(brand.id, id);
  if (!search) notFound();
  if (search.status !== "done" || !search.results) redirect(`/find/${id}`);

  const results = search.results as ResultsData;
  const photos = await photoLinks(results.creators.map((c) => c.username));

  return (
    <div>
      <Link href="/dashboard" className="text-sm text-muted hover:text-ink">
        My searches
      </Link>
      <h1 className="display mt-3 text-3xl font-extrabold md:text-4xl">{results.category}</h1>
      <p className="mt-2 max-w-[60ch] leading-relaxed text-muted">
        {results.creators.length} creators whose main content is {results.category.toLowerCase()}, for{" "}
        <span className="text-ink">{search.title}</span>. Biggest first; change the order below.
      </p>
      <Results creators={results.creators} photos={photos} />
    </div>
  );
}
