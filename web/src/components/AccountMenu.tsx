"use client";
import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { Avatar } from "@/components/Avatar";

/**
 * The account button in the header: Google photo, name, email and Sign out.
 * Closes on a click outside, on Escape and when the page changes (a plain <details> stayed open; user, 2026-11-27).
 */
export function AccountMenu({ name, email, avatar }: { name: string; email: string; avatar: string | null }) {
  // The menu remembers the page it was opened on, so moving to another page closes it.
  const path = usePathname();
  const [openOn, setOpenOn] = useState<string | null>(null);
  const open = openOn === path;
  const setOpen = (v: boolean) => setOpenOn(v ? path : null);
  const box = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOpen(false);
        button.current?.focus();
      }
    };
    document.addEventListener("pointerdown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onDown);
      document.removeEventListener("keydown", onKey);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  return (
    <div ref={box} className="relative">
      <button
        ref={button}
        type="button"
        onClick={() => setOpen(!open)}
        aria-label="Account"
        aria-expanded={open}
        aria-haspopup="true"
        className="flex items-center rounded-full p-0.5"
      >
        <Avatar src={avatar} name={name || email} size={36} />
      </button>
      {open && (
        <div className="card menu-pop absolute right-0 mt-2 w-60 p-3 text-sm">
          <p className="truncate font-semibold">{name}</p>
          <p className="truncate text-muted">{email}</p>
          <form action="/auth/signout" method="post" className="mt-3">
            <button className="btn btn-ghost h-9 w-full text-sm">Sign out</button>
          </form>
        </div>
      )}
    </div>
  );
}
