import axios from "axios";
import type { QueryResponse } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:7000";

export async function runQuery(question: string): Promise<QueryResponse> {
  const { data } = await axios.post<QueryResponse>(`${API_BASE}/api/query`, { question });
  return data;
}

// Optionnel (si tu as /api/graph côté backend)
export async function fetchGraph(): Promise<{ nodes: any[]; edges: any[] }> {
  const { data } = await axios.get(`${API_BASE}/api/graph/full`);
  return data;
}
