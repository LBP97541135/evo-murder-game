import type { AgentInfo, AgentPersona } from "../api/invoke";
import type { GamePlayer } from "../pages/gameMockData";

export const HUMAN_PLAYER = "human-player";

/** 人设 slug → 中文名（模板一键选角 & 兜底显示） */
export const PERSONA_CN_NAMES: Record<string, string> = {
  "white-crow": "白鸦",
  echo: "回声",
  "paper-owl": "纸鸮",
  flint: "燧石",
  undertow: "暗潮",
  "luna-moth": "月蛾",
  "moon-moth": "月蛾",
  "shadow-weaver": "影织者",
  "night-cicada": "夜蝉",
  "candle-core": "烛核",
  "mist-harbor": "雾港",
};

const PERSONA_KEY_ALIASES: Record<string, string> = {
  "luna-moth": "moon-moth",
};

export type CastingAgentOption = {
  key: string;
  name: string;
  highlight: string;
  personaKey?: string;
};
export type CastingRoleOption = {
  id: string;
  role: string;
  publicIdentity: string;
  background: string;
  tags: string[];
  color: string;
};

export type CastAssignment = {
  roleId: string;
  assignee: string;
};

export type ScriptCharacterSource = {
  id: string;
  name: string;
  bio?: string;
  personality?: string;
  context?: string;
  secret?: string;
  violation?: string;
  isVictim?: boolean;
};

const SEAT_COLORS = ["orange", "teal", "blue", "grape", "gray", "indigo"];

function parseChineseAgentName(agent: AgentInfo): string {
  if (/[\u4e00-\u9fff]/.test(agent.name)) return agent.name;
  const suffix = agent.key.match(/companion_(.+)$/i)?.[1];
  if (suffix && /[\u4e00-\u9fff]/.test(suffix)) return suffix;
  if (agent.persona_key && PERSONA_CN_NAMES[agent.persona_key]) {
    return PERSONA_CN_NAMES[agent.persona_key];
  }
  return agent.name;
}

function personaHighlight(persona: AgentPersona): string {
  return persona.strengths?.[0] || persona.vibe || persona.style || persona.genius?.[0] || "陪玩 Agent";
}

/** 合并 orchestrator Agent 与人设库，统一中文名与 orchestrator key */
export function buildCompanionCastingOptions(
  agents: AgentInfo[],
  personas: AgentPersona[],
): CastingAgentOption[] {
  const companions = agents.filter((agent) => agent.role === "companion");
  const companionPersonas = personas.filter((persona) => persona.role === "companion");
  const personaByKey = new Map(companionPersonas.map((persona) => [persona.key, persona]));
  const usedKeys = new Set<string>();
  const options: CastingAgentOption[] = [];

  for (const agent of companions) {
    const aliasKey = agent.persona_key ? PERSONA_KEY_ALIASES[agent.persona_key] || agent.persona_key : "";
    const persona =
      (agent.persona_key ? personaByKey.get(agent.persona_key) : undefined)
      || (aliasKey ? personaByKey.get(aliasKey) : undefined)
      || companionPersonas.find((item) => item.name === parseChineseAgentName(agent));

    options.push({
      key: agent.key,
      name: persona?.name || parseChineseAgentName(agent),
      highlight: persona ? personaHighlight(persona) : "陪玩 Agent",
      personaKey: persona?.key || agent.persona_key || undefined,
    });
    usedKeys.add(agent.key);
  }

  // 人设库里有但 orchestrator 尚未注册的 companion（仅展示，不可选）
  for (const persona of companionPersonas) {
    const already = options.some((item) => item.personaKey === persona.key || item.name === persona.name);
    if (already) continue;
    options.push({
      key: `persona-${persona.key}`,
      name: persona.name,
      highlight: personaHighlight(persona),
      personaKey: persona.key,
    });
  }

  return options;
}

export function resolveTemplateAgentKey(
  templateKey: string,
  availableAgents: CastingAgentOption[],
): string {
  const normalizedKey = PERSONA_KEY_ALIASES[templateKey] || templateKey;
  const direct = availableAgents.find((agent) => agent.key === templateKey || agent.key === normalizedKey);
  if (direct && !direct.key.startsWith("persona-")) return direct.key;

  const byPersona = availableAgents.find(
    (agent) => agent.personaKey === templateKey || agent.personaKey === normalizedKey,
  );
  if (byPersona && !byPersona.key.startsWith("persona-")) return byPersona.key;

  const cnName = PERSONA_CN_NAMES[templateKey] || PERSONA_CN_NAMES[normalizedKey];
  if (cnName) {
    const byName = availableAgents.find((agent) => agent.name === cnName && !agent.key.startsWith("persona-"));
    if (byName) return byName.key;
  }

  return `seat-${templateKey}`;
}

export function templateAgentDisplayNames(
  templateKeys: string[],
  availableAgents: CastingAgentOption[],
): string[] {
  return templateKeys.map((key) => {
    const resolved = resolveTemplateAgentKey(key, availableAgents);
    const agent = availableAgents.find((item) => item.key === resolved);
    if (agent) return agent.name;
    return PERSONA_CN_NAMES[key] || PERSONA_CN_NAMES[PERSONA_KEY_ALIASES[key] || ""] || key;
  });
}

export function isSeatFilled(assignee: string, agents: CastingAgentOption[]): boolean {
  if (assignee === HUMAN_PLAYER) return true;
  if (assignee.startsWith("seat-") || assignee.startsWith("persona-")) return false;
  return agents.some((agent) => agent.key === assignee && !agent.key.startsWith("persona-"));
}

export function scriptCharacterToCastingRole(
  character: ScriptCharacterSource,
  index: number,
): CastingRoleOption {
  const bio = character.bio || "";
  const firstSentence = bio.split(/[。！？\n]/).find(Boolean) || bio;
  const personality = character.personality || "";
  return {
    id: character.id,
    role: character.name,
    publicIdentity: firstSentence.slice(0, 36),
    background: bio,
    tags: personality
      ? personality.split(/[、,，]/).map((item) => item.trim()).filter(Boolean).slice(0, 4)
      : [],
    color: SEAT_COLORS[index % SEAT_COLORS.length],
  };
}

export function buildRosterFromCast(
  roles: CastingRoleOption[],
  assignments: CastAssignment[],
  agents: CastingAgentOption[],
  humanDisplayName = "林晓青",
): GamePlayer[] {
  const roster: GamePlayer[] = [];

  for (const role of roles) {
    const assignment = assignments.find((item) => item.roleId === role.id);
    if (!assignment || assignment.assignee.startsWith("seat-")) continue;
    if (assignment.assignee !== HUMAN_PLAYER && !isSeatFilled(assignment.assignee, agents)) continue;

    if (assignment.assignee === HUMAN_PLAYER) {
      roster.push({
        id: "user",
        name: humanDisplayName,
        role: role.role,
        publicIdentity: role.publicIdentity,
        agent: false,
        color: "orange",
        status: "空闲",
        tags: role.tags,
        background: role.background,
      });
      continue;
    }

    const agent = agents.find((item) => item.key === assignment.assignee);
    if (!agent) continue;

    roster.push({
      id: role.id,
      name: agent.name,
      role: role.role,
      publicIdentity: role.publicIdentity,
      agent: true,
      agentKey: agent.key,
      color: role.color,
      status: "空闲",
      tags: role.tags,
      background: role.background,
    });
  }

  return roster;
}

export function filterTemplateAgentKeys(
  agentKeys: string[],
  availableAgents: CastingAgentOption[],
): string[] {
  return agentKeys.map((key) => resolveTemplateAgentKey(key, availableAgents));
}

export function buildCastPayload(
  roles: CastingRoleOption[],
  assignments: CastAssignment[],
): Array<{ type: string; role: string; agentKey: string }> {
  const payload: Array<{ type: string; role: string; agentKey: string }> = [];
  for (const role of roles) {
    const assignment = assignments.find((item) => item.roleId === role.id);
    if (!assignment || assignment.assignee.startsWith("seat-")) continue;
    if (assignment.assignee === HUMAN_PLAYER) {
      payload.push({ type: "human", role: role.role, agentKey: "" });
    } else {
      payload.push({ type: "agent", role: role.role, agentKey: assignment.assignee });
    }
  }
  return payload;
}
