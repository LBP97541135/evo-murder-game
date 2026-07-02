/**
 * 会话 API
 *
 * 游戏会话的创建、查询、快照、结束等操作。
 */
import { apiClient } from './client';

export const sessionsApi = {
  /** 创建游戏会话 */
  create: (scriptId: string, title?: string) =>
    apiClient.post('/sessions', { script_id: scriptId, title }),

  /** 获取会话详情 */
  get: (sessionId: string) =>
    apiClient.get(`/sessions/${sessionId}`),

  /** 获取会话快照（服务端主状态） */
  getSnapshot: (sessionId: string) =>
    apiClient.get(`/sessions/${sessionId}/snapshot`),

  /** 结束会话 */
  end: (sessionId: string) =>
    apiClient.post(`/sessions/${sessionId}/end`),
};
