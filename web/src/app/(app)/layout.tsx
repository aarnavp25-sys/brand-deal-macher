import Link from "next/link";
import { Logo } from "@/components/Logo";
import { AccountMenu } from "@/components/AccountMenu";
import { NamePopup } from "@/components/NamePopup";
import { requireBrand } from "@/lib/auth";

/** Shell for every signed-in page (Google sign-in required). Checks the login with Supabase Auth before rendering. */
export default async function AppLayout({ children }: LayoutProps<"/">) {
  const brand = await requireBrand();
  return (
    <div className="min-h-[100dvh]">
      <header className="sticky top-0 z-20 border-b border-line bg-bg/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5 md:px-8">
          <Logo href="/dashboard" />
          <nav className="flex items-center gap-2 text-sm">
            <Link href="/dashboard" className="rounded-full px-3 py-2 hover:bg-surface-2">
              Dashboard
            </Link>
            <Link href="/find" className="btn btn-primary h-9 px-4 text-sm">
              New search
            </Link>
            <AccountMenu name={brand.name} email={brand.email} avatar={brand.avatar} />
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">{children}</main>
      {/* Right after Google sign-in: "What is your name?" until the brand answers it (user, 2026-11-27). */}
      {!brand.chatName && <NamePopup />}
    </div>
  );
}
