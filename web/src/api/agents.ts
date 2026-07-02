/**
 * Agent API
 *
 * Agent 注册、心跳、进化、人格等操作。
 */
import { apiClient } from './client';

export const agentsApi = {
  /** 注册 Agent */
  register: (data: { role: string; name: string; model: string; identityDoc?: string; constitution?: string }) =>
    apiClient.post('/agents/register', data),

  /** 获取 Agent 列表 */
  list: () =>
    apiClient.get('/agents/list'),

  /** Agent 心跳 */
  heartbeat: (agentKey: string) =>
    apiClient.post(`/agents/heartbeat/${agentKey}`),

  /** Agent 进化 */
  evolve: (agentKey: string, data: { nodeId?: string; updateType: string; newContent: string }) =>
    apiClient.post(`/agents/evolve/${agentKey}`, data),

  /** 初始化人格 */
  initPersonas: () =>
    apiClient.post('/agents/personas/init'),

  /** 获取人格列表 */
  listPersonas: (role?: string) =>
    apiClient.get(`/agents/personas${role ? `?role=${role}` : ''}`),

  /** 获取人格详情 */
  getPersona: (personaKey: string) =>
    apiClient.get(`/agents/personas/${personaKey}`),

  /** 加载人格 */
  loadPersona: (agentKey: string, personaKey: string) =>
    apiClient.post('/agents/personas/load', { agent_key: agentKey, persona_key: personaKey }),

  /** 自动匹配人格 */
  autoMatchPersonas: (scriptGenre: string, difficulty: string) =>
    apiClient.post('/agents/personas/auto-match', { script_genre: scriptGenre, difficulty }),
};
