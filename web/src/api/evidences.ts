/**
 * 证物 API
 *
 * 证物的发现、出示、组合等操作。
 */
import { apiClient } from './client';

export const evidencesApi = {
  /** 获取证物列表 */
  list: (scriptId: string, sessionId: string) =>
    apiClient.get(`/evidence/script/${scriptId}/session/${sessionId}`),

  /** 创建证物 */
  create: (data: any) =>
    apiClient.post('/evidence/create', data),

  /** 发现证物 */
  discover: (data: { scriptId: string; sessionId: string; scriptEvidenceId: string; discoveredBy?: string }) =>
    apiClient.post('/evidence/discover', data),

  /** 出示证物 */
  present: (data: { evidenceId: string; presentedTo: string; presentedBy: string; textContent?: string; presentationContext?: string }) =>
    apiClient.post('/evidence/present', data),

  /** 组合证物 */
  combine: (primaryEvidenceId: string, secondaryEvidenceId: string, attemptedBy: string) =>
    apiClient.post('/evidence/combine', { primaryEvidenceId, secondaryEvidenceId, attemptedBy }),

  /** 获取证物出示记录 */
  getPresentations: (evidenceId: string) =>
    apiClient.get(`/evidence/${evidenceId}/presentations`),

  /** 删除证物 */
  delete: (evidenceId: string) =>
    apiClient.delete(`/evidence/${evidenceId}`),
};
