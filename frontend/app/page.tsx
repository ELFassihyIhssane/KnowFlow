import Link from "next/link";

export default function HomePage() {
  return (
    <main className="space-y-10">
      <section className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-soft">
        <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs text-white/80">
          RAG • Graph • Evaluation • Traces
        </div>

        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-brand-beige">
          KnowFlow
        </h1>
        <p className="mt-3 max-w-2xl text-white/75">
          Adaptive Knowledge-Driven Multi-Agent Orchestrator. Ask scientific questions,
          retrieve passages, visualize a knowledge graph, and get evaluation signals.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/query"
            className="rounded-xl bg-brand-blue px-5 py-3 text-sm font-semibold text-white shadow-soft hover:bg-brand-sea"
          >
            Start a Query
          </Link>
          <Link
            href="/graph"
            className="rounded-xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-brand-beige hover:bg-white/10"
          >
            Explore Graph
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          { title: "Orchestrator", desc: "Intent → pipeline selection → agents coordination." },
          { title: "Traceability", desc: "Agents used, passages, sources, evaluation signals." },
          { title: "Knowledge Graph", desc: "Concepts + relations, visualized with Cytoscape." },
        ].map((x) => (
          <div
            key={x.title}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 hover:bg-white/10"
          >
            <div className="text-sm font-semibold text-brand-beige">{x.title}</div>
            <div className="mt-2 text-sm text-white/70">{x.desc}</div>
          </div>
        ))}
      </section>
    </main>
  );
}
