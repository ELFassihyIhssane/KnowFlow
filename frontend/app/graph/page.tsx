"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchGraph } from "@/lib/api-client";
import { GraphView } from "@/components/graph/GraphView";

export default function GraphPage() {
  const [loading, setLoading] = useState(false);
  const [graph, setGraph] = useState<{ nodes: any[]; edges: any[] } | null>(null);
  const [error, setError] = useState<string | null>(null);


  const [showScrollTop, setShowScrollTop] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

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


  useEffect(() => {
    function onScroll() {
      const y = window.scrollY || 0;
      const doc = document.documentElement;
      const max = Math.max(1, doc.scrollHeight - doc.clientHeight);
      const p = Math.min(1, Math.max(0, y / max));

      setScrollProgress(p);
      setShowScrollTop(y > 300);
    }

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }


  const ring = useMemo(() => {
    const size = 48;
    const stroke = 3;
    const r = (size - stroke) / 2;
    const c = 2 * Math.PI * r;
    const dash = c * (1 - scrollProgress);
    return { size, stroke, r, c, dash };
  }, [scrollProgress]);

  return (
    <main className="relative mx-auto max-w-6xl p-6">
      <h1 className="text-2xl font-semibold">Knowledge Graph</h1>

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

      {/* */}
      <div
        className={[
          "fixed bottom-6 right-6 z-50",
          "transition-all duration-300",
          showScrollTop
            ? "opacity-100 translate-y-0"
            : "pointer-events-none opacity-0 translate-y-3",
        ].join(" ")}
      >
        <button
          onClick={scrollToTop}
          aria-label="Scroll to top"
          className={[
            "group relative grid h-12 w-12 place-items-center rounded-full",
            "border border-white/15 bg-white/10 backdrop-blur-xl",
            "shadow-[0_10px_30px_-12px_rgba(0,0,0,0.6)]",
            "transition-transform duration-300 hover:scale-110 active:scale-95",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-beige/70 focus-visible:ring-offset-2 focus-visible:ring-offset-black/40",
          ].join(" ")}
        >
          {/*  */}
          <span
            className={[
              "absolute -inset-2 rounded-full opacity-0 blur-xl transition-opacity duration-300",
              "bg-brand-beige/30",
              "group-hover:opacity-100",
            ].join(" ")}
          />

          {/* */}
          <svg
            width={ring.size}
            height={ring.size}
            viewBox={`0 0 ${ring.size} ${ring.size}`}
            className="absolute inset-0"
            aria-hidden="true"
          >
            <circle
              cx={ring.size / 2}
              cy={ring.size / 2}
              r={ring.r}
              fill="none"
              stroke="rgba(255,255,255,0.14)"
              strokeWidth={ring.stroke}
            />
            <circle
              cx={ring.size / 2}
              cy={ring.size / 2}
              r={ring.r}
              fill="none"
              stroke="currentColor"
              className="text-brand-beige"
              strokeWidth={ring.stroke}
              strokeLinecap="round"
              strokeDasharray={ring.c}
              strokeDashoffset={ring.dash}
              transform={`rotate(-90 ${ring.size / 2} ${ring.size / 2})`}
            />
          </svg>

          {/*  */}
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            className="relative text-brand-beige transition-transform duration-300 group-hover:-translate-y-0.5"
            aria-hidden="true"
          >
            <path
              d="M12 5l-7 7m7-7l7 7M12 5v14"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </main>
  );
}
