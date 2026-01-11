import { TopNav } from "@/components/layout/TopNav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-navy via-slate-950 to-slate-950">
      <TopNav />

      {/* */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute -left-24 top-24 h-80 w-80 rounded-full bg-brand-blue/25 blur-3xl" />
        <div className="absolute right-0 top-56 h-96 w-96 rounded-full bg-brand-sea/20 blur-3xl" />
        <div className="absolute left-1/3 bottom-0 h-96 w-96 rounded-full bg-brand-beige/10 blur-3xl" />
      </div>

      <div className="mx-auto max-w-6xl px-4 py-8">{children}</div>
    </div>
  );
}
