import { API_URL } from "../constants";
import type { Actor, LLMMessage, SafeActor } from "../types";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detail?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type QueryValue = string | number | boolean | null | undefined;

function endpoint(path: string, query?: Record<string, QueryValue>) {
  const url = new URL(`${API_URL}${path}`);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  query?: Record<string, QueryValue>,
): Promise<T> {
  const requestUrl = endpoint(path, query);
  let response: Response;
  try {
    response = await fetch(requestUrl, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    throw new ApiError(
      `无法连接后端 ${requestUrl}：${error instanceof Error ? error.message : String(error)}`,
      0,
      error,
    );
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : payload;
    throw new ApiError(
      `${requestUrl} 返回 ${response.status}：${
        typeof detail === "string" ? detail : JSON.stringify(detail)
      }`,
      response.status,
      detail,
    );
  }
  return payload as T;
}

const get = <T>(path: string, query?: Record<string, QueryValue>) =>
  request<T>(path, {}, query);
const post = <T>(path: string, body?: unknown, query?: Record<string, QueryValue>) =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }, query);
const put = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "PUT", body: JSON.stringify(body) });
const remove = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: "DELETE", body: body === undefined ? undefined : JSON.stringify(body) });

export interface BackendScript {
  id: string;
  title: string;
  description: string;
  author: string;
  version: string;
  globalStory: string;
  sourceType: string;
  coverImage: string;
  genre: string;
  theme: string;
  difficulty: string;
  duration: number;
  emotionLevel: number;
  inferenceLevel: number;
  horrorLevel: number;
  playerCount: number;
  fixedKiller: string;
  characters: Array<Record<string, any>>;
  evidences: Array<Record<string, any>>;
  quiz: Array<Record<string, any>>;
  settings: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface AgentInfo {
  key: string;
  name: string;
  role: "dm" | "companion" | "assistant";
  node_id: string;
  registered: boolean;
  model: string;
  persona_key: string;
}

export interface AgentPersona {
  id: string;
  key: string;
  name: string;
  role: "dm" | "companion" | "assistant";
  vibe: string;
  style: string;
  genius: string[];
  personality: string[];
  scriptTypes: string[];
  activeLevel: string;
  pace: string;
  strengths: string[];
  promptStyle: string;
  fairness: string;
  roleMatch: string;
  reason: string;
  rating: number;
  historyCount: number;
  recentTags: string[];
}

export interface EvidenceRecord {
  id: string;
  name: string;
  basicDescription: string;
  detailedDescription: string;
  deepDescription: string;
  image: string;
  category: string;
  discoveryState: string;
  unlockLevel: number;
  relatedActors: string[];
  relatedEvidences: string[];
  combinableWith: string[];
  importance: string;
  sessionId: string;
  scriptId: string;
  isNew: boolean;
  hasUpdate: boolean;
}

export interface InvocationRequest {
  globalStory: string;
  actor: Actor;
  sessionId: string;
  detectiveName: string;
  victimName: string;
  allActors: SafeActor[];
  chatMessages: LLMMessage[];
  temperature: number;
}

export interface InvocationResponse {
  original: string;
  critique: string;
  refined: string;
  finalResponse: string;
}

function actorPayload(actor: Actor | SafeActor) {
  return {
    id: actor.id,
    name: actor.name,
    bio: actor.bio,
    personality: actor.personality,
    context: actor.context,
    ...("secret" in actor ? { secret: actor.secret, violation: actor.violation } : {}),
    image: actor.image,
    is_victim: actor.isVictim,
    is_killer: actor.isKiller,
    is_assistant: actor.isAssistant,
    is_player: actor.isPlayer,
    is_partner: actor.isPartner,
    role_type: actor.roleType,
  };
}

function invocationPayload(req: InvocationRequest) {
  return {
    global_story: req.globalStory,
    actor: actorPayload(req.actor),
    session_id: req.sessionId,
    detective_name: req.detectiveName,
    victim_name: req.victimName,
    all_actors: req.allActors.map(actorPayload),
    chat_messages: req.chatMessages,
    temperature: req.temperature,
  };
}

export async function healthCheck() {
  return get<Record<string, any>>("/health");
}

export async function invokeAI(req: InvocationRequest): Promise<InvocationResponse> {
  const result = await post<Record<string, string>>("/invoke/", invocationPayload(req));
  return {
    original: result.original || "",
    critique: result.critique || "",
    refined: result.refined || "",
    finalResponse: result.final_response || "",
  };
}

export async function invokeAIStream(
  req: InvocationRequest,
  onChunk: (text: string) => void,
  onDone: (final: string) => void,
  onError?: (error: Error) => void,
) {
  try {
    const response = await fetch(endpoint("/invoke/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(invocationPayload(req)),
    });
    if (!response.ok || !response.body) {
      throw new ApiError(`Streaming request failed: ${response.status}`, response.status);
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
        const data = JSON.parse(line.slice(5).trim());
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

export const listScripts = async () =>
  (await get<{ success: boolean; scripts: BackendScript[] }>("/scripts/list")).scripts;
export const getScript = async (scriptId: string) =>
  (await get<{ success: boolean; script: BackendScript }>(`/scripts/${scriptId}`)).script;

export const registerAgent = (
  role: string,
  name: string,
  model: string,
  identityDoc = "",
  constitution = "",
) =>
  post<Record<string, any>>("/agents/register", {
    role,
    name,
    model,
    identity_doc: identityDoc,
    constitution,
  });
export const listAgents = () => get<{ agents: AgentInfo[] }>("/agents/list");
export const heartbeatAgent = (agentKey: string) => post<Record<string, any>>(`/agents/heartbeat/${agentKey}`, {});
export const evolveAgent = (agentKey: string, updateType: string, newContent: string, nodeId = "") =>
  post<Record<string, any>>(`/agents/evolve/${agentKey}`, {
    node_id: nodeId,
    update_type: updateType,
    new_content: newContent,
  });
export const initPersonas = () => post<Record<string, any>>("/agents/personas/init", {});
export const listPersonas = async (role?: string) =>
  (await get<{ personas: AgentPersona[] }>("/agents/personas", { role })).personas;
export const getPersona = (personaKey: string) => get<AgentPersona>(`/agents/personas/${personaKey}`);
export const loadPersona = (agentKey: string, personaKey: string) =>
  post<Record<string, any>>("/agents/personas/load", { agent_key: agentKey, persona_key: personaKey });
export const autoMatchPersonas = (scriptGenre: string, difficulty: string) =>
  post<Record<string, any>>("/agents/personas/auto-match", {
    script_genre: scriptGenre,
    difficulty,
  });

export const createGameSession = async (scriptId: string, topic: string, playerRoleId = "") => {
  const result = await post<{ session_id: string; participants: string[]; status: string }>(
    "/game/create-session",
    { script_id: scriptId, topic, player_role_id: playerRoleId },
  );
  return { sessionId: result.session_id, participants: result.participants, status: result.status };
};
export const getGamePhase = (sessionId: string) => get<Record<string, any>>(`/game/phase/${sessionId}`);
export const getGameSessionInfo = (sessionId: string) => get<Record<string, any>>(`/game/session-info/${sessionId}`);
export const playerChat = (sessionId: string, content: string, targetKey = "") =>
  post<Record<string, any>>(`/game/chat/${sessionId}`, { content, target_key: targetKey });
export const advanceGamePhase = (sessionId: string) => post<Record<string, any>>(`/game/phase/${sessionId}/advance`);
export const forceGamePhase = (sessionId: string, phase: string) =>
  post<Record<string, any>>(`/game/phase/${sessionId}/force`, { phase });
export const submitGameVote = (sessionId: string, killer: string, motive: string, voter = "player") =>
  post<Record<string, any>>(`/game/vote/${sessionId}`, { killer, motive, voter });
export const broadcastMessage = (
  sessionId: string,
  msgType: string,
  payload: object,
  fromRole: string,
) => post<Record<string, any>>(`/game/broadcast/${sessionId}`, undefined, {
  msg_type: msgType,
  payload: JSON.stringify(payload),
  from_role: fromRole,
});
export const recordChatCount = (sessionId: string) => post<Record<string, any>>(`/game/chat-count/${sessionId}`);
export const postGameReflection = (sessionId: string, result: object) =>
  post<Record<string, any>>(`/game/reflect/${sessionId}`, result);
export const revealGame = (sessionId: string, result: object) =>
  post<Record<string, any>>(`/game/reveal/${sessionId}`, result);
export const generateSpoiler = (sessionId: string, result: object) =>
  post<Record<string, any>>(`/game/reveal/${sessionId}/spoiler`, result);
export const getAgentState = (sessionId: string, agentKey: string) =>
  get<Record<string, any>>(`/game/agent-state/${sessionId}/${agentKey}`);
export const getAgentIntents = (sessionId: string, agentKey: string) =>
  get<Record<string, any>>(`/game/intents/${sessionId}/${agentKey}`);
export const generateAgentIntents = (sessionId: string, agentKey: string) =>
  post<Record<string, any>>(`/game/intents/${sessionId}/${agentKey}/generate`);
export const approveAgentIntent = (
  sessionId: string,
  agentKey: string,
  intentType: string,
  approved: boolean,
) => post<Record<string, any>>(`/game/intents/${sessionId}/${agentKey}/approve`, {
  intent_type: intentType,
  approved,
});
export const recordAgentChat = (sessionId: string, agentKey: string, content: string, role = "player") =>
  post<Record<string, any>>(`/game/agent-chat/${sessionId}`, {
    session_id: sessionId,
    agent_key: agentKey,
    content,
    role,
  });
export const initSpeakRound = (sessionId: string) => post<Record<string, any>>(`/game/speak-round/${sessionId}/init`);
export const getSpeakRound = (sessionId: string) => get<Record<string, any>>(`/game/speak-round/${sessionId}`);
export const nextSpeakRound = (sessionId: string) => post<Record<string, any>>(`/game/speak-round/${sessionId}/next`);

export const getEvidences = async (
  scriptId: string,
  sessionId: string,
  filters: { category?: string; discoveryState?: string; importance?: string } = {},
) => get<{ success: boolean; evidences: EvidenceRecord[]; stats: Record<string, any> }>(
  `/evidence/script/${scriptId}/session/${sessionId}`,
  {
    category: filters.category,
    discovery_state: filters.discoveryState,
    importance: filters.importance,
  },
);
export const createEvidence = (data: Record<string, any>) => post<Record<string, any>>("/evidence/create", data);
export const updateEvidence = (evidenceId: string, data: Record<string, any>) =>
  put<Record<string, any>>(`/evidence/${evidenceId}`, data);
export const presentEvidence = (
  evidenceId: string,
  presentedTo: string,
  presentedBy: string,
  textContent = "",
  presentationContext = "",
) => post<Record<string, any>>("/evidence/present", {
  evidenceId,
  presentedTo,
  presentedBy,
  textContent,
  presentationContext,
});
export const combineEvidences = (primaryEvidenceId: string, secondaryEvidenceId: string, attemptedBy: string) =>
  post<Record<string, any>>("/evidence/combine", { primaryEvidenceId, secondaryEvidenceId, attemptedBy });
export const getEvidencePresentations = (evidenceId: string) =>
  get<Array<Record<string, any>>>(`/evidence/${evidenceId}/presentations`);
export const getGameProgress = (sessionId: string) =>
  get<Record<string, any>>(`/evidence/progress/${sessionId}`);
export const updateProgressPhase = (sessionId: string, phase: string) =>
  post<Record<string, any>>(`/evidence/progress/${sessionId}/phase`, { phase });
export const deleteEvidence = (evidenceId: string) => remove<Record<string, any>>(`/evidence/${evidenceId}`);

export const saveConversation = (data: {
  sessionId: string;
  actorName: string;
  chatMessages?: LLMMessage[];
  originalResponse?: string;
  critiqueResponse?: string;
  refinedResponse?: string;
  finalResponse?: string;
}) => post<Record<string, any>>("/conversations/save", {
  session_id: data.sessionId,
  actor_name: data.actorName,
  chat_messages: data.chatMessages || [],
  original_response: data.originalResponse || "",
  critique_response: data.critiqueResponse || "",
  refined_response: data.refinedResponse || "",
  final_response: data.finalResponse || "",
});
export const getConversations = (sessionId: string, actorName?: string, limit = 100) =>
  get<Record<string, any>>(`/conversations/session/${sessionId}`, { actor_name: actorName, limit });
export const clearConversations = (sessionId: string) =>
  remove<Record<string, any>>(`/conversations/session/${sessionId}`);

export const saveSpoilerStory = (data: Record<string, any>) =>
  post<Record<string, any>>("/spoiler-stories/save", data);
export const listSpoilerStories = (scriptId: string) =>
  get<Record<string, any>>(`/spoiler-stories/${scriptId}`);
export const getSpoilerStory = (storyId: number) =>
  get<Record<string, any>>(`/spoiler-stories/story/${storyId}`);
export const updateSpoilerStory = (storyId: number, data: Record<string, any>) =>
  put<Record<string, any>>(`/spoiler-stories/${storyId}`, data);
export const deleteSpoilerStory = (storyId: number) =>
  remove<Record<string, any>>(`/spoiler-stories/${storyId}`);
export const batchDeleteSpoilerStories = (storyIds: number[]) =>
  post<Record<string, any>>("/spoiler-stories/batch-delete", storyIds);

export const recordMemory = (
  nodeId: string,
  signals: string[],
  geneId: string,
  status: string,
  score: number,
  summary: string,
) => post<Record<string, any>>("/memory/record", {
  node_id: nodeId,
  signals,
  gene_id: geneId,
  status,
  score,
  summary,
});
export const recallMemory = (nodeId: string, signals: string[], limit = 5) =>
  post<Record<string, any>>("/memory/recall", { node_id: nodeId, signals, limit });
export const memoryStatus = (agentKey: string) =>
  get<Record<string, any>>(`/memory/status/${agentKey}`);

export const createGene = (data: Record<string, any>) => post<Record<string, any>>("/capsules/genes", data);
export const getGene = (geneId: string) => get<Record<string, any>>(`/capsules/genes/${geneId}`);
export const listGenes = (filters: Record<string, QueryValue> = {}) =>
  get<Array<Record<string, any>>>("/capsules/genes", filters);
export const reviewGene = (geneId: string, dmNodeId = "") =>
  post<Record<string, any>>(`/capsules/genes/${geneId}/review`, { dm_node_id: dmNodeId });
export const generateCapsuleFromGene = (geneId: string) =>
  post<Record<string, any>>(`/capsules/genes/${geneId}/generate-capsule`);
export const searchCapsules = (data: Record<string, any>) =>
  post<Array<Record<string, any>>>("/capsules/search", data);
export const getCapsule = (capsuleId: string) =>
  get<Record<string, any>>(`/capsules/capsules/${capsuleId}`);
export const listCapsules = (filters: Record<string, QueryValue> = {}) =>
  get<Array<Record<string, any>>>("/capsules/capsules", filters);
export const deleteCapsule = (capsuleId: string) =>
  remove<Record<string, any>>(`/capsules/capsules/${capsuleId}`);
export const consumeCapsules = (agentRole: string, signals?: string[], limit = 5) =>
  post<Record<string, any>>("/capsules/consume", { agent_role: agentRole, signals, limit });
export const reviewAndGenerateCapsules = (sessionId: string, scriptId = "") =>
  post<Record<string, any>>("/capsules/review-and-generate", {
    session_id: sessionId,
    script_id: scriptId,
  });

export function createSafeActorList(actors: Actor[]): SafeActor[] {
  return actors.map(({ secret: _secret, violation: _violation, backgroundImage: _background, ...actor }) => actor);
}
