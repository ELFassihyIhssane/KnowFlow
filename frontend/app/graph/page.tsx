"use client";

import { useState } from "react";
import { fetchGraph } from "@/lib/api-client";
import { GraphView } from "@/components/graph/GraphView";

export default function GraphPage() {
  const [loading, setLoading] = useState(false);
  const [graph, setGraph] = useState<{ nodes: any[]; edges: any[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const g = await fetchGraph();
      setGraph(g);
    } catch (e: any) {
      setError(e?.message || "Graph endpoint not available");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl p-6">
      <h1 className="text-2xl font-semibold">Knowledge Graph</h1>
      <p className="mt-1 text-zinc-300">
        Cytoscape view of the KG (requires backend /api/graph).
      </p>

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={load}
          className="rounded-lg bg-zinc-800 px-4 py-2 hover:bg-zinc-700 disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Loading..." : "Load graph"}
        </button>
        {error && <span className="text-red-300">{error}</span>}
      </div>

      <div className="mt-6">
        <GraphView graph={graph} />
      </div>
    </main>
  );
}
