import React from "react";
import {
  Avatar,
  Badge,
  Box,
  Card,
  Group,
  Modal,
  Paper,
  Stack,
  Text,
  Title,
} from "@mantine/core";

// ============================
// 角色立绘
// ============================

const characterPortraits: Record<string, string> = {
  "周野": new URL("../Character/周野.png", import.meta.url).href,
  "顾沉": new URL("../Character/顾沉.png", import.meta.url).href,
  "沈禾": new URL("../Character/沈禾.png", import.meta.url).href,
  "周岚": new URL("../Character/周岚.png", import.meta.url).href,
  "秦野": new URL("../Character/秦野.png", import.meta.url).href,
};

type CastingAgent = {
  key: string;
  name: string;
  highlight: string;
};

type CastingRole = {
  id: string;
  role: string;
  publicIdentity: string;
  background: string;
  tags: string[];
  color: string;
};

type CastingTemplate = {
  key: string;
  name: string;
  type: "高玩局" | "小白局" | "混合局";
  playerCount: number;
  agentKeys: string[];
  description: string;
};

const CASTING_AGENTS: CastingAgent[] = [
  { key: "white-crow", name: "白鸦", highlight: "推理专精" },
  { key: "echo", name: "回声", highlight: "控场大师" },
  { key: "paper-owl", name: "纸鸮", highlight: "情绪织网" },
  { key: "flint", name: "燧石", highlight: "对抗核心" },
  { key: "luna-moth", name: "月蛾", highlight: "创意引擎" },
  { key: "night-cicada", name: "夜蝉", highlight: "逻辑引擎" },
];

const CASTING_TEMPLATES: CastingTemplate[] = [
  {
    key: "high-level-4",
    name: "硬核四座",
    type: "高玩局",
    playerCount: 4,
    agentKeys: ["white-crow", "flint", "night-cicada", "iron-judge"],
    description: "推理专精、对抗核心、逻辑引擎与铁面控场，适合高难度硬核推理本。",
  },
  {
    key: "beginner-6",
    name: "新手六座",
    type: "小白局",
    playerCount: 6,
    agentKeys: ["paper-owl", "candle-core", "white-crow", "luna-moth", "echo", "mist-harbor"],
    description: "覆盖情绪引导、新手教学、推理、创意、控场和氛围能力。",
  },
  {
    key: "balanced-5",
    name: "均衡五座",
    type: "混合局",
    playerCount: 5,
    agentKeys: ["echo", "white-crow", "paper-owl", "flint", "luna-moth"],
    description: "控场、推理、情感、对抗与创意均衡，适合大多数中等难度剧本。",
  },
  {
    key: "reasoning-5",
    name: "推理五座",
    type: "高玩局",
    playerCount: 5,
    agentKeys: ["white-crow", "night-cicada", "flint", "echo", "luna-moth"],
    description: "强化时间线、证据链和交叉追问，同时保留一名场面推进 Agent。",
  },
  {
    key: "story-5",
    name: "沉浸五座",
    type: "小白局",
    playerCount: 5,
    agentKeys: ["paper-owl", "luna-moth", "white-crow", "echo", "night-cicada"],
    description: "以情绪承接和角色表达为主，由推理 Agent 在关键节点补充线索。",
  },
  {
    key: "competitive-6",
    name: "竞技六座",
    type: "高玩局",
    playerCount: 6,
    agentKeys: ["flint", "iron-judge", "night-cicada", "white-crow", "shadow-weaver", "echo"],
    description: "强调高对抗、严格主持、逻辑分析与场面推进。",
  },
  {
    key: "story-4",
    name: "故事四座",
    type: "小白局",
    playerCount: 4,
    agentKeys: ["paper-owl", "candle-core", "mist-harbor", "luna-moth"],
    description: "专注情绪、引导、氛围与创意的沉浸式故事体验。",
  },
];

const AVATAR_COLORS = ["red", "orange", "grape", "blue", "cyan", "teal", "pink", "yellow"];
const HUMAN_PLAYER = "human-player";

function emptySeats(count: number) {
  return Array.from({ length: count }, (_, index) => `seat-${index}`);
}

type AgentCastingPanelProps = {
  roles: CastingRole[];
  selectedPlayerRoleId: string;
  onPlayerRoleChange: (roleId: string) => void;
};

export function AgentCastingPanel({
  roles,
  selectedPlayerRoleId,
  onPlayerRoleChange,
}: AgentCastingPanelProps) {
  const playerCount = roles.length;
  const [ensembleSeats, setEnsembleSeats] = React.useState<string[]>(() => emptySeats(playerCount));
  const [selectedSeat, setSelectedSeat] = React.useState<number | null>(null);
  const [agentPickerOpen, setAgentPickerOpen] = React.useState(false);

  const filteredTemplates = CASTING_TEMPLATES.filter(
    (template) => template.playerCount === playerCount,
  );

  React.useEffect(() => {
    setEnsembleSeats(emptySeats(playerCount));
  }, [playerCount]);

  const applyTemplate = (template: CastingTemplate) => {
    setEnsembleSeats([...template.agentKeys]);
    onPlayerRoleChange("");
  };

  const handleAgentPick = (agentKey: string) => {
    if (selectedSeat !== null) {
      if (roles[selectedSeat]?.id === selectedPlayerRoleId) {
        onPlayerRoleChange("");
      }
      setEnsembleSeats((current) => {
        const next = [...current];
        next[selectedSeat] = agentKey;
        return next;
      });
    }
    setAgentPickerOpen(false);
    setSelectedSeat(null);
  };

  const handlePlayMyself = () => {
    if (selectedSeat === null) return;
    setEnsembleSeats((current) =>
      current.map((seat, index) => {
        if (index === selectedSeat) return HUMAN_PLAYER;
        return seat === HUMAN_PLAYER ? `seat-${index}` : seat;
      }),
    );
    onPlayerRoleChange(roles[selectedSeat]?.id || "");
    setAgentPickerOpen(false);
    setSelectedSeat(null);
  };

  const getSeatPosition = (index: number, total: number) => {
    const angle = -90 + (360 / total) * index;
    const radians = (angle * Math.PI) / 180;
    return {
      left: `${50 + 44 * Math.cos(radians)}%`,
      top: `${50 + 44 * Math.sin(radians)}%`,
    };
  };

  return (
    <Stack gap="lg">
      <Paper radius="xl" p="xl" className="industrial-card">
        <Stack gap="lg" align="center">
          <Group justify="space-between" w="100%" wrap="wrap">
            <Box>
              <Text className="monospace-label" size="xs" c="dimmed">role casting table</Text>
              <Title order={3}>剧本角色圆桌</Title>
            </Box>
            <Badge color="red" variant="light">{playerCount} 个角色席位</Badge>
          </Group>
          <Box className="round-table">
            <Box className="round-table__surface" />
            {ensembleSeats.map((agentKey, index) => {
              const agent = CASTING_AGENTS.find((item) => item.key === agentKey);
              const isHuman = agentKey === HUMAN_PLAYER;
              const position = getSeatPosition(index, playerCount);
              const roleName = roles[index]?.role || `角色 ${index + 1}`;
              return (
                <Box
                  key={`${index}-${agentKey}`}
                  className="round-table__seat"
                  style={{ left: position.left, top: position.top }}
                  onClick={() => {
                    setSelectedSeat(index);
                    setAgentPickerOpen(true);
                  }}
                >
                  {(() => {
                    const rolePortrait = characterPortraits[roleName];
                    const showPortrait = rolePortrait && (!agent || isHuman);
                    return showPortrait ? (
                      <Avatar src={rolePortrait} size={52} radius="xl" className="round-table__role" imageProps={{ style: { objectPosition: "top" } }} />
                    ) : (
                      <Avatar
                        size={52}
                        radius="xl"
                        color={isHuman ? "orange" : agent ? AVATAR_COLORS[agentKey.charCodeAt(0) % AVATAR_COLORS.length] : "gray"}
                        className="round-table__role"
                      >
                        {roleName}
                      </Avatar>
                    );
                  })()}
                  <Text size="xs" ta="center" mt={4} lineClamp={1} c={isHuman ? "orange.3" : undefined}>
                    {isHuman ? "我 · 真人玩家" : agent ? agent.name : roleName}
                  </Text>
                </Box>
              );
            })}
          </Box>
          <Text size="sm" c="dimmed">点击 Agent 空位或已有座位，可选择和更换 Agent。</Text>
        </Stack>
      </Paper>

      <Paper radius="xl" p="lg" className="industrial-card">
        <Group justify="space-between" mb="md">
          <Box>
            <Text className="monospace-label" size="xs" c="dimmed">ensemble templates</Text>
            <Title order={3}>推荐搭配</Title>
          </Box>
         
        </Group>
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
              <Text size="xs" c="red.2" mt="sm">点击卡片一键填充圆桌</Text>
              <Group gap={4} mt="md">
                {template.agentKeys.map((key) => {
                  const agent = CASTING_AGENTS.find((item) => item.key === key);
                  return (
                    <Avatar key={key} size={28} radius="xl" color={AVATAR_COLORS[key.charCodeAt(0) % 8]}>
                      {agent?.name[0] || "?"}
                    </Avatar>
                  );
                })}
              </Group>
            </Card>
          ))}
        </Box>
      </Paper>

      <Modal
        opened={agentPickerOpen}
        onClose={() => {
          setAgentPickerOpen(false);
          setSelectedSeat(null);
        }}
        title="选择角色扮演者"
        radius="xl"
        size="xl"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
      >
        {selectedSeat !== null && (
          <Box className="game-casting-picker">
            <Paper radius="xl" p="lg" className="game-casting-role-detail">
              <Box className="game-casting-role-portrait">
                {characterPortraits[roles[selectedSeat]?.role] ? (
                  <img
                    src={characterPortraits[roles[selectedSeat]?.role]}
                    alt={roles[selectedSeat]?.role}
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", objectPosition: "top" }}
                  />
                ) : (
                  <>
                    <Text className="monospace-label" size="xs" c="dimmed">character portrait</Text>
                    <Text c="dimmed">角色立绘占位</Text>
                  </>
                )}
              </Box>
              <Title order={2} mt="lg">{roles[selectedSeat]?.role}</Title>
              <Text fw={700} c="orange.3" mt={4}>{roles[selectedSeat]?.publicIdentity}</Text>
              <Text c="dimmed" lh={1.75} mt="md">{roles[selectedSeat]?.background}</Text>
              <Group gap={5} mt="md">
                {roles[selectedSeat]?.tags.map((tag) => (
                  <Badge key={tag} size="sm" variant="light" color="gray">{tag}</Badge>
                ))}
              </Group>
            </Paper>

            <Stack gap="sm">
              <Box>
                <Text className="monospace-label" size="xs" c="dimmed">casting options</Text>
                <Title order={3}>选择陪玩 Agent</Title>
              </Box>
              <Card
                radius="lg"
                className={selectedPlayerRoleId === roles[selectedSeat]?.id ? "game-casting-human is-selected" : "game-casting-human"}
                p="md"
                onClick={handlePlayMyself}
              >
                <Group justify="space-between">
                  <Group gap="sm">
                    <Avatar color="orange">我</Avatar>
                    <Box>
                      <Text fw={800}>由我扮演这个角色</Text>
                      <Text size="xs" c="dimmed">将此席位设为真人玩家</Text>
                    </Box>
                  </Group>
                  <Badge color="orange" variant="light">真人玩家</Badge>
                </Group>
              </Card>
              <Box className="game-casting-agent-list">
                {CASTING_AGENTS.map((agent) => (
                  <Card
                    key={agent.key}
                    radius="lg"
                    className="tone-panel game-casting-agent-option"
                    p="md"
                    onClick={() => handleAgentPick(agent.key)}
                  >
                    <Group justify="space-between">
                      <Group gap="sm">
                        <Avatar color={AVATAR_COLORS[agent.key.charCodeAt(0) % 8]}>{agent.name[0]}</Avatar>
                        <Box>
                          <Text fw={700}>{agent.name}</Text>
                          <Text size="xs" c="dimmed">{agent.highlight}</Text>
                        </Box>
                      </Group>
                      <Badge variant="light" color="blue">陪玩 Agent</Badge>
                    </Group>
                  </Card>
                ))}
              </Box>
            </Stack>
          </Box>
        )}
      </Modal>
    </Stack>
  );
}
