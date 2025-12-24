"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { runQuery, retryQuery } from "@/lib/api-client";
import type { QueryResponse } from "@/lib/types";
import { QueryForm } from "@/components/query/QueryForm";
import { QueryResult } from "@/components/query/QueryResult";

type ToastState = {
  open: boolean;
  title: string;
  message?: string;
  kind?: "success" | "error" | "info";
};

export default function QueryPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [showScrollTop, setShowScrollTop] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0); // 0..1

  // 🔽 NEW: toast (popup)
  const [toast, setToast] = useState<ToastState>({
    open: false,
    title: "",
    message: "",
    kind: "info",
  });

  // 🔽 NEW: ref to QueryResult section
  const resultRef = useRef<HTMLDivElement | null>(null);

  function showToast(next: Omit<ToastState, "open">, autoCloseMs = 2800) {
    setToast({ open: true, ...next });
    window.setTimeout(() => {
      setToast((t) => ({ ...t, open: false }));
    }, autoCloseMs);
  }

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

  async function onRetry() {
    if (!result) return;
    const actions = result.adaptation_actions ?? [];
    const retryCount = result.retry_count ?? 0;

    setLoading(true);
    setError(null);

    try {
      const data = await retryQuery(result.question, retryCount, actions);
      setResult(data);

      // ✅ After DOM updates, scroll to QueryResult section
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      });

      // ✅ Toast after successful retry
      const appliedCount = (actions?.length ?? 0);
      showToast(
        {
          kind: "success",
          title: "Retry completed",
          message:
            appliedCount > 0
              ? `Applied ${appliedCount} adaptation patch${appliedCount > 1 ? "es" : ""}.`
              : "Retry completed.",
        },
        3000
      );
    } catch (e: any) {
      const msg = e?.message || "Retry failed";
      setError(msg);

      // ❌ Toast on error
      showToast({ kind: "error", title: "Retry failed", message: msg }, 3600);
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

  // Progress ring math
  const ring = useMemo(() => {
    const size = 48;
    const stroke = 3;
    const r = (size - stroke) / 2;
    const c = 2 * Math.PI * r;
    const dash = c * (1 - scrollProgress);
    return { size, stroke, r, c, dash };
  }, [scrollProgress]);

  const toastTone =
    toast.kind === "success"
      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-50"
      : toast.kind === "error"
      ? "border-red-400/20 bg-red-400/10 text-red-50"
      : "border-white/15 bg-white/10 text-white";

  return (
    <main className="relative space-y-6">
      {/* ✅ Toast / Popup */}
      <div
        className={[
          "fixed top-5 right-5 z-[60] w-[min(420px,calc(100vw-2.5rem))]",
          "transition-all duration-300",
          toast.open ? "opacity-100 translate-y-0" : "pointer-events-none opacity-0 -translate-y-2",
        ].join(" ")}
        aria-live="polite"
        aria-atomic="true"
      >
        <div
          className={[
            "relative overflow-hidden rounded-2xl border p-4",
            "backdrop-blur-xl shadow-[0_12px_40px_-18px_rgba(0,0,0,0.75)]",
            toastTone,
          ].join(" ")}
        >
          {/* subtle glow */}
          <span className="pointer-events-none absolute -inset-6 rounded-full bg-brand-beige/15 blur-2xl" />
          <div className="relative flex items-start gap-3">
            <div className="mt-0.5 h-2.5 w-2.5 rounded-full bg-brand-beige shadow-[0_0_0_4px_rgba(255,255,255,0.06)]" />
            <div className="flex-1">
              <div className="text-sm font-semibold">{toast.title}</div>
              {toast.message ? (
                <div className="mt-1 text-xs opacity-80">{toast.message}</div>
              ) : null}
            </div>
            <button
              onClick={() => setToast((t) => ({ ...t, open: false }))}
              className="relative rounded-lg px-2 py-1 text-xs text-white/70 hover:bg-white/10"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-soft">
        <h1 className="text-2xl font-semibold text-brand-beige">Query</h1>
        <p className="mt-1 text-sm text-white/70">
          Ask a scientific question — see answer, passages, agents used, evaluation, and adaptation.
        </p>
      </div>

      <QueryForm loading={loading} onSubmit={onSubmit} />

      {error && (
        <div className="rounded-2xl border border-red-600/40 bg-red-950/40 p-4 text-red-200">
          {error}
        </div>
      )}

      {/* ✅ Anchor section for auto-scroll after retry */}
      {result && (
        <div ref={resultRef} className="scroll-mt-24">
          <QueryResult data={result} loading={loading} onRetry={onRetry} />
        </div>
      )}

      {/* 🔼 Beautiful Scroll-to-Top */}
      <div
        className={[
          "fixed bottom-6 right-6 z-50",
          "transition-all duration-300",
          showScrollTop ? "opacity-100 translate-y-0" : "pointer-events-none opacity-0 translate-y-3",
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
          <span
            className={[
              "absolute -inset-2 rounded-full opacity-0 blur-xl transition-opacity duration-300",
              "bg-brand-beige/30",
              "group-hover:opacity-100",
            ].join(" ")}
          />

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

          <span className="relative grid place-items-center">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              className="text-brand-beige transition-transform duration-300 group-hover:-translate-y-0.5"
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
          </span>
        </button>
      </div>
    </main>
  );
}
