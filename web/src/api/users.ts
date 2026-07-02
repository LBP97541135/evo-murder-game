/**
 * 用户 API
 *
 * 用户画像、个人助手等操作。
 */
import { apiClient } from './client';

export const usersApi = {
  /** 获取用户画像 */
  getProfile: (userId = 'user_default') =>
    apiClient.get(`/users/profile?user_id=${userId}`),

  /** 更新用户画像 */
  updateProfile: (data: any, userId = 'user_default') =>
    apiClient.post(`/users/profile/update?user_id=${userId}`, data),

  /** 个人助手对话 */
  assistantChat: (message: string, userId = 'user_default') =>
    apiClient.post(`/users/assistant/chat?user_id=${userId}`, { message }),

  /** 获取助手历史 */
  getAssistantHistory: (userId = 'user_default') =>
    apiClient.get(`/users/assistant/history?user_id=${userId}`),

  /** 获取助手问候 */
  getAssistantGreeting: (userId = 'user_default') =>
    apiClient.get(`/users/assistant/greeting?user_id=${userId}`),
};
