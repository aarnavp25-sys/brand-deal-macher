import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Avatar } from "@/components/Avatar";
import { requireBrand } from "@/lib/auth";

/** Shell for every signed-in page. Checks the login with Supabase Auth before rendering anything. */
export default async function AppLayout({ children }: LayoutProps<"/">) {
  const brand = await requireBrand();
  return (
    <div className="min-h-[100dvh]">
      <header className="sticky top-0 z-20 border-b border-line bg-bg/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5 md:px-8">
          <Logo href="/dashboard" />
          <nav className="flex items-center gap-2 text-sm">
            <Link href="/dashboard" className="hidden rounded-full px-3 py-2 hover:bg-surface-2 sm:inline-block">
              My searches
            </Link>
            <Link href="/find" className="btn btn-primary h-9 px-4 text-sm">
              New search
            </Link>
            <details className="relative">
              <summary className="flex cursor-pointer list-none items-center rounded-full p-0.5" aria-label="Account">
                <Avatar src={brand.avatar} name={brand.name || brand.email} size={36} />
              </summary>
              <div className="card absolute right-0 mt-2 w-60 p-3 text-sm">
                <p className="truncate font-semibold">{brand.name}</p>
                <p className="truncate text-muted">{brand.email}</p>
                <form action="/auth/signout" method="post" className="mt-3">
                  <button className="btn btn-ghost h-9 w-full text-sm">Sign out</button>
                </form>
              </div>
            </details>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">{children}</main>
    </div>
  );
}
