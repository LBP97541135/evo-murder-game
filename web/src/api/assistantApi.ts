import { API_URL } from "../constants";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`${path} 返回 ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function post<T>(path: string, body: Record<string, unknown>): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`${path} 返回 ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const forceAgentAnswer = (
  sessionId: string,
  targetKey: string,
  question: string,
  askerKey = "player",
) => post<{ success: boolean }>(`/game/force-answer/${sessionId}`, {
  asker_key: askerKey,
  target_key: targetKey,
  question,
});

/** @deprecated 喊话不再占用发言队列，无需 clear */
export const clearForceAnswer = (sessionId: string) =>
  post<{ success: boolean }>(`/game/force-answer/${sessionId}/clear`, {});

/** 解析 Agent 发言末尾的喊话标记 */
export function parseAgentCallout(text: string): {
  speechText: string;
  targetName: string | null;
  question: string;
} {
  const match = text.match(/\[喊话:([^|\]]+)(?:\|([^\]]*))?\]\s*$/);
  if (!match) {
    return { speechText: text.trim(), targetName: null, question: "" };
  }
  return {
    speechText: text.replace(/\[喊话:[^\]]+\]\s*$/, "").trim(),
    targetName: match[1].trim(),
    question: (match[2] || "").trim(),
  };
}

export const getRoleEvidences = (sessionId: string) =>
  get<{
    success: boolean;
    role_evidences: Record<string, Array<{ id: string; name: string; description: string }>>;
    player_role: string;
    player_evidences: Array<{ id: string; name: string; description: string }>;
  }>(`/game/role-evidences/${sessionId}`);

export const getPublicEvidences = (sessionId: string) =>
  get<{
    success: boolean;
    public_evidences: Array<{
      id: string;
      name: string;
      description: string;
      presented_by: string;
      reason?: string;
      ai_response?: string;
      presented_at?: string;
    }>;
  }>(`/game/public-evidences/${sessionId}`);

export const getAssistantGreeting = (userId = "user_default") =>
  get<{
    success: boolean;
    greeting: string;
    persona: { key: string; name: string; personaText: string; speechStyle: string };
  }>(`/users/assistant/greeting?user_id=${userId}`);

/** 解析 Agent 发言末尾的证物出示标记 */
export function parseAgentEvidencePresent(text: string): {
  speechText: string;
  evidenceName: string | null;
  reason: string;
} {
  const match = text.match(/\[出示证物:([^|\]]+)(?:\|([^\]]*))?\]\s*$/);
  if (!match) {
    return { speechText: text.trim(), evidenceName: null, reason: "" };
  }
  return {
    speechText: text.replace(/\[出示证物:[^\]]+\]\s*$/, "").trim(),
    evidenceName: match[1].trim(),
    reason: (match[2] || "").trim(),
  };
}
