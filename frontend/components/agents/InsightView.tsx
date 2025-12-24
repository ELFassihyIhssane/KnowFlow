import type { Insight } from "@/lib/types";

function Section({
  title,
  children
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/40 p-4">
      <div className="text-xs font-semibold text-white/70">{title}</div>
      <div className="mt-2">{children}</div>
    </div>
  );
}

export function InsightView({ insight }: { insight?: Insight | null }) {
  if (!insight) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-4">
        <div className="text-sm text-white/70">Insight</div>
        <div className="mt-2 text-sm text-white/60">(no insight)</div>
      </div>
    );
  }

  const gaps = insight.gaps ?? [];
  const contra = insight.contradictions ?? [];
  const future = insight.future_directions ?? [];

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="text-sm font-semibold text-brand-beige">Insight</div>
      <div className="mt-1 text-xs text-white/70">
        Deep analysis + gaps + future directions (if triggered).
      </div>

      <div className="mt-4 grid gap-3">
        {insight.analysis && (
          <Section title="Analysis">
            <div className="whitespace-pre-wrap text-sm text-white/85">
              {insight.analysis}
            </div>
          </Section>
        )}

        <div className="grid gap-3 md:grid-cols-3">
          <Section title={`Gaps (${gaps.length})`}>
            <ul className="list-disc space-y-1 pl-5 text-sm text-white/80">
              {gaps.length ? gaps.map((x, i) => <li key={i}>{x}</li>) : <li>(none)</li>}
            </ul>
          </Section>

          <Section title={`Contradictions (${contra.length})`}>
            <ul className="list-disc space-y-1 pl-5 text-sm text-white/80">
              {contra.length ? contra.map((x, i) => <li key={i}>{x}</li>) : <li>(none)</li>}
            </ul>
          </Section>

          <Section title={`Future directions (${future.length})`}>
            <ul className="list-disc space-y-1 pl-5 text-sm text-white/80">
              {future.length ? future.map((x, i) => <li key={i}>{x}</li>) : <li>(none)</li>}
            </ul>
          </Section>
        </div>
      </div>
    </div>
  );
}
