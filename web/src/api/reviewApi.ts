import { API_URL } from "../constants";

async function request<T>(path: string, options: RequestInit = {}, timeoutMs = 600000): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
    if (!response.ok) {
      throw new Error(`${path} 返回 ${response.status}`);
    }
    return response.json() as Promise<T>;
  } finally {
    window.clearTimeout(timer);
  }
}

export type ScoreDimensionKey =
  | "evidenceCount"
  | "clueMastery"
  | "logicClarity"
  | "activity"
  | "progress"
  | "roleImmersion"
  | "collaboration"
  | "reasoningAccuracy";

export interface CharacterScore {
  role_name: string;
  agent_key?: string;
  agent_name?: string;
  participant_type?: string;
  compositeScore: number;
  dimensions: Record<ScoreDimensionKey, number>;
  dmComment: string;
}

export interface TruthReview {
  truth_narrative?: string;
  discussion_critique?: string;
  key_lessons?: string[];
  vote_analysis?: string;
}

export interface ReviewGene {
  id?: string;
  gene_id?: string;
  agent_key?: string;
  agent_name?: string;
  summary?: string;
  detail?: string;
  category?: string;
  score?: number;
  dmScore?: number;
  dmComment?: string;
  dmSuggestions?: string;
  capsuleId?: string;
}

export interface ReviewCapsule {
  id: string;
  title: string;
  category?: string;
  publisherRole?: string;
  agent_key?: string;
  agent_name?: string;
  score?: number;
  content?: string;
  strategy?: string;
  signals?: string[];
  usageCount?: number;
  createdAt?: string;
  stored_in_db?: boolean;
  reviewStatus?: string;
  geneId?: string;
}

export interface GameReviewBundle {
  success?: boolean;
  session_id?: string;
  script_title?: string;
  truth_killer?: string;
  truth_review?: TruthReview;
  character_scores?: CharacterScore[];
  score_dimensions?: Array<{ key: string; label: string; description: string }>;
  capsules?: ReviewCapsule[];
  genes?: ReviewGene[];
  evolution_summary?: {
    genes_created?: number;
    capsules_created?: number;
    capsules_stored?: number;
    errors?: string[];
  };
  message?: string;
  review_status?: string;
}

export const getGameReview = (sessionId: string) =>
  request<GameReviewBundle>(`/game/review/${sessionId}`);

export const runGameReview = (sessionId: string) =>
  request<GameReviewBundle>(`/game/review/${sessionId}/run`, { method: "POST" });
