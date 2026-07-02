/**
 * Skill API
 *
 * Skill 的增删改查、搜索、导入导出、审核等操作。
 */
import { apiClient } from './client';

export const skillsApi = {
  /** 获取 Skill 列表 */
  list: (params?: { category?: string; status?: string }) =>
    apiClient.get(`/skills${params ? `?category=${params.category || ''}&status=${params.status || ''}` : ''}`),

  /** 获取 Skill 详情 */
  get: (skillId: string) =>
    apiClient.get(`/skills/${skillId}`),

  /** 创建 Skill */
  create: (data: any) =>
    apiClient.post('/skills', data),

  /** 更新 Skill */
  update: (skillId: string, data: any) =>
    apiClient.patch(`/skills/${skillId}`, data),

  /** 删除 Skill */
  delete: (skillId: string) =>
    apiClient.delete(`/skills/${skillId}`),

  /** 搜索 Skill */
  search: (params: { role?: string; category?: string; signals?: string[] }) =>
    apiClient.post('/skills/search', params),

  /** 导出 Skill */
  export: (skillId: string) =>
    apiClient.get(`/skills/${skillId}/export`),

  /** 导入 Skill */
  import: (data: any) =>
    apiClient.post('/skills/import', data),

  /** 审核 Skill */
  review: (skillId: string, data: { status: string; comment?: string }) =>
    apiClient.post(`/skills/${skillId}/review`, data),
};
