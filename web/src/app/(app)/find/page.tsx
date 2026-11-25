import type { Metadata } from "next";
import { StartSearch } from "@/components/StartSearch";

export const metadata: Metadata = { title: "New search" };

/** /find starts a new chat and moves to /find/<id>. */
export default function FindPage() {
  return <StartSearch />;
}
