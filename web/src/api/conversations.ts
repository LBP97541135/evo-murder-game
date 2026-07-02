/**
 * 对话 API
 *
 * 对话消息的保存、查询、清空等操作。
 */
import { apiClient } from './client';

export const conversationsApi = {
  /** 保存对话记录 */
  save: (data: {
    sessionId: string;
    actorName: string;
    chatMessages?: Array<{ role: string; content: string }>;
    originalResponse?: string;
    critiqueResponse?: string;
    refinedResponse?: string;
    finalResponse?: string;
  }) =>
    apiClient.post('/conversations/save', {
      session_id: data.sessionId,
      actor_name: data.actorName,
      chat_messages: data.chatMessages || [],
      original_response: data.originalResponse || '',
      critique_response: data.critiqueResponse || '',
      refined_response: data.refinedResponse || '',
      final_response: data.finalResponse || '',
    }),

  /** 获取会话对话记录 */
  get: (sessionId: string, actorName?: string, limit = 100) =>
    apiClient.get(`/conversations/session/${sessionId}?actor_name=${actorName || ''}&limit=${limit}`),

  /** 清空会话对话记录 */
  clear: (sessionId: string) =>
    apiClient.delete(`/conversations/session/${sessionId}`),
};
