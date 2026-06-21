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

export function publicEventsToEvidenceRecords(
  events: Array<{ type: string; evidence?: { id: string; name: string; description: string }; speaker?: string; reason?: string; aiResponse?: string; targetName?: string }>,
): PublicEvidenceRecord[] {
  return events
    .filter((event) => event.type === "evidence" && event.evidence && (event.targetName === "所有人" || !event.targetName))
    .map((event) => ({
      id: event.evidence!.id,
      name: event.evidence!.name,
      description: event.evidence!.description,
      presented_by: (event.speaker || "").split(" · ")[0] || event.speaker || "未知",
      reason: event.reason,
      ai_response: event.aiResponse,
      presented_at: new Date().toISOString(),
    }));
}
