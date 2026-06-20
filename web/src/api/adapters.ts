import type { BackendScript, EvidenceRecord } from "./invoke";
import type { ScriptCard } from "../pages/scriptData";
import type { Evidence } from "../pages/gameMockData";

const FALLBACK_COVER =
  "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1200&h=1500&fit=crop&auto=format";

const difficultyLabels: Record<string, ScriptCard["difficulty"]> = {
  easy: "入门",
  medium: "进阶",
  hard: "硬核",
  入门: "入门",
  进阶: "进阶",
  硬核: "硬核",
};

const genreLabels: Record<string, ScriptCard["genre"]> = {
  emotional: "情感本",
  mystery: "推理本",
  mechanism: "机制本",
  faction: "阵营本",
  情感本: "情感本",
  推理本: "推理本",
  机制本: "机制本",
  阵营本: "阵营本",
};

export function backendScriptToCard(script: BackendScript): ScriptCard {
  const duration = Number(script.duration || 0);
  const createdAt = script.createdAt ? new Date(script.createdAt).getTime() : 0;
  const isNew = createdAt > 0 && Date.now() - createdAt < 30 * 24 * 60 * 60 * 1000;
  const rating = Math.max(
    3.5,
    Math.min(5, 3.8 + Number(script.inferenceLevel || 0) * 0.7 + Number(script.emotionLevel || 0) * 0.5),
  );
  const tags = [
    script.theme,
    script.genre,
    script.inferenceLevel >= 0.7 ? "高推理" : "",
    script.emotionLevel >= 0.7 ? "强情感" : "",
    script.horrorLevel >= 0.5 ? "惊悚" : "",
  ].filter(Boolean);

  return {
    id: script.id,
    title: script.title,
    subtitle: script.author || script.version || "Backend Script",
    genre: genreLabels[script.genre] || "推理本",
    difficulty: difficultyLabels[script.difficulty] || "进阶",
    players: `${script.playerCount || 0}人`,
    playerCount: script.playerCount || script.characters?.length || 0,
    duration: duration ? `${Math.max(1, Math.round(duration / 60))}小时` : "时长待定",
    rating,
    description: script.description || script.globalStory || "暂无简介",
    details: script.globalStory || script.description || "暂无剧本详情",
    cover: script.coverImage || FALLBACK_COVER,
    tags: tags.length ? tags : ["后端剧本"],
    audienceTags: [
      script.difficulty === "easy" ? "新手玩家" : "推理玩家",
      script.playerCount >= 7 ? "大型组局" : "小型组局",
    ],
    hot: rating >= 4.6,
    newArrival: isNew,
    recommended: true,
    friendsPlayed: false,
    agentFit: [],
    roles: (script.characters || []).map((character) => String(character.name || "")).filter(Boolean),
  };
}

export function backendEvidenceToGameEvidence(evidence: EvidenceRecord): Evidence {
  return {
    id: evidence.id,
    name: evidence.name,
    description:
      evidence.deepDescription ||
      evidence.detailedDescription ||
      evidence.basicDescription ||
      "暂无描述",
    location: evidence.category || "未知位置",
    time: evidence.discoveryState || "已发现",
    source: evidence.importance || "后端证物",
    visibility: "仅自己",
    icon: evidence.category || "file",
  };
}
