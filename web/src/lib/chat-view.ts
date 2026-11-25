import type { Draft } from "@/lib/brief";
import type { Msg, Search, Status } from "@/lib/searches";

/** What the browser gets for the chat screen: no user id, no results. */
export type ChatView = { id: string; status: Status; messages: Msg[]; brief: Draft };

export function chatView(s: Search): ChatView {
  return { id: s.id, status: s.status, messages: s.messages, brief: s.brief ?? {} };
}
