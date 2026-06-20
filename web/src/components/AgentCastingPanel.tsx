import React from "react";
import {
  Avatar,
  Badge,
  Box,
  Card,
  Collapse,
  Group,
  Modal,
  Paper,
  ScrollArea,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import {
  HUMAN_PLAYER,
  filterTemplateAgentKeys,
  isSeatFilled,
  templateAgentDisplayNames,
  type CastAssignment,
  type CastingAgentOption,
  type CastingRoleOption,
} from "../utils/gameCasting";

const characterPortraits: Record<string, string> = {
  "周野": new URL("../Character/周野.png", import.meta.url).href,
  "顾沉": new URL("../Character/顾沉.png", import.meta.url).href,
  "沈禾": new URL("../Character/沈禾.png", import.meta.url).href,
  "沈砚": new URL("../Character/沈禾.png", import.meta.url).href,
  "周岚": new URL("../Character/周岚.png", import.meta.url).href,
  "秦野": new URL("../Character/秦野.png", import.meta.url).href,
  "林远": new URL("../Character/周野.png", import.meta.url).href,
};

const agentPortraits: Record<string, string> = {
  "白鸦": new URL("../video_picture/白鸽.png", import.meta.url).href,
  "回声": new URL("../video_picture/回声.png", import.meta.url).href,
  "纸鸮": new URL("../video_picture/纸鸮.png", import.meta.url).href,
  "燧石": new URL("../video_picture/燧石.png", import.meta.url).href,
  "月蛾": new URL("../video_picture/月蛾.png", import.meta.url).href,
  "影织者": new URL("../video_picture/影织者.png", import.meta.url).href,
  "夜蝉": new URL("../video_picture/夜蝉.png", import.meta.url).href,
  "雾港主理人": new URL("../video_picture/雾港主理人.png", import.meta.url).href,
  "暮烛引导员": new URL("../video_picture/暮烛引导员.png", import.meta.url).href,
  "铁幕裁判": new URL("../video_picture/铁幕裁判.png", import.meta.url).href,
};

type CastingTemplate = {
  key: string;
  name: string;
  type: "高玩局" | "小白局" | "混合局";
  playerCount: number;
  agentKeys: string[];
  description: string;
};

const CASTING_TEMPLATES: CastingTemplate[] = [
  {
    key: "balanced-5",
    name: "均衡五座",
    type: "混合局",
    playerCount: 5,
    agentKeys: ["echo", "white-crow", "paper-owl", "flint", "luna-moth"],
    description: "锈铁大道推荐：5 名嫌疑人各由一名陪玩 Agent 担任，真人以侦探林晓青身份参与。",
  },
  {
    key: "reasoning-5",
    name: "推理五座",
    type: "高玩局",
    playerCount: 5,
    agentKeys: ["white-crow", "night-cicada", "flint", "echo", "luna-moth"],
    description: "强化时间线、证据链和交叉追问。",
  },
  {
    key: "story-5",
    name: "沉浸五座",
    type: "小白局",
    playerCount: 5,
    agentKeys: ["paper-owl", "luna-moth", "white-crow", "echo", "night-cicada"],
    description: "以情绪承接和角色表达为主。",
  },
  {
    key: "balanced-6",
    name: "均衡六座",
    type: "混合局",
    playerCount: 6,
    agentKeys: ["echo", "white-crow", "paper-owl", "flint", "luna-moth", "shadow-weaver"],
    description: "6 人局推荐：5 名嫌疑人 + 1 名证人，含悬念编织。",
  },
  {
    key: "beginner-6",
    name: "新手六座",
    type: "小白局",
    playerCount: 6,
    agentKeys: ["paper-owl", "candle-core", "white-crow", "luna-moth", "echo", "mist-harbor"],
    description: "六席本模板（需剧本提供 6 个可玩席位）。",
  },
];

const AVATAR_COLORS = ["red", "orange", "grape", "blue", "cyan", "teal", "pink", "yellow"];

type AgentCastingPanelProps = {
  roles: CastingRoleOption[];
  availableAgents: CastingAgentOption[];
  selectedPlayerRoleId: string;
  onPlayerRoleChange: (roleId: string) => void;
  onEnsembleChange: (filled: boolean) => void;
  onCastChange: (assignments: CastAssignment[]) => void;
};

function emptyAssignments(roles: CastingRoleOption[]): CastAssignment[] {
  return roles.map((role) => ({ roleId: role.id, assignee: `seat-${role.id}` }));
}

export function AgentCastingPanel({
  roles,
  availableAgents,
  selectedPlayerRoleId,
  onPlayerRoleChange,
  onEnsembleChange,
  onCastChange,
}: AgentCastingPanelProps) {
  const [assignments, setAssignments] = React.useState<CastAssignment[]>(() => emptyAssignments(roles));
  const [selectedSeatIndex, setSelectedSeatIndex] = React.useState<number | null>(null);
  const [agentPickerOpen, setAgentPickerOpen] = React.useState(false);
  const [templatesOpen, setTemplatesOpen] = React.useState(true);

  const playerCount = roles.length;
  const filteredTemplates = CASTING_TEMPLATES.filter((template) => template.playerCount === playerCount);

  React.useEffect(() => {
    setAssignments((prev) => {
      const next = roles.map((role) => {
        const existing = prev.find((item) => item.roleId === role.id);
        return existing || { roleId: role.id, assignee: `seat-${role.id}` };
      });
      return next;
    });
  }, [roles]);

  const syncParent = React.useCallback((next: CastAssignment[]) => {
    onCastChange(next);
    const filled = roles.length > 0 && roles.every((role) => {
      const item = next.find((entry) => entry.roleId === role.id);
      return item ? isSeatFilled(item.assignee, availableAgents) : false;
    });
    onEnsembleChange(filled);
  }, [availableAgents, onCastChange, onEnsembleChange, roles]);

  React.useEffect(() => {
    syncParent(assignments);
  }, [assignments, syncParent]);

  const getSeatPosition = (index: number, total: number) => {
    const angle = -90 + (360 / total) * index;
    const radians = (angle * Math.PI) / 180;
    return {
      left: `${50 + 44 * Math.cos(radians)}%`,
      top: `${50 + 44 * Math.sin(radians)}%`,
    };
  };

  const applyTemplate = (template: CastingTemplate) => {
    const keys = filterTemplateAgentKeys(template.agentKeys, availableAgents);
    const next = roles.map((role, index) => ({
      roleId: role.id,
      assignee: keys[index] || `seat-${role.id}`,
    }));
    setAssignments(next);
    onPlayerRoleChange("");
  };

  const updateAssignment = (index: number, assignee: string) => {
    const next = assignments.map((item, idx) => (idx === index ? { ...item, assignee } : item));
    setAssignments(next);
  };

  const handleAgentPick = (agentKey: string) => {
    if (selectedSeatIndex === null) return;
    if (roles[selectedSeatIndex]?.id === selectedPlayerRoleId) {
      onPlayerRoleChange("");
    }
    updateAssignment(selectedSeatIndex, agentKey);
    setAgentPickerOpen(false);
    setSelectedSeatIndex(null);
  };

  const handlePlayMyself = () => {
    if (selectedSeatIndex === null) return;
    const roleId = roles[selectedSeatIndex]?.id || "";
    const next = assignments.map((item, index) => {
      if (index === selectedSeatIndex) return { ...item, assignee: HUMAN_PLAYER };
      if (item.assignee === HUMAN_PLAYER) return { ...item, assignee: `seat-${item.roleId}` };
      return item;
    });
    setAssignments(next);
    onPlayerRoleChange(roleId);
    setAgentPickerOpen(false);
    setSelectedSeatIndex(null);
  };

  const resolveAgent = (assignee: string) =>
    availableAgents.find((agent) => agent.key === assignee && !agent.key.startsWith("persona-"));

  const selectableAgents = availableAgents.filter((agent) => !agent.key.startsWith("persona-"));

  return (
    <Stack gap="lg">
      {filteredTemplates.length > 0 && (
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" mb={templatesOpen ? "md" : 0} style={{ cursor: "pointer" }} onClick={() => setTemplatesOpen((o) => !o)}>
            <Box>
              <Text className="monospace-label" size="xs" c="dimmed">ensemble templates</Text>
              <Title order={3}>推荐搭配</Title>
              <Text size="xs" c="red.2" mt="sm">点击卡片一键填充圆桌（{playerCount} 席）</Text>
            </Box>
            <Badge color="gray" variant="light" style={{ cursor: "pointer" }}>{templatesOpen ? "收起" : "展开"}</Badge>
          </Group>
          <Collapse in={templatesOpen}>
            <Box className="game-casting-template-grid">
              {filteredTemplates.map((template) => (
              <Card
                key={template.key}
                radius="lg"
                className="tone-panel"
                p="md"
                style={{ cursor: "pointer" }}
                onClick={() => applyTemplate(template)}
              >
                <Group justify="space-between" mb="sm">
                  <Text fw={800}>{template.name}</Text>
                  <Badge color={template.type === "高玩局" ? "red" : template.type === "小白局" ? "green" : "orange"}>
                    {template.type}
                  </Badge>
                </Group>
                <Text size="sm" c="dimmed" lh={1.6}>{template.description}</Text>
                <Group gap={6} mt="md" wrap="wrap">
                  {templateAgentDisplayNames(template.agentKeys, availableAgents).map((label) => (
                    <Badge key={label} variant="light" color="blue">{label}</Badge>
                  ))}
                </Group>
              </Card>
                ))}
              </Box>
            </Collapse>
          </Paper>
      )}

      <Paper radius="xl" p="xl" className="industrial-card">
        <Stack gap="lg" align="center">
          <Group justify="space-between" w="100%" wrap="wrap">
            <Box>
              <Text className="monospace-label" size="xs" c="dimmed">role casting table</Text>
              <Title order={3}>剧本角色圆桌</Title>
              <Text size="xs" c="dimmed" mt={4}>
                锈铁为 6 人本：5 名在席嫌疑人 + 受害者顾沉（由 DM 叙述，不占席位）
              </Text>
            </Box>
            <Badge color="red" variant="light">{playerCount} 个角色席位</Badge>
          </Group>
          <Box className="round-table">
            <Box className="round-table__surface" />
            {roles.map((role, index) => {
              const assignee = assignments[index]?.assignee || `seat-${role.id}`;
              const agent = resolveAgent(assignee);
              const isHuman = assignee === HUMAN_PLAYER;
              const position = getSeatPosition(index, playerCount);
              const rolePortrait = characterPortraits[role.role];
              const agentPortrait = agent ? agentPortraits[agent.name] : undefined;
              const showPortrait = Boolean(rolePortrait) && (isHuman || !agent);
              const showAgentPortrait = !isHuman && agent && Boolean(agentPortrait);
              return (
                <Box
                  key={role.id}
                  className="round-table__seat"
                  style={{ left: position.left, top: position.top }}
                  onClick={() => {
                    setSelectedSeatIndex(index);
                    setAgentPickerOpen(true);
                  }}
                >
                  {showAgentPortrait ? (
                    <Avatar src={agentPortrait} size={52} radius="xl" className="round-table__role" imageProps={{ style: { objectPosition: "top" } }} />
                  ) : showPortrait ? (
                    <Avatar src={rolePortrait} size={52} radius="xl" className="round-table__role" imageProps={{ style: { objectPosition: "top" } }} />
                  ) : (
                    <Avatar
                      size={52}
                      radius="xl"
                      color={isHuman ? "orange" : agent ? AVATAR_COLORS[index % AVATAR_COLORS.length] : "gray"}
                      className="round-table__role"
                    >
                      {agent?.name.slice(0, 1) || role.role.slice(0, 1)}
                    </Avatar>
                  )}
                  <Text size="xs" ta="center" mt={4} lineClamp={1} c={isHuman ? "orange.3" : undefined}>
                    {isHuman ? "我 · 真人玩家" : agent ? `${agent.name} · ${role.role}` : role.role}
                  </Text>
                </Box>
              );
            })}
          </Box>
          <Text size="sm" c="dimmed">
            点击席位选择 Agent。全 AI 局：5 席均选 Agent；若你亲自扮演某嫌疑人，其余 {Math.max(playerCount - 1, 0)} 席选 Agent。
          </Text>
          {selectableAgents.length < playerCount && (
            <Text size="sm" c="orange">
              当前仅有 {selectableAgents.length} 个可用陪玩 Agent，本剧本建议至少 {playerCount} 个（全 AI）或 {Math.max(playerCount - 1, 0)} 个（你扮演 1 席）。
            </Text>
          )}
          <Paper radius="lg" p="md" w="100%" className="tone-panel">
            <Group justify="space-between" mb="sm">
              <Text fw={700}>可用陪玩 Agent</Text>
              <Badge color="blue" variant="light">{selectableAgents.length} 位在线</Badge>
            </Group>
            <ScrollArea mah={200} offsetScrollbars>
              <Group gap="sm" wrap="wrap">
              {selectableAgents.map((agent, index) => (
                <Paper key={agent.key} p="xs" radius="md" withBorder style={{ minWidth: 120 }}>
                  <Group gap="xs" wrap="nowrap">
                    {agentPortraits[agent.name] ? (
                      <Avatar src={agentPortraits[agent.name]} size={28} radius="xl" imageProps={{ style: { objectPosition: "top" } }} />
                    ) : (
                      <Avatar size={28} radius="xl" color={AVATAR_COLORS[index % AVATAR_COLORS.length]}>
                        {agent.name.slice(0, 1)}
                      </Avatar>
                    )}
                    <Box style={{ flex: 1, minWidth: 0 }}>
                      <Text size="sm" fw={700} lineClamp={1}>{agent.name}</Text>
                      <Text size="xs" c="dimmed" lineClamp={1}>{agent.highlight}</Text>
                    </Box>
                  </Group>
                </Paper>
              ))}
            </Group>
            </ScrollArea>
          </Paper>
        </Stack>
      </Paper>

      <Modal
        opened={agentPickerOpen}
        onClose={() => {
          setAgentPickerOpen(false);
          setSelectedSeatIndex(null);
        }}
        title="选择角色扮演者"
        radius="xl"
        size="xl"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
      >
        {selectedSeatIndex !== null && roles[selectedSeatIndex] && (
          <Box className="game-casting-picker">
            <Paper radius="xl" p="lg" className="game-casting-role-detail">
              <Box className="game-casting-role-portrait">
                {characterPortraits[roles[selectedSeatIndex].role] ? (
                  <img
                    src={characterPortraits[roles[selectedSeatIndex].role]}
                    alt={roles[selectedSeatIndex].role}
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", objectPosition: "top" }}
                  />
                ) : (
                  <Text c="dimmed">角色立绘占位</Text>
                )}
              </Box>
              <Title order={2} mt="lg">{roles[selectedSeatIndex].role}</Title>
              <Text fw={700} c="orange.3" mt={4}>{roles[selectedSeatIndex].publicIdentity}</Text>
              <Text c="dimmed" lh={1.75} mt="md">{roles[selectedSeatIndex].background}</Text>
            </Paper>

            <Stack gap="sm">
              <Card radius="lg" className="game-casting-human" p="md" onClick={handlePlayMyself}>
                <Group justify="space-between">
                  <Group gap="sm">
                    <Avatar color="orange">我</Avatar>
                    <Box>
                      <Text fw={800}>由我扮演这个角色</Text>
                      <Text size="xs" c="dimmed">其余席位需分配给陪玩 Agent</Text>
                    </Box>
                  </Group>
                  <Badge color="orange" variant="light">真人玩家</Badge>
                </Group>
              </Card>
              <Box className="game-casting-agent-list">
                {selectableAgents.length === 0 ? (
                  <Text c="dimmed" size="sm">暂无可用陪玩 Agent，请先在 Agent 面板注册。</Text>
                ) : (
                  selectableAgents.map((agent, index) => (
                    <Card
                      key={agent.key}
                      radius="lg"
                      className="tone-panel game-casting-agent-option"
                      p="md"
                      onClick={() => handleAgentPick(agent.key)}
                    >
                      <Group justify="space-between">
                        <Group gap="sm">
                          {agentPortraits[agent.name] ? (
                            <Avatar src={agentPortraits[agent.name]} radius="xl" imageProps={{ style: { objectPosition: "top" } }} />
                          ) : (
                            <Avatar color={AVATAR_COLORS[index % AVATAR_COLORS.length]}>{agent.name.slice(0, 1)}</Avatar>
                          )}
                          <Box>
                            <Text fw={700}>{agent.name}</Text>
                            <Text size="xs" c="dimmed">{agent.highlight}</Text>
                          </Box>
                        </Group>
                        <Badge variant="light" color="blue">陪玩 Agent</Badge>
                      </Group>
                    </Card>
                  ))
                )}
              </Box>
            </Stack>
          </Box>
        )}
      </Modal>
    </Stack>
  );
}
