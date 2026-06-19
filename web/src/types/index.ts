/**
 * EvoMap Murder Game - 类型定义
 *
 * 定义所有前端使用的 TypeScript 类型。
 */

// ============================
// 角色 / Agent 类型
// ============================

export interface Actor {
  id: string;
  name: string;
  bio: string;
  personality: string;
  context: string;
  secret: string;
  violation: string;
  image?: string;
  backgroundImage?: string;
  isVictim: boolean;
  isKiller: boolean;
  isAssistant: boolean;
  isPlayer: boolean;
  isPartner: boolean;
  roleType: string; // suspect / witness / victim / killer / assistant / partner
}

export interface SafeActor {
  id: string;
  name: string;
  bio: string;
  personality: string;
  context: string;
  image?: string;
  isVictim: boolean;
  isKiller: boolean;
  isAssistant: boolean;
  isPlayer: boolean;
  isPartner: boolean;
  roleType: string;
}

export interface LLMMessage {
  role: string;
  content: string;
}

// ============================
// Agent 节点类型
// ============================

export interface AgentNodeInfo {
  key: string;
  name: string;
  role: "dm" | "companion" | "assistant";
  nodeId: string;
  registered: boolean;
  model: string;
}

export interface AgentRegistration {
  nodeId: string;
  nodeSecret: string;
  claimUrl: string;
  claimCode: string;
  status: string;
}

// ============================
// 剧本类型
// ============================

export interface Script {
  id: string;
  title: string;
  description: string;
  author: string;
  globalStory: string;
  sourceType: string;
  theme: string;
  difficulty: string;
  duration: number;
  emotionLevel: number;
  inferenceLevel: number;
  horrorLevel: number;
  playerCount: number;
  coverImage?: string;
  fixedKiller: string;
  characters: Character[];
}

export interface Character {
  id: string;
  name: string;
  bio: string;
  personality: string;
  context: string;
  secret: string;
  violation: string;
  isVictim: boolean;
  isKiller: boolean;
  isAssistant: boolean;
  isPlayer: boolean;
  isPartner: boolean;
  roleType: string;
  image?: string;
  backgroundImage?: string;
}

export interface ScriptSettings {
  theme: string;
  difficulty: string;
  duration: number;
  emotionLevel: number;
  inferenceLevel: number;
  horrorLevel: number;
  playerCount: number;
  fixedKiller: string;
}

// ============================
// 游戏会话类型
// ============================

export interface GameSession {
  sessionId: string;
  participants: string[];
  status: "active" | "paused" | "completed" | "failed";
  scriptId: string;
  topic: string;
  currentPhase: string;
}

// ============================
// 进化类型
// ============================

export interface EvolutionRecord {
  id: string;
  agentNodeId: string;
  sessionId: string;
  signals: string[];
  geneId: string;
  status: string;
  score: number;
  summary: string;
  updateType: string;
  oldContent: string;
  newContent: string;
  createdAt: string;
}

export interface EvolutionUpdate {
  nodeId: string;
  updateType: "constitution" | "identity_doc";
  newContent: string;
}
