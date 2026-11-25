import { handle } from "@/lib/api";
import { deleteSearch } from "@/lib/searches";

/** DELETE /api/searches/:id: remove one of the brand's own searches. */
export async function DELETE(_req: Request, ctx: RouteContext<"/api/searches/[id]">) {
  return handle(async (brand) => {
    const { id } = await ctx.params;
    await deleteSearch(brand.id, id);
    return { ok: true };
  });
}
