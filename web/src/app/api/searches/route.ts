import { handle } from "@/lib/api";
import { createSearch } from "@/lib/searches";

/** POST /api/searches: start a new "Find creators" chat (creates the visitor's anonymous session if needed). */
export async function POST() {
  return handle(async (brand) => ({ id: await createSearch(brand.id, brand.name) }), true);
}
