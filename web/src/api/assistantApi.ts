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

const EVIDENCE_MARKER_RE = /\[出示证物:([^|\]]+)(?:\|([^\]]*))?\]/;
const CALLOUT_MARKER_RE = /\[喊话:([^|\]]+)(?:\|([^\]]*))?\]/;

function stripActionMarkers(text: string): string {
  return text
    .replace(EVIDENCE_MARKER_RE, "")
    .replace(CALLOUT_MARKER_RE, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/** 从 Agent 发言中解析证物出示 + 喊话（标记可在文末任意独立行） */
export function parseAgentSpeechActions(text: string): {
  speechText: string;
  evidenceName: string | null;
  evidenceReason: string;
  calloutTarget: string | null;
  calloutQuestion: string;
} {
  const evidenceMatch = text.match(EVIDENCE_MARKER_RE);
  const calloutMatch = text.match(CALLOUT_MARKER_RE);
  return {
    speechText: stripActionMarkers(text),
    evidenceName: evidenceMatch?.[1]?.trim() || null,
    evidenceReason: (evidenceMatch?.[2] || "").trim(),
    calloutTarget: calloutMatch?.[1]?.trim() || null,
    calloutQuestion: (calloutMatch?.[2] || "").trim(),
  };
}

/** 解析 Agent 发言中的喊话标记 */
export function parseAgentCallout(text: string): {
  speechText: string;
  targetName: string | null;
  question: string;
} {
  const parsed = parseAgentSpeechActions(text);
  return {
    speechText: parsed.speechText,
    targetName: parsed.calloutTarget,
    question: parsed.calloutQuestion,
  };
}

/** 解析 Agent 发言中的证物出示标记 */
export function parseAgentEvidencePresent(text: string): {
  speechText: string;
  evidenceName: string | null;
  reason: string;
} {
  const parsed = parseAgentSpeechActions(text);
  return {
    speechText: parsed.speechText,
    evidenceName: parsed.evidenceName,
    reason: parsed.evidenceReason,
  };
}

type StreamActorPayload = {
  id: string;
  name: string;
  bio?: string;
  personality?: string;
  context?: string;
  secret?: string;
  violation?: string;
  image?: string;
  isVictim?: boolean;
  isKiller?: boolean;
  isAssistant?: boolean;
  isPlayer?: boolean;
  isPartner?: boolean;
  roleType?: string;
};

/** 流式 invoke，支持 speech_phase */
export async function invokeAIStreamWithPhase(
  payload: {
    globalStory: string;
    actor: StreamActorPayload;
    sessionId: string;
    detectiveName: string;
    victimName: string;
    allActors: StreamActorPayload[];
    chatMessages: Array<{ role: string; content: string }>;
    temperature: number;
    speechPhase?: string;
  },
  onChunk: (text: string) => void,
  onDone: (final: string) => void,
  onError?: (error: Error) => void,
) {
  const actorPayload = (actor: StreamActorPayload) => ({
    id: actor.id,
    name: actor.name,
    bio: actor.bio,
    personality: actor.personality,
    context: actor.context,
    secret: actor.secret,
    violation: actor.violation,
    image: actor.image,
    is_victim: actor.isVictim,
    is_killer: actor.isKiller,
    is_assistant: actor.isAssistant,
    is_player: actor.isPlayer,
    is_partner: actor.isPartner,
    role_type: actor.roleType,
  });

  try {
    const response = await fetch(`${API_URL}/invoke/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({
        global_story: payload.globalStory,
        actor: actorPayload(payload.actor),
        session_id: payload.sessionId,
        detective_name: payload.detectiveName,
        victim_name: payload.victimName,
        all_actors: payload.allActors.map(actorPayload),
        chat_messages: payload.chatMessages,
        temperature: payload.temperature,
        speech_phase: payload.speechPhase || "",
      }),
    });
    if (!response.ok || !response.body) {
      throw new Error(`Streaming request failed: ${response.status}`);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let final = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";
      for (const event of events) {
        const line = event.split("\n").find((item) => item.startsWith("data:"));
        if (!line) continue;
        const data = JSON.parse(line.slice(5).trim()) as {
          type: string;
          content?: string;
          final?: string;
          message?: string;
        };
        if (data.type === "token") {
          final += data.content || "";
          onChunk(data.content || "");
        } else if (data.type === "done") {
          final = data.final || final;
        } else if (data.type === "error") {
          throw new Error(data.message || "Streaming request failed");
        }
      }
    }
    onDone(final);
  } catch (error) {
    onError?.(error instanceof Error ? error : new Error(String(error)));
    if (!onError) throw error;
  }
}
