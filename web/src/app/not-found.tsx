import Link from "next/link";
import { Logo } from "@/components/Logo";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-xl flex-col px-6 py-6">
      <Logo />
      <div className="my-auto py-16">
        <h1 className="display text-4xl font-extrabold">Page not found</h1>
        <p className="mt-3 text-muted">This page does not exist, or it belongs to another account.</p>
        <Link href="/dashboard" className="btn btn-primary mt-8 h-11 px-6">Go to my searches</Link>
      </div>
    </div>
  );
}
