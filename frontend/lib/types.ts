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

export type QueryResponse = {
  question: string;
  intent: string;
  sub_tasks: string[];
  answer: string;
  passages: Passage[];
  evaluation?: EvaluationResult;
  // futur: graph / traces
  graph?: { nodes: any[]; edges: any[] };
  agents_used?: string[];
};
