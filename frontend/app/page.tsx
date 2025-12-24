import Link from "next/link";
import { ArrowRight, GitBranch, Network, Sparkles, Layers3 } from "lucide-react";

export default function HomePage() {
  const features = [
    {
      title: "Orchestrator",
      desc: "Intent → pipeline selection → multi-agent coordination.",
      Icon: Layers3,
    },
    {
      title: "Traceability",
      desc: "Agents used, passages, sources, evaluation signals.",
      Icon: GitBranch,
    },
    {
      title: "Knowledge Graph",
      desc: "Concepts + relations, visualized with Cytoscape.",
      Icon: Network,
    },
  ];


  return (
    <main className="relative overflow-hidden">
      {/* Background glows (subtle) */}
      <div className="pointer-events-none absolute -top-36 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-brand-beige/12 blur-[120px]" />
      <div className="pointer-events-none absolute -bottom-40 right-[-120px] h-[520px] w-[520px] rounded-full bg-brand-blue/10 blur-[120px]" />

      {/* ONE compact HERO section */}
      <section className="relative rounded-3xl border border-white/10 bg-white/5 p-6 shadow-soft backdrop-blur-xl sm:p-7">
        {/* subtle sheen */}
        <div className="pointer-events-none absolute inset-0 rounded-3xl bg-gradient-to-b from-white/10 via-transparent to-transparent" />

        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs text-white/80">
            <Sparkles className="h-4 w-4 text-brand-beige" />
            RAG • Graph • Evaluation • Traces
          </div>

          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-brand-beige sm:text-4xl">
            KnowFlow
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-white/75 sm:text-base">
            Adaptive knowledge-driven multi-agent orchestrator. Ask scientific questions,
            retrieve grounded passages, explore a living knowledge graph, and inspect
            evaluation signals — all in one flow.
          </p>

          {/* CTAs */}
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              href="/query"
              className="
                group inline-flex items-center gap-2
                rounded-xl bg-brand-blue px-5 py-2.5
                text-sm font-semibold text-white
                shadow-soft transition-all
                hover:scale-[1.02] hover:bg-brand-sea
                active:scale-95
                focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-beige/70
                focus-visible:ring-offset-2 focus-visible:ring-offset-black/40
              "
            >
              Start a Query
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>

            <Link
              href="/graph"
              className="
                inline-flex items-center gap-2
                rounded-xl border border-white/20 bg-white/5 px-5 py-2.5
                text-sm font-semibold text-brand-beige
                backdrop-blur transition-all
                hover:scale-[1.02] hover:bg-white/10
                active:scale-95
                focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-beige/70
                focus-visible:ring-offset-2 focus-visible:ring-offset-black/40
              "
            >
              Explore Graph
              <Network className="h-4 w-4 opacity-80" />
            </Link>
          </div>

          {/* EVERYTHING INSIDE SAME "POPUP" */}
          <div className="mt-6 grid gap-4">
            {/* feature cards INSIDE hero */}
            <div className="grid gap-3 md:grid-cols-3">
              {features.map(({ title, desc, Icon }) => (
                <div
                  key={title}
                  className="
                    group relative overflow-hidden
                    rounded-2xl border border-white/10 bg-white/5 p-5
                    transition-all
                    hover:bg-white/10 hover:-translate-y-0.5
                    hover:shadow-[0_18px_50px_-30px_rgba(0,0,0,0.75)]
                  "
                >
                  <div className="pointer-events-none absolute -inset-10 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100">
                    <div className="h-full w-full rounded-full bg-brand-beige/10" />
                  </div>

                  <div className="relative flex items-start gap-3">
                    <div className="grid h-10 w-10 place-items-center rounded-2xl border border-white/10 bg-white/10">
                      <Icon className="h-5 w-5 text-brand-beige" />
                    </div>

                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-brand-beige">{title}</div>
                      <div className="mt-2 text-sm text-white/70">{desc}</div>
                      <div className="mt-3 text-xs text-white/55">
                        Designed for inspection & iteration
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* optional: small divider footer inside hero */}
            <div className="pt-1 text-xs text-white/45">
              Tip: Start with a Query, then inspect evaluation and graph updates.
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
