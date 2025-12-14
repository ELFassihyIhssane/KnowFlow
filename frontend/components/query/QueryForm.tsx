"use client";

import { useState } from "react";

export function QueryForm({
  loading,
  onSubmit
}: {
  loading: boolean;
  onSubmit: (question: string) => void;
}) {
  const [q, setQ] = useState("");

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
      <label className="text-sm text-zinc-300">Question</label>
      <textarea
        value={q}
        onChange={(e) => setQ(e.target.value)}
       className="mt-2 h-28 w-full resize-none rounded-xl border border-white/10 bg-slate-950/60 p-3 text-white outline-none focus:border-brand-sea"
        placeholder="Ask something…"
      />

      <div className="mt-3 flex gap-3">
<button
  disabled={loading || q.trim().length < 3}
  onClick={() => onSubmit(q.trim())}
  className="rounded-xl bg-brand-blue px-4 py-2 text-sm font-semibold text-white shadow-soft hover:bg-brand-sea disabled:opacity-50"
>
  {loading ? "Running…" : "Run"}
</button>


        <button
          disabled={loading}
          onClick={() => setQ("")}
          className="rounded-lg bg-zinc-800 px-4 py-2 hover:bg-zinc-700 disabled:opacity-50"
        >
          Clear
        </button>
      </div>
    </div>
  );
}
