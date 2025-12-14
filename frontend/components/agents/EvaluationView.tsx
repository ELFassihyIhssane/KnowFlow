import type { EvaluationResult } from "@/lib/types";
import { clamp01 } from "@/lib/utils";

export function EvaluationView({ evaluation }: { evaluation?: EvaluationResult }) {
  const issues = evaluation?.issues ?? [];
  const recs = evaluation?.recommendations ?? [];

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="text-sm text-zinc-400">Evaluator</div>

      {!evaluation ? (
        <div className="mt-2 text-zinc-300">(no evaluation)</div>
      ) : (
        <>
          <div className="mt-3 text-sm">
            <span className="text-zinc-400">Global score:</span>{" "}
            <span className="font-semibold">{clamp01(evaluation.global_score).toFixed(3)}</span>
          </div>

          <div className="mt-3">
            <div className="text-xs text-zinc-500">Scores</div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
              {Object.entries(evaluation.scores || {}).map(([k, v]) => (
                <div key={k} className="rounded-lg bg-zinc-800 p-2">
                  <div className="text-xs text-zinc-400">{k}</div>
                  <div className="font-semibold">{clamp01(v).toFixed(3)}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4">
            <div className="text-xs text-zinc-500">Issues ({issues.length})</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-200">
              {issues.length ? issues.map((x, i) => <li key={i}>{x}</li>) : <li>(none)</li>}
            </ul>
          </div>

          <div className="mt-4">
            <div className="text-xs text-zinc-500">Recommendations ({recs.length})</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-200">
              {recs.length ? recs.map((x, i) => <li key={i}>{x}</li>) : <li>(none)</li>}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
