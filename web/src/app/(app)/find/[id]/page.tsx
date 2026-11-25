import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { requireBrand } from "@/lib/auth";
import { getSearch } from "@/lib/searches";
import { chatView } from "@/lib/chat-view";
import { facets } from "@/lib/matching";
import { Chat } from "@/components/Chat";

export const metadata: Metadata = { title: "Find creators" };

export default async function ChatPage({ params }: PageProps<"/find/[id]">) {
  const { id } = await params;
  const brand = await requireBrand(`/find/${id}`);
  const search = await getSearch(brand.id, id);
  if (!search) notFound();
  if (search.status === "done") redirect(`/results/${id}`);
  return <Chat initial={chatView(search)} facets={await facets()} />;
}
