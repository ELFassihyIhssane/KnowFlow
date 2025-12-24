import type { QueryResponse } from "@/lib/types";
import { IntentView } from "@/components/agents/IntentView";
import { EvaluationView } from "@/components/agents/EvaluationView";
import { PassagesView } from "@/components/sources/PassagesView";
import { AdaptationPanel } from "@/components/query/AdaptationPanel";
import { inferAgentsUsed } from "@/lib/utils";
import { InsightView } from "@/components/agents/InsightView";

export function QueryResult({
  data,
  loading,
  onRetry
}: {
  data: QueryResponse;
  loading: boolean;
  onRetry: () => void;
}) {
  const agents = data.agents_used?.length ? data.agents_used : inferAgentsUsed(data.intent);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-sm font-semibold text-brand-beige">Answer</div>
            <div className="mt-1 text-xs text-white/60">Model-generated response grounded by passages.</div>
          </div>
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
            intent: {data.intent}
          </span>
        </div>

        <div className="mt-4 whitespace-pre-wrap rounded-xl border border-white/10 bg-slate-950/40 p-4 text-white/90">
          {data.answer?.trim() ? data.answer : "(empty answer)"}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <IntentView intent={data.intent} subTasks={data.sub_tasks} agentsUsed={agents} />
        <EvaluationView evaluation={data.evaluation} />
      </div>

      <AdaptationPanel
        canRetry={data.can_retry}
        retryCount={data.retry_count}
        actions={data.adaptation_actions}
        tuning={data.tuning}
        onRetry={onRetry}
        loading={loading}
      />
      <InsightView insight={data.insight} />

      <PassagesView passages={data.passages || []} />
    </div>
  );
}
