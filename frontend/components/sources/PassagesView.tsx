import type { Passage } from "@/lib/types";

export function PassagesView({ passages }: { passages: Passage[] }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="text-sm text-zinc-400">Retrieved passages</div>

      <div className="mt-3 space-y-3">
        {passages.length === 0 ? (
          <div className="text-zinc-300">(no passages)</div>
        ) : (
          passages.map((p, idx) => (
            <div key={idx} className="rounded-lg border border-zinc-800 bg-zinc-950 p-3">
              <div className="flex items-center justify-between gap-4">
                <div className="text-xs text-zinc-500">#{idx} • score {p.score.toFixed(3)}</div>
                {p.metadata?.url && (
                  <a className="text-xs" href={p.metadata.url} target="_blank" rel="noreferrer">
                    open source
                  </a>
                )}
              </div>

              {p.metadata?.title && (
                <div className="mt-1 text-sm font-semibold text-zinc-200">
                  {p.metadata.title}
                </div>
              )}

              <div className="mt-2 whitespace-pre-wrap text-sm text-zinc-100">
                {p.text}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
