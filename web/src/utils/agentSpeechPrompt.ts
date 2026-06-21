type HeldEvidence = { name: string; description: string };
type RosterPlayer = { id: string; role: string; name: string };

export function buildAgentDiscussionUserPrompt(
  recentDiscussion: string,
  heldEvidences: HeldEvidence[],
  roster: RosterPlayer[],
  speakerId: string,
): string {
  const evidenceBlock = heldEvidences.length
    ? heldEvidences
      .filter((item) => item.name)
      .map((item) => `- ${item.name}：${item.description || "（无描述）"}`)
      .join("\n")
    : "（当前未分配证物，不可出示）";

  const calloutTargets = roster
    .filter((player) => player.id !== speakerId)
    .map((player) => player.role)
    .concat("林晓青")
    .join("、");

  return [
    `最近讨论内容：\n${recentDiscussion || "（讨论刚开始）"}`,
    "",
    "【你当前持有的证物】（公开出示时须使用下列完整名称）",
    evidenceBlock,
    "",
    `【可喊话对象】${calloutTargets}`,
    "",
    "请按「线索交流」规则发表 100-200 字看法。正文结束后，**另起一行**追加行动标记（可同时使用两条）：",
    "[出示证物:证物全名|出示理由]",
    "[喊话:角色名或林晓青|问题]",
    "",
    "示例：",
    "我认为控制室的时间线对不上，需要有人解释清楚。",
    "[出示证物:值班日志|记录显示案发时段有人进出]",
    "[喊话:秦野|你当时在哪里]",
  ].join("\n");
}
