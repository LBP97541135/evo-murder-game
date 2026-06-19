/**
 * EvoMap Murder Game - Script Library Page
 *
 * Figma-inspired cinematic script library.
 */

import React from "react";
import {
  Badge,
  Box,
  Button,
  Card,
  Divider,
  Grid,
  Group,
  Paper,
  Progress,
  SegmentedControl,
  Select,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconBook2,
  IconCrown,
  IconFlame,
  IconGhost,
  IconHeart,
  IconMoon,
  IconRobot,
  IconSearch,
  IconSparkles,
  IconUsers,
} from "@tabler/icons-react";

import { StudioShell } from "./StudioShell";

type ScriptCard = {
  id: string;
  title: string;
  subtitle: string;
  genre: "情感本" | "推理本" | "机制本" | "阵营本";
  difficulty: "入门" | "进阶" | "硬核";
  players: string;
  duration: string;
  rating: number;
  description: string;
  cover: string;
  tags: string[];
  emotion: number;
  inference: number;
  horror: number;
  newPlayer: number;
  hot: boolean;
  newArrival: boolean;
  recommended: boolean;
  friendsPlayed: boolean;
  supportSolo: boolean;
  supportTeam: boolean;
  dmAgents: string[];
  companionAgents: string[];
};

const scripts: ScriptCard[] = [
  {
    id: "iron-avenue",
    title: "锈铁大道",
    subtitle: "The Rusted Avenue",
    genre: "推理本",
    difficulty: "进阶",
    players: "4-6人",
    duration: "4-5小时",
    rating: 4.9,
    description: "停摆工厂、老旧宿舍与失踪名单被压在同一座锈色街区里，真相沿着管道慢慢回流。",
    cover:
      "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=900&h=1200&fit=crop&auto=format",
    tags: ["工业氛围", "线索链", "反转强", "高复盘"],
    emotion: 38,
    inference: 86,
    horror: 22,
    newPlayer: 55,
    hot: true,
    newArrival: true,
    recommended: true,
    friendsPlayed: true,
    supportSolo: false,
    supportTeam: true,
    dmAgents: ["雾港主理人", "铁幕裁判"],
    companionAgents: ["白鸦", "回声", "灯塔"],
  },
  {
    id: "black-archive",
    title: "黑箱档案馆",
    subtitle: "Black Archive",
    genre: "情感本",
    difficulty: "入门",
    players: "6-7人",
    duration: "5-6小时",
    rating: 4.8,
    description: "灰尘、烛火与被封存的家族信件，把每个人拽回一段难以解释的旧日往事。",
    cover:
      "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&h=1200&fit=crop&auto=format",
    tags: ["高沉浸", "氛围感", "情绪拉扯", "新手友好"],
    emotion: 92,
    inference: 44,
    horror: 74,
    newPlayer: 88,
    hot: true,
    newArrival: false,
    recommended: true,
    friendsPlayed: false,
    supportSolo: true,
    supportTeam: true,
    dmAgents: ["深井讲述者", "暮烛引导员"],
    companionAgents: ["纸鸦", "棱镜", "夜航"],
  },
  {
    id: "mirror-parade",
    title: "镜面游行",
    subtitle: "Mirror Parade",
    genre: "阵营本",
    difficulty: "硬核",
    players: "7-9人",
    duration: "6小时",
    rating: 4.7,
    description: "面具、反光和舞台灯一起把每次发言切成碎片，所有阵营都在互相借力与拆台。",
    cover:
      "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=900&h=1200&fit=crop&auto=format",
    tags: ["阵营博弈", "控场强", "表演位", "高对抗"],
    emotion: 54,
    inference: 78,
    horror: 18,
    newPlayer: 28,
    hot: true,
    newArrival: true,
    recommended: false,
    friendsPlayed: true,
    supportSolo: false,
    supportTeam: true,
    dmAgents: ["铁幕裁判", "节拍室主理"],
    companionAgents: ["钩索", "纸鸢", "燧石"],
  },
  {
    id: "salt-ward",
    title: "盐雾病房",
    subtitle: "Salt Ward",
    genre: "推理本",
    difficulty: "入门",
    players: "5-6人",
    duration: "3.5小时",
    rating: 4.6,
    description: "潮湿长廊与失效监控构成一场节奏温和、适合新手入门的推理练习。",
    cover:
      "https://images.unsplash.com/photo-1516738901171-8eb4fc13bd20?w=900&h=1200&fit=crop&auto=format",
    tags: ["新手友好", "节奏清晰", "信息适中"],
    emotion: 33,
    inference: 70,
    horror: 48,
    newPlayer: 92,
    hot: false,
    newArrival: true,
    recommended: true,
    friendsPlayed: false,
    supportSolo: true,
    supportTeam: true,
    dmAgents: ["暮烛引导员", "雾港主理人"],
    companionAgents: ["白鸦", "回声", "纸鸦"],
  },
  {
    id: "wolf-assembly",
    title: "狼群集会",
    subtitle: "Wolf Assembly",
    genre: "机制本",
    difficulty: "进阶",
    players: "6-8人",
    duration: "4.5小时",
    rating: 4.5,
    description: "围绕营地资源与夜巡制度展开博弈，角色推进与资源调度都要算得很细。",
    cover:
      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=900&h=1200&fit=crop&auto=format",
    tags: ["机制感", "资源调度", "夜谈博弈"],
    emotion: 26,
    inference: 61,
    horror: 35,
    newPlayer: 64,
    hot: false,
    newArrival: false,
    recommended: true,
    friendsPlayed: true,
    supportSolo: false,
    supportTeam: true,
    dmAgents: ["节拍室主理", "铁幕裁判"],
    companionAgents: ["燧石", "钩索", "回声"],
  },
  {
    id: "paper-cathedral",
    title: "纸穹教堂",
    subtitle: "Paper Cathedral",
    genre: "情感本",
    difficulty: "硬核",
    players: "6-8人",
    duration: "5.5小时",
    rating: 4.9,
    description: "一座被封死的旧教堂正在吞没记忆，人物关系和信仰冲突同时发酵。",
    cover:
      "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=900&h=1200&fit=crop&auto=format",
    tags: ["重氛围", "高情绪", "禁忌感"],
    emotion: 88,
    inference: 62,
    horror: 83,
    newPlayer: 32,
    hot: false,
    newArrival: true,
    recommended: false,
    friendsPlayed: true,
    supportSolo: false,
    supportTeam: true,
    dmAgents: ["深井讲述者", "暮烛引导员"],
    companionAgents: ["夜航", "棱镜", "白鸦"],
  },
];

const genreOptions = ["全部", "情感本", "推理本", "机制本", "阵营本"];
const difficultyOptions = ["全部", "入门", "进阶", "硬核"];
const feedOptions = [
  { value: "featured", label: "精选" },
  { value: "hot", label: "热门" },
  { value: "new", label: "新上线" },
  { value: "recommended", label: "个人推荐" },
  { value: "friends", label: "好友玩过" },
];

function ScriptLibrary() {
  const [query, setQuery] = React.useState("");
  const [genre, setGenre] = React.useState("全部");
  const [difficulty, setDifficulty] = React.useState("全部");
  const [feed, setFeed] = React.useState("featured");
  const [selectedId, setSelectedId] = React.useState(scripts[0].id);

  const filtered = scripts.filter((script) => {
    const hitQuery =
      script.title.includes(query.trim()) ||
      script.subtitle.includes(query.trim()) ||
      script.tags.some((tag) => tag.includes(query.trim()));
    const hitGenre = genre === "全部" || script.genre === genre;
    const hitDifficulty = difficulty === "全部" || script.difficulty === difficulty;
    const hitFeed =
      feed === "featured" ||
      (feed === "hot" && script.hot) ||
      (feed === "new" && script.newArrival) ||
      (feed === "recommended" && script.recommended) ||
      (feed === "friends" && script.friendsPlayed);
    return hitQuery && hitGenre && hitDifficulty && hitFeed;
  });

  const selected = filtered.find((script) => script.id === selectedId) || filtered[0] || scripts[0];

  return (
    <StudioShell
      title="剧本库"
      subtitle="像翻开一间旧宅档案馆那样找本：先看主视觉，再按题材、人数、难度和情绪浓度筛选，最后挑出能直接开局的剧本。"
      eyebrow="library / archive / recommendation"
      stats={[
        { label: "剧本总数", value: `${scripts.length}` },
        { label: "热门剧本", value: `${scripts.filter((s) => s.hot).length}` },
        { label: "新上线", value: `${scripts.filter((s) => s.newArrival).length}` },
        { label: "推荐剧本", value: `${scripts.filter((s) => s.recommended).length}` },
      ]}
    >
      <Stack gap="xl">
        <Grid gutter="xl">
          <Grid.Col span={{ base: 12, lg: 8 }}>
            <Paper radius="xl" p={{ base: "lg", md: "xl" }} className="tone-hero">
              <Group align="stretch" gap="xl" wrap="wrap">
                <Box
                  style={{
                    width: 240,
                    minHeight: 320,
                    borderRadius: 24,
                    backgroundImage: `linear-gradient(180deg, rgba(0,0,0,0.05), rgba(0,0,0,0.75)), url(${selected.cover})`,
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                    boxShadow: "0 24px 72px rgba(0,0,0,0.45)",
                  }}
                />
                <Stack justify="space-between" gap="md" style={{ flex: 1 }}>
                  <Stack gap="sm">
                    <Group gap="xs">
                      <Badge color="red" variant="filled">
                        Figma 风格
                      </Badge>
                      <Badge variant="light" color="gray">
                        {selected.genre}
                      </Badge>
                      <Badge variant="light" color="yellow">
                        {selected.difficulty}
                      </Badge>
                    </Group>
                    <Title order={1} fz={{ base: 34, md: 56 }} lh={0.95}>
                      {selected.title}
                    </Title>
                    <Text size="lg" c="dimmed" maw={640} lh={1.8}>
                      {selected.description}
                    </Text>
                  </Stack>

                  <Group gap="md" wrap="wrap">
                    {[
                      { label: "人数", value: selected.players },
                      { label: "时长", value: selected.duration },
                      { label: "评分", value: `★ ${selected.rating.toFixed(1)}` },
                      { label: "新手友好", value: `${selected.newPlayer}%` },
                    ].map((item) => (
                      <Paper key={item.label} radius="xl" p="md" className="industrial-card" style={{ minWidth: 132 }}>
                        <Text className="monospace-label" size="xs" c="dimmed">
                          {item.label}
                        </Text>
                        <Text fw={800} mt={4}>
                          {item.value}
                        </Text>
                      </Paper>
                    ))}
                  </Group>
                </Stack>
              </Group>
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, lg: 4 }}>
            <Stack gap="md">
              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  search archive
                </Text>
                <TextInput
                  mt="sm"
                  placeholder="搜索剧本名称 / 标签 / 子标题"
                  leftSection={<IconSearch size={16} />}
                  value={query}
                  onChange={(event) => setQuery(event.currentTarget.value)}
                  radius="xl"
                />
                <Grid mt="sm" gutter="sm">
                  <Grid.Col span={6}>
                    <Select
                      label="题材"
                      value={genre}
                      onChange={(value) => setGenre(value || "全部")}
                      data={genreOptions}
                    />
                  </Grid.Col>
                  <Grid.Col span={6}>
                    <Select
                      label="难度"
                      value={difficulty}
                      onChange={(value) => setDifficulty(value || "全部")}
                      data={difficultyOptions}
                    />
                  </Grid.Col>
                </Grid>
                <SegmentedControl mt="sm" fullWidth value={feed} onChange={setFeed} data={feedOptions} />
              </Paper>

              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  recommendation logic
                </Text>
                <Stack gap="sm" mt="sm">
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      偏好匹配
                    </Text>
                    <Text fw={700}>92%</Text>
                  </Group>
                  <Progress value={92} color="red" radius="xl" />
                  <Text size="sm" c="dimmed" lh={1.7}>
                    综合剧本类型、最近游玩记录、想体验的情绪、在线时长、组队人数和 Agent 擅长方向生成解释型推荐。
                  </Text>
                </Stack>
              </Paper>
            </Stack>
          </Grid.Col>
        </Grid>

        <Grid gutter="xl">
          <Grid.Col span={{ base: 12, lg: 8 }}>
            <Group justify="space-between" align="center" mb="md" wrap="wrap">
              <Group gap="xs">
                <Badge color="red" variant="filled" leftSection={<IconCrown size={14} />}>
                  热门剧本
                </Badge>
                <Badge color="gray" variant="light" leftSection={<IconSparkles size={14} />}>
                  新上线剧本
                </Badge>
                <Badge color="blue" variant="light" leftSection={<IconHeart size={14} />}>
                  个人推荐
                </Badge>
                <Badge color="green" variant="light" leftSection={<IconUsers size={14} />}>
                  好友玩过
                </Badge>
              </Group>
              <Text size="sm" c="dimmed">
                点击卡片切换右侧详情
              </Text>
            </Group>

            <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
              {filtered.map((script) => {
                const active = selected.id === script.id;
                return (
                  <Card
                    key={script.id}
                    radius="xl"
                    className="industrial-card"
                    p="md"
                    onClick={() => setSelectedId(script.id)}
                    style={{
                      cursor: "pointer",
                      borderColor: active ? "rgba(212, 84, 65, 0.55)" : undefined,
                      transform: active ? "translateY(-2px)" : undefined,
                    }}
                  >
                    <Group align="stretch" gap="md" wrap="nowrap">
                      <Box
                        style={{
                          width: 132,
                          minHeight: 180,
                          borderRadius: 18,
                          backgroundImage: `linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,0.72)), url(${script.cover})`,
                          backgroundSize: "cover",
                          backgroundPosition: "center",
                        }}
                      />
                      <Stack gap="xs" style={{ flex: 1 }}>
                        <Group justify="space-between" align="flex-start">
                          <Stack gap={2}>
                            <Text className="monospace-label" size="xs" c="dimmed">
                              {script.subtitle}
                            </Text>
                            <Title order={4}>{script.title}</Title>
                          </Stack>
                          <Badge variant="light" color="red">
                            ★ {script.rating.toFixed(1)}
                          </Badge>
                        </Group>

                        <Text size="sm" c="dimmed" lh={1.65}>
                          {script.description}
                        </Text>

                        <Group gap="xs" mt="auto">
                          {script.tags.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="light" color="gray">
                              {tag}
                            </Badge>
                          ))}
                        </Group>

                        <Group justify="space-between" mt="xs">
                          <Text size="sm" c="dimmed">
                            {script.players} · {script.duration} · {script.difficulty}
                          </Text>
                          <Badge variant="light" color={script.newPlayer >= 80 ? "teal" : "yellow"}>
                            新手 {script.newPlayer}%
                          </Badge>
                        </Group>
                      </Stack>
                    </Group>
                  </Card>
                );
              })}
            </SimpleGrid>
          </Grid.Col>

          <Grid.Col span={{ base: 12, lg: 4 }}>
            <Stack gap="md">
              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  selected script
                </Text>
                <Title order={4} mt={6}>
                  {selected.title}
                </Title>
                <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                  {selected.description}
                </Text>
                <Divider my="md" color="rgba(255,255,255,0.08)" />
                <Stack gap="sm">
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      情感浓度
                    </Text>
                    <Text fw={700}>{selected.emotion}</Text>
                  </Group>
                  <Progress value={selected.emotion} color="red" radius="xl" />
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      推理难度
                    </Text>
                    <Text fw={700}>{selected.inference}</Text>
                  </Group>
                  <Progress value={selected.inference} color="orange" radius="xl" />
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      恐怖程度
                    </Text>
                    <Text fw={700}>{selected.horror}</Text>
                  </Group>
                  <Progress value={selected.horror} color="gray" radius="xl" />
                </Stack>
              </Paper>

              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  agent fit
                </Text>
                <Stack gap="xs" mt="sm">
                  <Text fw={700}>可用 DM-Agent</Text>
                  <Group gap="xs">
                    {selected.dmAgents.map((item) => (
                      <Badge key={item} color="red" variant="light">
                        {item}
                      </Badge>
                    ))}
                  </Group>
                  <Text fw={700} mt="sm">
                    适配陪玩 Agent
                  </Text>
                  <Group gap="xs">
                    {selected.companionAgents.map((item) => (
                      <Badge key={item} color="blue" variant="light">
                        {item}
                      </Badge>
                    ))}
                  </Group>
                </Stack>
              </Paper>

              <Paper radius="xl" p="lg" className="industrial-card">
                <Text className="monospace-label" size="xs" c="dimmed">
                  scene rules
                </Text>
                <Stack gap="xs" mt="sm">
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      单人模式
                    </Text>
                    <Text fw={700}>{selected.supportSolo ? "支持" : "不支持"}</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                      真人组队
                    </Text>
                    <Text fw={700}>{selected.supportTeam ? "支持" : "不支持"}</Text>
                  </Group>
                </Stack>
              </Paper>
            </Stack>
          </Grid.Col>
        </Grid>

        <SimpleGrid cols={{ base: 1, md: 2, lg: 4 }} spacing="md">
          {[
            {
              title: "根据用户偏好推荐剧本",
              icon: IconHeart,
              text: "根据剧本类型、情绪偏好、接受时长和恐怖阈值生成可解释结果。",
            },
            {
              title: "根据最近游玩记录推荐",
              icon: IconSparkles,
              text: "自动避开疲劳类型，优先推送你最近最想补齐的空白风格。",
            },
            {
              title: "根据组队人数推荐",
              icon: IconUsers,
              text: "把当前房间人数和角色构成一起考虑，减少开局后再改本。",
            },
            {
              title: "根据常用 Agent 推荐",
              icon: IconRobot,
              text: "让剧本选择和陪玩阵容一起联动，直接输出完整开局方案。",
            },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.title} radius="xl" className="industrial-card" p="md">
                <Icon size={18} />
                <Text fw={800} mt="sm">
                  {item.title}
                </Text>
                <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                  {item.text}
                </Text>
              </Card>
            );
          })}
        </SimpleGrid>

        <Paper radius="xl" p="lg" className="industrial-card">
          <Group justify="space-between" align="flex-start" wrap="wrap">
            <Stack gap={4}>
              <Text className="monospace-label" size="xs" c="dimmed">
                social proof
              </Text>
              <Title order={3}>热门剧本与玩家反馈</Title>
            </Stack>
            <Badge variant="light" color="red" leftSection={<IconGhost size={14} />}>
              暗黑 / 工业 / 废宅气质
            </Badge>
          </Group>

          <SimpleGrid cols={{ base: 1, md: 3 }} mt="md" spacing="md">
            {[
              {
                name: "林晓青",
                role: "资深玩家 · 200+局",
                text: "《血色玫瑰庄园》让我哭了半小时，结尾的收束很狠。",
              },
              {
                name: "陈墨",
                role: "推理爱好者 · 80+局",
                text: "GM 专业度很高，节奏和氛围都很稳定，适合沉浸。",
              },
              {
                name: "苏颜",
                role: "新手玩家 · 15局",
                text: "第一次就能听懂，推荐很准，体验没有压力。",
              },
            ].map((item) => (
              <Card key={item.name} radius="lg" className="tone-panel" p="md">
                <Group justify="space-between">
                  <Stack gap={2}>
                    <Text fw={700}>{item.name}</Text>
                    <Text size="sm" c="dimmed">
                      {item.role}
                    </Text>
                  </Stack>
                  <Badge variant="light" color="yellow">
                    5.0
                  </Badge>
                </Group>
                <Text size="sm" c="dimmed" mt="sm" lh={1.7}>
                  {item.text}
                </Text>
              </Card>
            ))}
          </SimpleGrid>
        </Paper>
      </Stack>
    </StudioShell>
  );
}

export { ScriptLibrary };
