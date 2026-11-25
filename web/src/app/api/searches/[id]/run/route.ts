import { handle, jsonBody } from "@/lib/api";
import { runSearch } from "@/lib/searches";

/** POST /api/searches/:id/run  { brief }: save the final answers and load the creators of the chosen category. */
export async function POST(req: Request, ctx: RouteContext<"/api/searches/[id]/run">) {
  return handle(async (brand) => {
    const { id } = await ctx.params;
    const body = await jsonBody(req);
    await runSearch(brand.id, id, body.brief);
    return { ok: true, id };
  });
}
