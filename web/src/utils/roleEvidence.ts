import type { Evidence } from "../types";

export function roleEvidenceItemsToGameEvidence(
  items: Array<{ id: string; name: string; description: string; category?: string }>,
): Evidence[] {
  return items.map((item) => ({
    id: item.id,
    name: item.name,
    description: item.description,
    location: item.category || "未知",
    time: "游戏开始",
    source: "角色初始证物",
    visibility: "仅自己" as const,
    icon: item.category || "card",
  }));
}
