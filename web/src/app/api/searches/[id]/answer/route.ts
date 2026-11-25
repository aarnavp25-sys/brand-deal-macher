import { handle, jsonBody } from "@/lib/api";
import { answer } from "@/lib/searches";
import { chatView } from "@/lib/chat-view";

/** POST /api/searches/:id/answer  { step, value }: answer the current question, get the next one. */
export async function POST(req: Request, ctx: RouteContext<"/api/searches/[id]/answer">) {
  return handle(async (brand) => {
    const { id } = await ctx.params;
    const body = await jsonBody(req);
    return chatView(await answer(brand.id, id, body.step, body.value));
  });
}
