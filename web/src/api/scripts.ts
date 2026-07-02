/**
 * 剧本 API
 *
 * 剧本列表、详情、证物池等操作。
 */
import { apiClient } from './client';

export const scriptsApi = {
  /** 获取剧本列表 */
  list: () =>
    apiClient.get('/scripts'),

  /** 获取剧本详情 */
  get: (scriptId: string) =>
    apiClient.get(`/scripts/${scriptId}`),

  /** 获取剧本证物池 */
  getEvidencePool: (scriptId: string) =>
    apiClient.get(`/scripts/${scriptId}/evidence-pool`),
};
