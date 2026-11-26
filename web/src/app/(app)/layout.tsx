import Link from "next/link";
import { Logo } from "@/components/Logo";

/** Shell for the chat, results and "My searches". Each page checks the visitor's session itself. */
export default function AppLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="min-h-[100dvh]">
      <header className="sticky top-0 z-20 border-b border-line bg-bg/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5 md:px-8">
          <Logo href="/dashboard" />
          <nav className="flex items-center gap-2 text-sm">
            <Link href="/dashboard" className="rounded-full px-3 py-2 hover:bg-surface-2">
              My searches
            </Link>
            <Link href="/find" className="btn btn-primary h-9 px-4 text-sm">
              New search
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">{children}</main>
    </div>
  );
}
