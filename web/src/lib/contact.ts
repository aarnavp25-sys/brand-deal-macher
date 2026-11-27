/*
  Collab contact a creator put in their own Instagram bio (user, 2026-11-27: "agar bio mein unka collab email hai ya
  phir number hai, to wo bhi dikhna chahiye"). Only what the bio itself shows: an email, an Indian mobile number,
  a WhatsApp link from the bio links. Nothing is guessed.
*/
export type Contact = { email?: string; phone?: string; whatsapp?: string };

const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}/;
const PHONE = /(?:\+?91[\s-]?)?\b([6-9]\d{4})[\s-]?(\d{5})\b/;

export function contactFrom(bio: string | null | undefined, links: { url?: string | null }[] | null | undefined): Contact {
  const out: Contact = {};
  const text = bio ?? "";
  const e = text.match(EMAIL);
  if (e) out.email = e[0].replace(/\.$/, "").toLowerCase();
  const p = text.match(PHONE);
  if (p) out.phone = `+91 ${p[1]} ${p[2]}`;
  for (const l of links ?? []) {
    const u = (l?.url ?? "").trim();
    if (/^https?:\/\/(wa\.me|api\.whatsapp\.com)\//i.test(u)) {
      out.whatsapp = u.replace(/^http:/i, "https:");
      break;
    }
  }
  return out;
}
