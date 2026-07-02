/**
 * 复盘 API
 *
 * 游戏复盘的查询和执行。
 */
import { apiClient } from './client';

export const reviewsApi = {
  /** 获取游戏复盘 */
  get: (sessionId: string) =>
    apiClient.get(`/game/review/${sessionId}`),

  /** 执行复盘 */
  run: (sessionId: string) =>
    apiClient.post(`/game/review/${sessionId}/run`),
};
