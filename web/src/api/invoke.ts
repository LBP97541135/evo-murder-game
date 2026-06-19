/**
 * EvoMap Murder Game - API Layer
 *
 * 所有与后端交互的 API 调用封装。
 */

import { API_URL } from "../constants";
import { Actor, SafeActor, LLMMessage, AgentRegistration, AgentNodeInfo, GameSession } from "../types";


// ============================
// 通用 HTTP 工具
// ============================

async function post<T>(endpoint: string, body: object): Promise<T> {
  const r = await fetch(`${API_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`API Error: ${r.status} ${r.statusText}`);
  return r.json();
}

async function get<T>(endpoint: string): Promise<T> {
  const r = await fetch(`${API_URL}${endpoint}`);
  if (!r.ok) throw new Error(`API Error: ${r.status} ${r.statusText}`);
  return r.json();
}


// ============================
// AI Invocation（三层管道）
// ============================

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

export async function invokeAI(req: InvocationRequest): Promise<InvocationResponse> {
  return post<InvocationResponse>("/invoke", req);
}

/** 流式 SSE 调用（占位，后续实现） */
export async function invokeAIStream(
  req: InvocationRequest,
  onChunk: (text: string) => void,
  onDone: () => void,
): Promise<void> {
  // TODO: 实现流式 SSE 调用
  onChunk("[streaming placeholder]");
  onDone();
}


// ============================
// Agent Management
// ============================

export async function registerAgent(
  role: string, name: string, model: string,
  identityDoc: string, constitution: string,
): Promise<AgentRegistration> {
  return post<AgentRegistration>("/agents/register", {
    role, name, model, identity_doc: identityDoc, constitution,
  });
}

export async function listAgents(): Promise<{ agents: AgentNodeInfo[] }> {
  return get("/agents/list");
}

export async function heartbeatAgent(agentKey: string): Promise<any> {
  return post(`/agents/heartbeat/${agentKey}`, {});
}

export async function evolveAgent(
  agentKey: string, updateType: string, newContent: string,
): Promise<any> {
  return post(`/agents/evolve/${agentKey}`, {
    node_id: "", update_type: updateType, new_content: newContent,
  });
}


// ============================
// Game Session
// ============================

export async function createGameSession(
  scriptId: string, topic: string,
): Promise<GameSession> {
  return post<GameSession>("/game/create-session", { script_id: scriptId, topic });
}

export async function broadcastMessage(
  sessionId: string, msgType: string, payload: object, fromRole: string,
): Promise<any> {
  return post(`/game/broadcast/${sessionId}`, { msg_type: msgType, payload, from_role: fromRole });
}

export async function postGameReflection(
  sessionId: string, gameResult: object,
): Promise<any> {
  return post(`/game/reflect/${sessionId}`, gameResult);
}


// ============================
// Memory & Evolution
// ============================

export async function recordMemory(
  nodeId: string, signals: string[], geneId: string,
  status: string, score: number, summary: string,
): Promise<any> {
  return post("/memory/record", { node_id: nodeId, signals, gene_id: geneId, status, score, summary });
}

export async function recallMemory(
  nodeId: string, signals: string[], limit: number = 5,
): Promise<any> {
  return post("/memory/recall", { node_id: nodeId, signals, limit });
}

export async function memoryStatus(agentKey: string): Promise<any> {
  return get(`/memory/status/${agentKey}`);
}


// ============================
// SafeActor 信息隔离
// ============================

/** 创建安全版本的角色信息——过滤 secret/violation 字段。 */
export function createSafeActorList(actors: Actor[]): SafeActor[] {
  return actors.map((a) => ({
    id: a.id,
    name: a.name,
    bio: a.bio,
    personality: a.personality,
    context: a.context,
    image: a.image,
    isVictim: a.isVictim,
    isKiller: a.isKiller,
    isAssistant: a.isAssistant,
    isPlayer: a.isPlayer,
    isPartner: a.isPartner,
    roleType: a.roleType,
  }));
}
