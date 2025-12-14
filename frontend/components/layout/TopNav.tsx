import Link from "next/link";

export function TopNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-brand-navy/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-brand-sea to-brand-blue shadow-soft" />
          <div className="leading-tight">
            <div className="text-sm font-semibold text-brand-beige">KnowFlow</div>
            <div className="text-[11px] text-white/70">Adaptive Multi-Agent Orchestrator</div>
          </div>
        </Link>

        <nav className="flex items-center gap-2 text-sm">
          <Link
            href="/"
            className="rounded-lg px-3 py-2 text-white/80 hover:bg-white/10 hover:text-white"
          >
            Home
          </Link>
          <Link
            href="/query"
            className="rounded-lg px-3 py-2 text-white/80 hover:bg-white/10 hover:text-white"
          >
            Query
          </Link>
          <Link
            href="/graph"
            className="rounded-lg px-3 py-2 text-white/80 hover:bg-white/10 hover:text-white"
          >
            Graph
          </Link>
        </nav>
      </div>
    </header>
  );
}
