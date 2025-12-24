export type Passage = {
  text: string;
  score: number;
  metadata?: Record<string, any>;
};

export type EvaluationResult = {
  scores: Record<string, number>;
  global_score: number;
  issues?: string[];
  recommendations?: string[];
};

export type AdaptationAction = {
  name: string;
  reason?: string;
  patch?: Record<string, any>;
};

export type Tuning = {
  top_k: number;
  min_overlap: number;
  temperature: number;
  enable_llm_critique: boolean;
  enable_graph_update: boolean;
};

export type Insight = {
  analysis?: string;
  gaps?: string[];
  contradictions?: string[];
  future_directions?: string[];
};

export type QueryResponse = {
  question: string;
  intent: string;
  sub_tasks: string[];
  answer: string;
  passages: Passage[];
  evaluation?: EvaluationResult;

  // ✅ insight
  insight?: Insight | null;

  // ✅ adaptation + manual retry
  can_retry?: boolean;
  retry_count?: number;
  adaptation_actions?: AdaptationAction[];
  tuning?: Tuning;

  graph?: { nodes: any[]; edges: any[] };
  agents_used?: string[];
};
