import type { Evidence } from "../pages/gameMockData";

export type PublicEvidenceRecord = {
  id: string;
  name: string;
  description: string;
  presented_by: string;
  reason?: string;
  ai_response?: string;
  presented_at?: string;
};

export function publicEvidenceRecordToGameEvidence(item: PublicEvidenceRecord): Evidence {
  return {
    id: item.id,
    name: item.name,
    description: item.description,
    location: "线索交流",
    time: item.presented_at ? new Date(item.presented_at).toLocaleString("zh-CN") : "讨论阶段",
    source: `${item.presented_by} 公开出示`,
    visibility: "所有人",
    icon: "card",
  };
}

export function publicEvidenceRecordsToGameEvidence(items: PublicEvidenceRecord[]): Evidence[] {
  return items.map(publicEvidenceRecordToGameEvidence);
}

export function mergePublicEvidenceRecords(
  current: PublicEvidenceRecord[],
  incoming: PublicEvidenceRecord,
): PublicEvidenceRecord[] {
  if (current.some((item) => item.id === incoming.id)) return current;
  return [...current, incoming];
}
