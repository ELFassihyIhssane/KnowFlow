import Image from "next/image";
import Link from "next/link";

export function TopNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-brand-navy/70 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="relative flex items-center">
          {/*  */}
          <div className="relative h-10 w-10" />

          {/*  */}
          <div className="absolute left-0 top-1/2 h-40 w-52 -translate-y-1/2">
            <Image
              src="/KnowFlow.png"
              alt="KnowFlow"
              fill
              className="object-contain"
              priority
            />
          </div>
        </Link>

        <nav className="flex items-center gap-2 text-sm">
          <Link href="/" className="rounded-lg px-3 py-2 text-white/80 hover:bg-white/10 hover:text-white">
            Home
          </Link>
          <Link href="/query" className="rounded-lg px-3 py-2 text-white/80 hover:bg-white/10 hover:text-white">
            Query
          </Link>
          <Link href="/graph" className="rounded-lg px-3 py-2 text-white/80 hover:bg-white/10 hover:text-white">
            Graph
          </Link>
        </nav>
      </div>
    </header>
  );
}
