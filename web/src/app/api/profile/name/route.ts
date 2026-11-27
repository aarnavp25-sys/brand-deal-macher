import { handle, jsonBody } from "@/lib/api";
import { saveName } from "@/lib/searches";

/** POST /api/profile/name  { name }: the name pop-up shown once after Google sign-in. */
export async function POST(req: Request) {
  return handle(async (brand) => {
    const body = await jsonBody(req);
    return { name: await saveName(brand.id, body.name) };
  });
}
