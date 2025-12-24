"use client";

import type { AdaptationAction, Tuning } from "@/lib/types";

function PatchBadge({ k, v }: { k: string; v: any }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs text-white/80">
      <span className="text-white/60">{k}</span>
      <span className="font-semibold text-brand-beige">{String(v)}</span>
    </span>
  );
}

export function AdaptationPanel({
  canRetry,
  retryCount,
  actions,
  tuning,
  onRetry,
  loading
}: {
  canRetry?: boolean;
  retryCount?: number;
  actions?: AdaptationAction[];
  tuning?: Tuning;
  onRetry: () => void;
  loading: boolean;
}) {
  const safeActions = actions ?? [];
  const can = Boolean(canRetry) && (retryCount ?? 0) < 1 && safeActions.length > 0;

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-brand-beige">Adaptation</div>
          <div className="mt-1 text-xs text-white/70">
            Suggestions based on evaluation signals (manual retry only).
          </div>
        </div>

        <button
          onClick={onRetry}
          disabled={!can || loading}
          className="rounded-xl bg-brand-blue px-4 py-2 text-sm font-semibold text-white shadow-soft hover:bg-brand-sea disabled:opacity-50"
          title={
            can
              ? "Retry once with recommended patches"
              : safeActions.length === 0
              ? "No adaptation suggested"
              : (retryCount ?? 0) >= 1
              ? "Retry already used"
              : "Retry not recommended"
          }
        >
          {loading ? "Retrying…" : "Retry (1x)"}
        </button>
      </div>

      <div className="mt-4 grid gap-3">
        {tuning && (
          <div className="rounded-xl border border-white/10 bg-slate-950/40 p-3">
            <div className="text-xs text-white/60">Current tuning</div>
            <div className="mt-2 flex flex-wrap gap-2">
              <PatchBadge k="top_k" v={tuning.top_k} />
              <PatchBadge k="temperature" v={tuning.temperature} />
              <PatchBadge k="min_overlap" v={tuning.min_overlap} />
              <PatchBadge k="llm_critique" v={tuning.enable_llm_critique} />
              <PatchBadge k="graph_update" v={tuning.enable_graph_update} />
            </div>
          </div>
        )}

        <div className="rounded-xl border border-white/10 bg-slate-950/40 p-3">
          <div className="text-xs text-white/60">
            Suggested actions ({safeActions.length})
          </div>

          {safeActions.length === 0 ? (
            <div className="mt-2 text-sm text-white/70">(none)</div>
          ) : (
            <div className="mt-3 space-y-3">
              {safeActions.map((a, i) => (
                <div key={i} className="rounded-xl border border-white/10 bg-white/5 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="rounded-lg bg-white/10 px-2 py-1 text-xs text-white/80">
                      {a.name}
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {a.patch
                        ? Object.entries(a.patch).map(([k, v]) => (
                            <PatchBadge key={k} k={k} v={v} />
                          ))
                        : null}
                    </div>
                  </div>

                  {a.reason && <div className="mt-2 text-sm text-white/70">{a.reason}</div>}
                </div>
              ))}
            </div>
          )}
        </div>

        {!canRetry && (
          <div className="text-xs text-white/60">
            Retry is not recommended for this run (or no useful patch).
          </div>
        )}
      </div>
    </div>
  );
}
