"use client";

import { useState } from "react";
import { runQuery } from "@/lib/api-client";
import type { QueryResponse } from "@/lib/types";
import { QueryForm } from "@/components/query/QueryForm";
import { QueryResult } from "@/components/query/QueryResult";

export default function QueryPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(question: string) {
    setLoading(true);
    setError(null);
    try {
      const data = await runQuery(question);
      setResult(data);
    } catch (e: any) {
      setError(e?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
<main className="space-y-6">
  <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-soft">
    <h1 className="text-2xl font-semibold text-brand-beige">Query</h1>
    <p className="mt-1 text-sm text-white/70">
      Ask a scientific question — see answer, passages, agents used, and evaluation.
    </p>
  </div>

  <QueryForm loading={loading} onSubmit={onSubmit} />

      {error && (
        <div className="mt-4 rounded-lg border border-red-600/40 bg-red-950/40 p-4 text-red-200">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6">
          <QueryResult data={result} />
        </div>
      )}
    </main>
  );
}
