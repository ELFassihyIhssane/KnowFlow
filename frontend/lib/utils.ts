export function inferAgentsUsed(intent: string): string[] {
  const base = ["Intent Agent", "Retriever Agent", "Evaluator Agent"];

  if (intent === "summary") return ["Intent Agent", "Retriever Agent", "Summarizer Agent", "Evaluator Agent"];
  if (intent === "comparison") return ["Intent Agent", "Retriever Agent", "Summarizer Agent", "Insight Agent", "Evaluator Agent"];
  if (intent === "concepts") return ["Intent Agent", "Retriever Agent", "Concept & Graph Agent", "Evaluator Agent"];
  if (intent === "gap") return ["Intent Agent", "Retriever Agent", "Insight Agent", "Evaluator Agent"];
  if (intent === "deep_analysis") return ["Intent Agent", "Retriever Agent", "Insight Agent", "Evaluator Agent"];

  return base;
}

export function clamp01(x: number) {
  if (Number.isNaN(x)) return 0;
  return Math.max(0, Math.min(1, x));
}
