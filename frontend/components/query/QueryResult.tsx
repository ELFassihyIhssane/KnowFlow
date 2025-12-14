import type { QueryResponse } from "@/lib/types";
import { IntentView } from "@/components/agents/IntentView";
import { EvaluationView } from "@/components/agents/EvaluationView";
import { PassagesView } from "@/components/sources/PassagesView";
import { inferAgentsUsed } from "@/lib/utils";

export function QueryResult({ data }: { data: QueryResponse }) {
  const agents = data.agents_used?.length ? data.agents_used : inferAgentsUsed(data.intent);

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
        <div className="text-sm text-zinc-400">Answer</div>
        <div className="mt-2 whitespace-pre-wrap text-zinc-100">
          {data.answer?.trim() ? data.answer : "(empty answer)"}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <IntentView intent={data.intent} subTasks={data.sub_tasks} agentsUsed={agents} />
        <EvaluationView evaluation={data.evaluation} />
      </div>

      <PassagesView passages={data.passages || []} />
    </div>
  );
}
