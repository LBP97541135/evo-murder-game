import type { PublicEvidenceRecord } from "./publicEvidence";

type DiscussionEvent = {
  type: string;
  speaker?: string;
  text?: string;
  evidence?: { name: string; description: string };
  reason?: string;
  aiResponse?: string;
  asker?: string;
  target?: string;
  question?: string;
  answer?: string;
};

export function buildDiscussionContextForPrompt(
  events: DiscussionEvent[],
  publicEvidence: PublicEvidenceRecord[] = [],
  extraEvidence?: { name: string; description: string; presentedBy?: string; reason?: string },
): string {
  const parts: string[] = [];

  const recent = events
    .filter((event) => ["speech", "evidence", "callout"].includes(event.type))
    .slice(-8);

  if (recent.length > 0) {
    const lines = recent.map((event) => {
      if (event.type === "speech") {
        return `${event.speaker}：${event.text}`;
      }
      if (event.type === "evidence") {
        let line = `${event.speaker} 向全场公开出示证物【${event.evidence?.name}】：${event.evidence?.description}`;
        if (event.reason) line += `（理由：${event.reason}）`;
        if (event.aiResponse) line += `；现场反应：${event.aiResponse}`;
        return line;
      }
      if (event.type === "callout") {
        return `${event.asker} 喊话 ${event.target}：「${event.question}」→ ${event.answer}`;
      }
      return "";
    }).filter(Boolean);
    parts.push(`【最近公共讨论】\n${lines.join("\n")}`);
  }

  const publicLines: string[] = [];
  if (extraEvidence) {
    publicLines.push(
      `- 【${extraEvidence.presentedBy || "刚出示"} 公开】${extraEvidence.name}：${extraEvidence.description}`
      + (extraEvidence.reason ? `（理由：${extraEvidence.reason}）` : ""),
    );
  }
  for (const item of publicEvidence) {
    if (extraEvidence && item.name === extraEvidence.name) continue;
    publicLines.push(
      `- 【${item.presented_by} 公开】${item.name}：${item.description}`
      + (item.reason ? `（理由：${item.reason}）` : ""),
    );
  }
  if (publicLines.length > 0) {
    parts.push(`【场上已公开证物（全场可见，你必须在此语境下回应）】\n${publicLines.join("\n")}`);
  }

  return parts.join("\n\n");
}

export function buildCalloutUserPrompt(
  askerLabel: string,
  question: string,
  discussionContext: string,
): string {
  const blocks = [
    discussionContext,
    `${askerLabel} 向你喊话："${question}"`,
    "请立即以角色身份简短回答（60-120字）。",
    "重要：若上述讨论中已有公开证物或发言与你相关，你必须在该语境下回应——可以撒谎、狡辩或转移话题，但不得假装「没听说过」「不知道有什么证物/血迹」。",
  ].filter(Boolean);
  return blocks.join("\n\n");
}
