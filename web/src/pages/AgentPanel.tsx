/**
 * EvoMap Murder Game - Agent Panel
 *
 * 陪玩 Agent 广场 + DM-Agent 广场 + 操作中心。
 */

import React from "react";
import {
  Badge,
  Button,
  Card,
  Divider,
  Grid,
  Group,
  Paper,
  Rating,
  SegmentedControl,
  Select,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconBolt,
  IconHeart,
  IconMessage2,
  IconRobot,
  IconSearch,
  IconShieldCheck,
  IconStars,
  IconUserStar,
} from "@tabler/icons-react";

import { StudioShell } from "./StudioShell";

type CompanionAgent = {
  key: string;
  name: string;
  vibe: string;
  style: string;
  genius: string[];
  personality: string[];
  scriptTypes: string[];
  activeLevel: "低" | "中" | "高";
  rating: number;
  history: string;
  newTag: string;
  roleMatch: string;
  reason: string;
};

type DMAgent = {
  key: string;
  name: string;
  vibe: string;
  pace: string;
  focus: string[];
  strengths: string[];
  promptStyle: string;
  fairness: string;
  rating: number;
  runs: string;
  recentGrowth: string;
  detail: string;
};

const companionAgents: CompanionAgent[] = [
  {
    key: "white-crow",
    name: "白鸦",
    vibe: "克制、清冷、会稳稳接话",
    style: "适合推理链条和关键节点补刀",
    genius: ["推理", "线索整理", "新手引导"],
    personality: ["冷静", "耐心", "不抢戏"],
    scriptTypes: ["推理本", "新手局", "中等沉浸"],
    activeLevel: "中",
    rating: 4.9,
    history: "历史协作 142 局",
    newTag: "新增「反证整理」标签",
    roleMatch: "更适合侦探位、辅助位与观察者位",
    reason: "能把复杂信息压成清晰语义，适合谜案型剧本。",
  },
  {
    key: "echo",
    name: "回声",
    vibe: "轻松、会抛梗、能带动气氛",
    style: "适合欢乐局和节奏推进",
    genius: ["控场", "表演", "推进"],
    personality: ["外向", "有存在感", "会接梗"],
    scriptTypes: ["阵营本", "欢乐局", "机制本"],
    activeLevel: "高",
    rating: 4.8,
    history: "历史协作 98 局",
    newTag: "新增「推进型」标签",
    roleMatch: "适合前置位、推动位、串联位",
    reason: "在不抢关键叙述的前提下，能把局面快速往前推。",
  },
  {
    key: "paper-owl",
    name: "纸鸮",
    vibe: "温和、沉浸、情绪层次细",
    style: "擅长情感本与角色关系铺垫",
    genius: ["情绪", "代入", "细腻表达"],
    personality: ["温柔", "共情强", "慢热"],
    scriptTypes: ["情感本", "沉浸本", "旧宅类"],
    activeLevel: "低",
    rating: 4.9,
    history: "历史协作 176 局",
    newTag: "新增「关系补全」标签",
    roleMatch: "适合情感位、羁绊位与线索收束位",
    reason: "可以把人物关系像织网一样慢慢铺开。",
  },
  {
    key: "flint",
    name: "燧石",
    vibe: "锋利、果断、推进力强",
    style: "适合压力局和高对抗局",
    genius: ["博弈", "对抗", "抢节奏"],
    personality: ["直接", "有压迫感", "执行强"],
    scriptTypes: ["阵营本", "机制本", "硬核推理"],
    activeLevel: "高",
    rating: 4.7,
    history: "历史协作 126 局",
    newTag: "新增「压迫型推进」标签",
    roleMatch: "适合核心对抗位、站队位与压盘位",
    reason: "适合需要强推和压节奏的桌子。",
  },
];

const dmAgents: DMAgent[] = [
  {
    key: "mist-harbor",
    name: "雾港主理人",
    vibe: "氛围强、低语感、慢慢收口",
    pace: "慢",
    focus: ["情感本", "沉浸局", "新手局"],
    strengths: ["氛围营造", "提示克制", "复盘清晰"],
    promptStyle: "提示偏间接，避免直接揭底",
    fairness: "违规率极低，控场稳定",
    rating: 4.9,
    runs: "主持 188 局",
    recentGrowth: "最近新增「低压引导」标签",
    detail: "适合想要沉浸、又不希望节奏被打碎的剧本。",
  },
  {
    key: "iron-judge",
    name: "铁幕裁判",
    vibe: "冷静、硬朗、节奏精确",
    pace: "快",
    focus: ["硬核推理", "阵营本", "机制本"],
    strengths: ["控场", "时间管理", "规则解释"],
    promptStyle: "提示直接，适合高强度推理盘",
    fairness: "几乎不剧透，判定明确",
    rating: 4.8,
    runs: "主持 214 局",
    recentGrowth: "最近获得「高压盘面管理」标签",
    detail: "适合需要严格节奏与清晰规则的桌子。",
  },
  {
    key: "candle-core",
    name: "暮烛引导员",
    vibe: "温柔、细致、会照顾新手",
    pace: "中",
    focus: ["新手局", "情感本", "长局"],
    strengths: ["新手教学", "提示节制", "复盘引导"],
    promptStyle: "会先给方向，再给细节",
    fairness: "兼顾剧本推进和体验保护",
    rating: 4.9,
    runs: "主持 167 局",
    recentGrowth: "新增「教学模式」标签",
    detail: "适合第一次上桌或有较多新手的房间。",
  },
];

const companionFilters = ["全部", "低", "中", "高"];
const dmPaceFilters = ["全部", "快", "中", "慢"];
const scriptTypeFilters = ["全部", "推理本", "情感本", "机制本", "阵营本"];

function AgentPanel() {
  const [mode, setMode] = React.useState("companion");
  const [query, setQuery] = React.useState("");
  const [activeCompanion, setActiveCompanion] = React.useState(companionAgents[0].key);
  const [activeDm, setActiveDm] = React.useState(dmAgents[0].key);
  const [activeLevel, setActiveLevel] = React.useState("全部");
  const [activeScriptType, setActiveScriptType] = React.useState("全部");
  const [dmPace, setDmPace] = React.useState("全部");

  const companionList = companionAgents.filter((agent) => {
    const hitQuery =
      agent.name.includes(query) ||
      agent.vibe.includes(query) ||
      agent.genius.some((tag) => tag.includes(query)) ||
      agent.scriptTypes.some((tag) => tag.includes(query));
    const hitLevel = activeLevel === "全部" || agent.activeLevel === activeLevel;
    const hitScriptType =
      activeScriptType === "全部" || agent.scriptTypes.includes(activeScriptType);
    return hitQuery && hitLevel && hitScriptType;
  });

  const dmList = dmAgents.filter((agent) => {
    const hitQuery =
      agent.name.includes(query) ||
      agent.vibe.includes(query) ||
      agent.focus.some((tag) => tag.includes(query)) ||
      agent.strengths.some((tag) => tag.includes(query));
    const hitPace = dmPace === "全部" || agent.pace === dmPace;
    return hitQuery && hitPace;
  });

  const selectedCompanion =
    companionList.find((agent) => agent.key === activeCompanion) || companionList[0];
  const selectedDm = dmList.find((agent) => agent.key === activeDm) || dmList[0];

  return (
    <StudioShell
      title="Agent 广场"
      subtitle="这里把陪玩 Agent 和 DM-Agent 拆成两条并行谱系：一边看性格、主动程度和擅长类型，一边看节奏、提示方式和复盘能力。"
      eyebrow="agents / dm / ensemble"
      stats={[
        { label: "陪玩 Agent", value: `${companionAgents.length}` },
        { label: "DM-Agent", value: `${dmAgents.length}` },
        { label: "热门标签", value: "12+" },
        { label: "可操作项", value: "收藏 / 关注 / 邀请" },
      ]}
    >
      <Stack gap="lg">
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="flex-start" wrap="wrap">
            <Stack gap={6} style={{ maxWidth: 760 }}>
              <Text className="monospace-label" size="xs" c="orange.3">
                agent bazaar
              </Text>
              <Title order={2}>陪玩与 DM 的双广场</Title>
              <Text c="dimmed" lh={1.75}>
                通过搜索、能力标签、性格标签、擅长剧本类型、主动程度和用户评分，快速筛选出适合当前房间的 Agent。
              </Text>
            </Stack>

            <SegmentedControl
              value={mode}
              onChange={setMode}
              data={[
                { label: "陪玩Agent", value: "companion" },
                { label: "DM-Agent", value: "dm" },
                { label: "阵容推荐", value: "ensemble" },
              ]}
            />
          </Group>
        </Paper>

        <Paper radius="xl" p="lg" className="industrial-card">
          <Group align="center" justify="space-between" wrap="wrap">
            <Group gap="sm" wrap="wrap">
              <TextInput
                placeholder="搜索 Agent 名称 / 标签 / 风格"
                leftSection={<IconSearch size={16} />}
                value={query}
                onChange={(event) => setQuery(event.currentTarget.value)}
                radius="xl"
              />
              {mode !== "dm" ? (
                <Select
                  data={companionFilters}
                  value={activeLevel}
                  onChange={(value) => setActiveLevel(value || "全部")}
                  label="主动程度"
                />
              ) : null}
              {mode !== "companion" ? (
                <Select
                  data={dmPaceFilters}
                  value={dmPace}
                  onChange={(value) => setDmPace(value || "全部")}
                  label="主持节奏"
                />
              ) : null}
              {mode !== "dm" ? (
                <Select
                  data={scriptTypeFilters}
                  value={activeScriptType}
                  onChange={(value) => setActiveScriptType(value || "全部")}
                  label="擅长剧本"
                />
              ) : null}
            </Group>
            <Group gap="xs">
              <Badge variant="light" color="orange" leftSection={<IconStars size={14} />}>
                热门
              </Badge>
              <Badge variant="light" color="gray" leftSection={<IconUserStar size={14} />}>
                新晋
              </Badge>
              <Badge variant="light" color="blue" leftSection={<IconHeart size={14} />}>
                常用助手推荐
              </Badge>
            </Group>
          </Group>
        </Paper>

        {mode === "companion" ? (
          <Grid gutter="lg">
            <Grid.Col span={{ base: 12, lg: 3 }}>
              <Stack gap="md">
                {companionList.map((agent) => (
                  <Card
                    key={agent.key}
                    radius="xl"
                    className="industrial-card"
                    p="md"
                    style={{
                      cursor: "pointer",
                      borderColor:
                        agent.key === selectedCompanion?.key
                          ? "rgba(255, 165, 84, 0.5)"
                          : undefined,
                    }}
                    onClick={() => setActiveCompanion(agent.key)}
                  >
                    <Group justify="space-between" align="flex-start">
                      <Stack gap={4}>
                        <Text className="monospace-label" size="xs" c="dimmed">
                          companion
                        </Text>
                        <Title order={4}>{agent.name}</Title>
                      </Stack>
                      <Badge variant="filled" color="blue">
                        {agent.activeLevel}主动
                      </Badge>
                    </Group>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {agent.vibe}
                    </Text>
                    <Group gap="xs" mt="md">
                      {agent.genius.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="light" color="gray">
                          {tag}
                        </Badge>
                      ))}
                    </Group>
                  </Card>
                ))}
              </Stack>
            </Grid.Col>

            <Grid.Col span={{ base: 12, lg: 5 }}>
              {selectedCompanion ? (
                <Stack gap="md">
                  <Paper radius="xl" p="lg" className="industrial-card">
                    <Group justify="space-between" align="flex-start">
                      <Stack gap={4}>
                        <Text className="monospace-label" size="xs" c="orange.3">
                          companion detail
                        </Text>
                        <Title order={3}>{selectedCompanion.name}</Title>
                        <Text c="dimmed">{selectedCompanion.vibe}</Text>
                      </Stack>
                      <Badge variant="light" color="orange">
                        {selectedCompanion.newTag}
                      </Badge>
                    </Group>
                    <Divider my="md" color="rgba(255,255,255,0.08)" />
                    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>说话 / 游戏风格</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          {selectedCompanion.style}
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>适合角色类型</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          {selectedCompanion.roleMatch}
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>能力标签</Text>
                        <Group gap="xs" mt="sm">
                          {selectedCompanion.genius.map((tag) => (
                            <Badge key={tag} variant="light" color="orange">
                              {tag}
                            </Badge>
                          ))}
                        </Group>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>性格标签</Text>
                        <Group gap="xs" mt="sm">
                          {selectedCompanion.personality.map((tag) => (
                            <Badge key={tag} variant="light" color="gray">
                              {tag}
                            </Badge>
                          ))}
                        </Group>
                      </Card>
                    </SimpleGrid>

                    <Group mt="md" justify="space-between" wrap="wrap">
                      <Text size="sm" c="dimmed">
                        擅长剧本：{selectedCompanion.scriptTypes.join(" / ")}
                      </Text>
                      <Text size="sm" c="dimmed">
                        {selectedCompanion.history}
                      </Text>
                    </Group>
                    <Rating value={selectedCompanion.rating} fractions={2} readOnly mt="sm" />
                    <Text size="sm" c="dimmed" mt="sm">
                      推荐理由：{selectedCompanion.reason}
                    </Text>
                  </Paper>

                  <Paper radius="xl" p="lg" className="industrial-card">
                    <Text className="monospace-label" size="xs" c="dimmed">
                      actions
                    </Text>
                    <SimpleGrid cols={{ base: 2, md: 3 }} spacing="sm" mt="sm">
                      {[
                        "收藏 Agent",
                        "关注 Agent",
                        "邀请进房间",
                        "设为常用",
                        "查看共同游玩",
                        "屏蔽 / 不再推荐",
                      ].map((item) => (
                        <Button key={item} variant="light" radius="xl" leftSection={<IconBolt size={14} />}>
                          {item}
                        </Button>
                      ))}
                    </SimpleGrid>
                  </Paper>
                </Stack>
              ) : null}
            </Grid.Col>

            <Grid.Col span={{ base: 12, lg: 4 }}>
              <Stack gap="md">
                <Paper radius="xl" p="lg" className="industrial-card">
                  <Text className="monospace-label" size="xs" c="dimmed">
                    ensemble hints
                  </Text>
                  <Stack gap="sm" mt="sm">
                    <Text fw={700}>陪玩阵容推荐维度</Text>
                    <Text size="sm" c="dimmed" lh={1.7}>
                      当前剧本所需能力、玩家风格、真人玩家特点、已选 Agent 互补性、抢话风险、是否缺少推进型 Agent。
                    </Text>
                    <Group gap="xs">
                      <Badge variant="light" color="orange">
                        互补性
                      </Badge>
                      <Badge variant="light" color="blue">
                        抢话风险
                      </Badge>
                      <Badge variant="light" color="green">
                        新手引导
                      </Badge>
                    </Group>
                  </Stack>
                </Paper>

                <Paper radius="xl" p="lg" className="industrial-card">
                  <Text className="monospace-label" size="xs" c="dimmed">
                    cooperation archive
                  </Text>
                  <Stack gap="sm" mt="sm">
                    <Text fw={700}>共同游玩记录</Text>
                    <Text size="sm" c="dimmed" lh={1.7}>
                      可查看共同玩过的剧本、默契度、历史互动数据和近期评价，帮助你判断是否适合作为常用搭档。
                    </Text>
                    <Button variant="light" radius="xl" leftSection={<IconMessage2 size={14} />}>
                      进入共同记录
                    </Button>
                  </Stack>
                </Paper>
              </Stack>
            </Grid.Col>
          </Grid>
        ) : null}

        {mode === "dm" ? (
          <Grid gutter="lg">
            <Grid.Col span={{ base: 12, lg: 3 }}>
              <Stack gap="md">
                {dmList.map((agent) => (
                  <Card
                    key={agent.key}
                    radius="xl"
                    className="industrial-card"
                    p="md"
                    style={{
                      cursor: "pointer",
                      borderColor:
                        agent.key === selectedDm?.key
                          ? "rgba(255, 165, 84, 0.5)"
                          : undefined,
                    }}
                    onClick={() => setActiveDm(agent.key)}
                  >
                    <Group justify="space-between" align="flex-start">
                      <Stack gap={4}>
                        <Text className="monospace-label" size="xs" c="dimmed">
                          dm-agent
                        </Text>
                        <Title order={4}>{agent.name}</Title>
                      </Stack>
                      <Badge variant="filled" color="red">
                        {agent.pace}节奏
                      </Badge>
                    </Group>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {agent.vibe}
                    </Text>
                  </Card>
                ))}
              </Stack>
            </Grid.Col>

            <Grid.Col span={{ base: 12, lg: 5 }}>
              {selectedDm ? (
                <Stack gap="md">
                  <Paper radius="xl" p="lg" className="industrial-card">
                    <Group justify="space-between" align="flex-start">
                      <Stack gap={4}>
                        <Text className="monospace-label" size="xs" c="orange.3">
                          dm detail
                        </Text>
                        <Title order={3}>{selectedDm.name}</Title>
                        <Text c="dimmed">{selectedDm.vibe}</Text>
                      </Stack>
                      <Badge variant="light" color="red">
                        {selectedDm.promptStyle}
                      </Badge>
                    </Group>
                    <Divider my="md" color="rgba(255,255,255,0.08)" />
                    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>主持风格</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          {selectedDm.pace}节奏，偏向{selectedDm.focus.join(" / ")}。
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>控场 / 提示</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          {selectedDm.detail}
                        </Text>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>擅长能力</Text>
                        <Group gap="xs" mt="sm">
                          {selectedDm.strengths.map((tag) => (
                            <Badge key={tag} variant="light" color="orange">
                              {tag}
                            </Badge>
                          ))}
                        </Group>
                      </Card>
                      <Card radius="lg" className="ambient-grid" p="md">
                        <Text fw={700}>公平 / 违规</Text>
                        <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                          {selectedDm.fairness}
                        </Text>
                      </Card>
                    </SimpleGrid>
                    <Group mt="md" justify="space-between" wrap="wrap">
                      <Text size="sm" c="dimmed">
                        {selectedDm.runs}
                      </Text>
                      <Text size="sm" c="dimmed">
                        {selectedDm.recentGrowth}
                      </Text>
                    </Group>
                    <Rating value={selectedDm.rating} fractions={2} readOnly mt="sm" />
                  </Paper>

                  <Paper radius="xl" p="lg" className="industrial-card">
                    <Text className="monospace-label" size="xs" c="dimmed">
                      host settings
                    </Text>
                    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="sm" mt="sm">
                      {[
                        "节奏快 / 慢",
                        "是否允许主动催场",
                        "卡住多久后提示",
                        "提示直接程度",
                        "是否需要新手教学",
                        "是否加强氛围描写",
                        "复盘详细程度",
                        "是否允许缩短非关键环节",
                      ].map((item) => (
                        <Button key={item} variant="light" radius="xl">
                          {item}
                        </Button>
                      ))}
                    </SimpleGrid>
                  </Paper>
                </Stack>
              ) : null}
            </Grid.Col>

            <Grid.Col span={{ base: 12, lg: 4 }}>
              <Stack gap="md">
                <Paper radius="xl" p="lg" className="industrial-card">
                  <Text className="monospace-label" size="xs" c="dimmed">
                    preference match
                  </Text>
                  <Stack gap="sm" mt="sm">
                    <Text fw={700}>DM 偏好设置</Text>
                    <Text size="sm" c="dimmed" lh={1.7}>
                      可以基于玩家经验、剧本类型和本局氛围，设置节奏、提示风格、教学强度和复盘粒度。
                    </Text>
                    <Group gap="xs">
                      <Badge variant="light" color="orange">
                        快节奏
                      </Badge>
                      <Badge variant="light" color="gray">
                        提示克制
                      </Badge>
                      <Badge variant="light" color="green">
                        新手教学
                      </Badge>
                    </Group>
                  </Stack>
                </Paper>

                <Paper radius="xl" p="lg" className="industrial-card">
                  <Text className="monospace-label" size="xs" c="dimmed">
                    ensemble judgment
                  </Text>
                  <Stack gap="sm" mt="sm">
                    <Text fw={700}>阵容推荐理由</Text>
                    <Text size="sm" c="dimmed" lh={1.7}>
                      系统会判断是否缺少推进型 Agent、是否存在抢话风险、是否需要新手引导型 Agent，并给出完整推荐解释。
                    </Text>
                    <Button variant="light" radius="xl" leftSection={<IconShieldCheck size={14} />}>
                      生成推荐阵容
                    </Button>
                  </Stack>
                </Paper>
              </Stack>
            </Grid.Col>
          </Grid>
        ) : null}

        {mode === "ensemble" ? (
          <Paper radius="xl" p="lg" className="industrial-card">
            <Group justify="space-between" align="flex-start" wrap="wrap">
              <Stack gap={4}>
                <Text className="monospace-label" size="xs" c="dimmed">
                  ensemble recommendation
                </Text>
                <Title order={3}>陪玩 Agent 阵容推荐</Title>
              </Stack>
              <Badge variant="light" color="orange" leftSection={<IconRobot size={14} />}>
                当前剧本所需能力 + 玩家风格 + 互补性 + 风险判断
              </Badge>
            </Group>

            <SimpleGrid cols={{ base: 1, md: 2, lg: 4 }} mt="md" spacing="md">
              {[
                "根据当前剧本所需能力推荐阵容",
                "根据用户喜欢的陪玩风格推荐阵容",
                "根据当前真人玩家特点推荐阵容",
                "根据已选 Agent 之间的互补性推荐阵容",
              ].map((item) => (
                <Card key={item} radius="lg" className="ambient-grid" p="md">
                  <Text fw={700}>{item}</Text>
                </Card>
              ))}
            </SimpleGrid>

            <Divider my="lg" color="rgba(255,255,255,0.08)" />

            <SimpleGrid cols={{ base: 1, md: 2, lg: 3 }} spacing="md">
              {[
                "判断是否存在抢话风险",
                "判断是否缺少推进型 Agent",
                "判断是否需要新手引导型 Agent",
              ].map((item) => (
                <Paper key={item} radius="lg" p="md" className="industrial-card">
                  <Text fw={700}>{item}</Text>
                </Paper>
              ))}
            </SimpleGrid>
          </Paper>
        ) : null}
      </Stack>
    </StudioShell>
  );
}

export { AgentPanel };
