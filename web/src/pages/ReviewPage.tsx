/**
 * EvoMap Murder Game — 复盘页面
 *
 * 两个 Tab：
 *   1. 圆桌评分看板 — 1:1 复刻游戏选角圆桌，DM 居中，角色环绕，综合评分+维度详情
 *   2. 基因胶囊面板 — 局后经验提炼为可复用胶囊的展示面板
 */

import React from "react";
import {
  Avatar,
  Badge,
  Box,
  Button,
  Card,
  Group,
  Modal,
  Paper,
  Progress,
  RingProgress,
  Stack,
  Tabs,
  Text,
  Title,
  Tooltip,
} from "@mantine/core";
import {
  IconArrowLeft,
  IconBrain,
  IconBulb,
  IconChartBar,
  IconDna,
  IconEye,
  IconFlame,
  IconHeart,
  IconLink,
  IconMessageCircle,
  IconSearch,
  IconStarFilled,
  IconUserCircle,
  IconUsers,
} from "@tabler/icons-react";
import { useNavigate, useParams } from "react-router-dom";

import { GAME_PLAYERS, type GamePlayer } from "./gameMockData";

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

const dmPortrait = new URL("../video_picture/雾港主理人.png", import.meta.url).href;

// ============================
// DM 评分维度
// ============================

type DimensionKey =
  | "evidenceCount"
  | "clueMastery"
  | "logicClarity"
  | "activity"
  | "progress"
  | "roleImmersion"
  | "collaboration"
  | "reasoningAccuracy";

interface ScoreDimension {
  key: DimensionKey;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const SCORE_DIMENSIONS: ScoreDimension[] = [
  { key: "evidenceCount", label: "搜证数量", icon: <IconSearch size={16} />, description: "主动搜索与发现的线索数量" },
  { key: "clueMastery", label: "线索掌握度", icon: <IconLink size={16} />, description: "对线索的理解深度与关联能力" },
  { key: "logicClarity", label: "条理清晰度", icon: <IconBulb size={16} />, description: "发言结构与推理链完整度" },
  { key: "activity", label: "活跃度", icon: <IconFlame size={16} />, description: "发言频率与参与讨论的积极性" },
  { key: "progress", label: "推进度", icon: <IconChartBar size={16} />, description: "对游戏进程的关键推动程度" },
  { key: "roleImmersion", label: "角色代入度", icon: <IconUserCircle size={16} />, description: "是否始终以角色身份行动和发言" },
  { key: "collaboration", label: "协作度", icon: <IconUsers size={16} />, description: "与其他玩家配合程度" },
  { key: "reasoningAccuracy", label: "推理准确度", icon: <IconBrain size={16} />, description: "最终结论与真相的接近程度" },
];

// ============================
// 模拟复盘数据（对应 GAME_PLAYERS 中非 DM 的 5 个角色）
// ============================

interface PlayerReview {
  playerId: string;
  compositeScore: number;
  dimensions: Record<DimensionKey, number>;
  dmComment: string;
}

const MOCK_REVIEWS: PlayerReview[] = [
  {
    playerId: "user",
    compositeScore: 88,
    dimensions: { evidenceCount: 85, clueMastery: 90, logicClarity: 92, activity: 80, progress: 88, roleImmersion: 95, collaboration: 78, reasoningAccuracy: 90 },
    dmComment: "推理链条完整，角色代入感极强。在最后投票阶段的逻辑梳理是全场亮点。搜证稍显保守，下次可以更大胆地追问。",
  },
  {
    playerId: "chen",
    compositeScore: 72,
    dimensions: { evidenceCount: 60, clueMastery: 65, logicClarity: 70, activity: 75, progress: 68, roleImmersion: 85, collaboration: 82, reasoningAccuracy: 65 },
    dmComment: "角色扮演认真，但推理时容易被带偏。线索利用率偏低，建议下次多关注时间线矛盾。",
  },
  {
    playerId: "crow",
    compositeScore: 85,
    dimensions: { evidenceCount: 88, clueMastery: 82, logicClarity: 85, activity: 90, progress: 86, roleImmersion: 75, collaboration: 70, reasoningAccuracy: 88 },
    dmComment: "搜证能力出众，发言条理清晰。但偶尔抢话，建议给其他玩家更多表达空间。整体表现优秀。",
  },
  {
    playerId: "su",
    compositeScore: 76,
    dimensions: { evidenceCount: 68, clueMastery: 75, logicClarity: 72, activity: 65, progress: 70, roleImmersion: 88, collaboration: 85, reasoningAccuracy: 72 },
    dmComment: "角色扮演出色，情感表达自然。推理参与度可以更高，面对质询时不要急于回避。",
  },
  {
    playerId: "echo",
    compositeScore: 80,
    dimensions: { evidenceCount: 78, clueMastery: 80, logicClarity: 78, activity: 88, progress: 82, roleImmersion: 72, collaboration: 75, reasoningAccuracy: 76 },
    dmComment: "推进节奏积极，控场能力不错。但角色代入可以更深入，避免过于功能化的发言。",
  },
];

// ============================
// 模拟基因胶囊数据
// ============================

interface GeneCapsule {
  id: string;
  title: string;
  category: "reasoning" | "role-playing" | "hosting" | "collaboration" | "strategy";
  categoryLabel: string;
  publisherName: string;
  publisherRole: string;
  score: number;
  content: string;
  strategy: string;
  signals: string[];
  usageCount: number;
  createdAt: string;
}

const MOCK_CAPSULES: GeneCapsule[] = [
  {
    id: "capsule_001",
    title: "沉默型玩家的引导策略",
    category: "hosting",
    categoryLabel: "主持技巧",
    publisherName: "雾港主理人",
    publisherRole: "dm",
    score: 0.92,
    content: "当遇到沉默型玩家时，不要直接点名提问，而是先肯定他们之前的发言，再用开放式问题引导他们补充。给予足够思考时间，不要催促。",
    strategy: "1. 先回顾该玩家已有的贡献\n2. 抛出一个与其角色相关的开放问题\n3. 等待至少30秒再跟进\n4. 不直接给答案，而是给方向",
    signals: ["新手引导", "沉默玩家", "氛围营造"],
    usageCount: 24,
    createdAt: "2026-06-15",
  },
  {
    id: "capsule_002",
    title: "时间线矛盾的定位方法",
    category: "reasoning",
    categoryLabel: "推理技巧",
    publisherName: "白鸦",
    publisherRole: "companion",
    score: 0.88,
    content: "面对复杂时间线时，先将所有事件按角色分别列出，再交叉对比。重点关注事件之间的最小时间间隔，找到不可能同时成立的矛盾点。",
    strategy: "1. 按角色整理时间线\n2. 标注每个事件的时间精度（精确/约/估计）\n3. 寻找重叠区间\n4. 用证据验证关键时间点",
    signals: ["时间线分析", "逻辑推理", "证据链"],
    usageCount: 31,
    createdAt: "2026-06-14",
  },
  {
    id: "capsule_003",
    title: "情感角色的沉浸推进法",
    category: "role-playing",
    categoryLabel: "角色扮演",
    publisherName: "纸鸮",
    publisherRole: "companion",
    score: 0.85,
    content: "扮演情感位角色时，不要急于推进推理。先用角色关系互动建立情感连接，让其他玩家产生共情后再自然引出关键线索。情感线是推理线的土壤。",
    strategy: "1. 开场先用角色关系铺垫\n2. 在关键剧情节点表达情感反应\n3. 用情感线索引出物理线索\n4. 在高潮处释放情感，推高推理张力",
    signals: ["情感本", "角色关系", "沉浸"],
    usageCount: 18,
    createdAt: "2026-06-13",
  },
  {
    id: "capsule_004",
    title: "对抗型玩家的边界管理",
    category: "collaboration",
    categoryLabel: "协作技巧",
    publisherName: "燧石",
    publisherRole: "companion",
    score: 0.79,
    content: "对抗不意味着敌对。质疑时要区分'角色的谎言'和'玩家的推理'。质疑角色是游戏的一部分，质疑玩家则会破坏体验。保持尊重，用证据说话。",
    strategy: "1. 质疑前先确认自己的证据基础\n2. 用'我注意到...这似乎与...矛盾'代替'你在撒谎'\n3. 被反驳时大方接受\n4. 对抗结束后主动释放善意",
    signals: ["对抗", "边界管理", "尊重"],
    usageCount: 15,
    createdAt: "2026-06-12",
  },
  {
    id: "capsule_005",
    title: "新手局的节奏控制",
    category: "hosting",
    categoryLabel: "主持技巧",
    publisherName: "暮烛引导员",
    publisherRole: "dm",
    score: 0.91,
    content: "新手局中，DM需要在引导和放手之间找到平衡。每个阶段开始前给出明确的结构预告，过程中用间接提示代替直接答案，阶段结束后做简短复盘总结。",
    strategy: "1. 每阶段开始：用1-2句话说明本阶段目标\n2. 过程中：只在方向偏离时给出暗示\n3. 阶段结束：30秒回顾要点\n4. 全程：用计时器可视化节奏",
    signals: ["新手局", "节奏控制", "教学"],
    usageCount: 27,
    createdAt: "2026-06-11",
  },
  {
    id: "capsule_006",
    title: "证据链的闭环验证",
    category: "reasoning",
    categoryLabel: "推理技巧",
    publisherName: "夜蝉",
    publisherRole: "companion",
    score: 0.87,
    content: "每个证据都应该被验证两次：一次从物理线索的角度，一次从动机的角度。只有两线交汇的点才是可靠的推理节点。单一来源的证据不可作为核心推理依据。",
    strategy: "1. 对每个关键证据问：谁、什么、何时、何地\n2. 找到至少一个动机线索与之呼应\n3. 画出证据关系图\n4. 标记孤证并标注为'待验证'",
    signals: ["证据链", "逻辑推理", "验证"],
    usageCount: 22,
    createdAt: "2026-06-10",
  },
];

// ============================
// 辅助函数
// ============================

const CATEGORY_COLORS: Record<string, string> = {
  reasoning: "blue",
  "role-playing": "grape",
  hosting: "orange",
  collaboration: "green",
  strategy: "red",
};

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  reasoning: <IconBrain size={14} />,
  "role-playing": <IconHeart size={14} />,
  hosting: <IconStarFilled size={14} />,
  collaboration: <IconUsers size={14} />,
  strategy: <IconBulb size={14} />,
};

function getScoreColor(score: number): string {
  if (score >= 90) return "yellow";
  if (score >= 80) return "teal";
  if (score >= 70) return "blue";
  if (score >= 60) return "orange";
  return "red";
}

function getRingColor(score: number): string {
  if (score >= 90) return "#fbbf24";
  if (score >= 80) return "#2dd4bf";
  if (score >= 70) return "#60a5fa";
  if (score >= 60) return "#fb923c";
  return "#f87171";
}

function getSeatPosition(index: number, total: number) {
  const angle = -90 + (360 / total) * index;
  const radians = (angle * Math.PI) / 180;
  return {
    left: `${50 + 42 * Math.cos(radians)}%`,
    top: `${50 + 42 * Math.sin(radians)}%`,
  };
}

// ============================
// 主页面
// ============================

export function ReviewPage() {
  const navigate = useNavigate();
  const { id = "iron-avenue" } = useParams();

  const [reviewTab, setReviewTab] = React.useState<string | null>("table");
  const [selectedPlayerId, setSelectedPlayerId] = React.useState<string | null>(null);
  const [selectedCapsule, setSelectedCapsule] = React.useState<GeneCapsule | null>(null);

  const gamePlayers = React.useMemo(() => GAME_PLAYERS.filter((p) => p.id !== "dm"), []);
  const dmPlayer = React.useMemo(() => GAME_PLAYERS.find((p) => p.id === "dm"), []);

  const getReview = (playerId: string) => MOCK_REVIEWS.find((r) => r.playerId === playerId);

  const highestScoreId = React.useMemo(() => {
    if (MOCK_REVIEWS.length === 0) return "";
    return MOCK_REVIEWS.reduce((max, r) =>
      r.compositeScore > (MOCK_REVIEWS.find((x) => x.playerId === max)?.compositeScore ?? 0) ? r.playerId : max,
      MOCK_REVIEWS[0].playerId,
    );
  }, []);

  const selectedPlayer = React.useMemo(
    () => GAME_PLAYERS.find((p) => p.id === selectedPlayerId) ?? null,
    [selectedPlayerId],
  );
  const selectedReview = React.useMemo(
    () => MOCK_REVIEWS.find((r) => r.playerId === selectedPlayerId) ?? null,
    [selectedPlayerId],
  );

  return (
    <Box
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, rgba(157, 28, 28, 0.28), transparent 26%), " +
          "radial-gradient(circle at 80% 8%, rgba(255, 181, 122, 0.08), transparent 18%), " +
          "linear-gradient(180deg, #0c0808 0%, #130d0d 42%, #090606 100%)",
      }}
    >
      <Stack gap="xl" p="lg" maw={1200} mx="auto">
        {/* 顶部返回栏 */}
        <Group justify="space-between">
          <Button
            variant="subtle"
            leftSection={<IconArrowLeft size={16} />}
            radius="xl"
            onClick={() => navigate("/games")}
          >
            返回我的游戏
          </Button>
          <Group gap="xs">
            <Text className="monospace-label" size="xs" c="dimmed">
              post-game review
            </Text>
            <Badge color="red" variant="filled">复盘</Badge>
          </Group>
        </Group>

        {/* Tab 切换 */}
        <Tabs value={reviewTab} onChange={setReviewTab}>
          <Tabs.List grow mb="xl">
            <Tabs.Tab value="table" leftSection={<IconUsers size={16} />}>
              圆桌评分看板
            </Tabs.Tab>
            <Tabs.Tab value="capsules" leftSection={<IconDna size={16} />}>
              基因胶囊面板
            </Tabs.Tab>
          </Tabs.List>

          {/* ==================== Tab 1：圆桌评分看板 ==================== */}
          <Tabs.Panel value="table" pt="md">
            <Paper radius="xl" p="xl" className="industrial-card">
              <Stack gap="lg" align="center">
                {/* 标题行 */}
                <Group justify="space-between" w="100%" wrap="wrap">
                  <Box>
                    <Text className="monospace-label" size="xs" c="dimmed">
                      dm score table
                    </Text>
                    <Title order={3}>DM 综合评分圆桌</Title>
                  </Box>
                  <Badge color="red" variant="light">
                    {gamePlayers.length} 个角色席位
                  </Badge>
                </Group>

                {/* 圆桌 — 1:1 复刻 game 里的 round-table */}
                <Box className="round-table" style={{ width: 420, height: 420 }}>
                  {/* 桌面 */}
                  <Box className="round-table__surface" />

                  {/* DM 居中 */}
                  {dmPlayer && (
                    <Box
                      style={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        zIndex: 5,
                        textAlign: "center",
                      }}
                    >
                      <Tooltip label="DM · 雾港主理人">
                        <Avatar
                          src={dmPortrait}
                          size={64}
                          radius="xl"
                          imageProps={{ style: { objectPosition: "top" } }}
                          style={{
                            border: "3px solid rgba(250, 82, 82, 0.45)",
                            boxShadow: "0 0 24px rgba(250, 82, 82, 0.2)",
                          }}
                        />
                      </Tooltip>
                      <Text size="xs" c="dimmed" mt={2}>DM</Text>
                    </Box>
                  )}

                  {/* 角色座位 */}
                  {gamePlayers.map((player, index) => {
                    const review = getReview(player.id);
                    const score = review?.compositeScore ?? 0;
                    const isHighest = player.id === highestScoreId;
                    const position = getSeatPosition(index, gamePlayers.length);
                    const portrait = characterPortraits[player.role];

                    return (
                      <Box
                        key={player.id}
                        className="round-table__seat"
                        style={{ left: position.left, top: position.top }}
                        onClick={() => setSelectedPlayerId(player.id)}
                      >
                        {/* 评分光环 */}
                        <RingProgress
                          size={84}
                          thickness={4}
                          roundCaps
                          sections={[{ value: score, color: getRingColor(score) }]}
                          label={
                            <Box style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                              {portrait ? (
                                <Avatar
                                  src={portrait}
                                  size={52}
                                  radius="xl"
                                  className="round-table__role"
                                  imageProps={{ style: { objectPosition: "top" } }}
                                />
                              ) : (
                                <Avatar size={52} radius="xl" color={player.color} className="round-table__role">
                                  {player.role.slice(0, 1)}
                                </Avatar>
                              )}
                            </Box>
                          }
                        />
                        {/* 角色名（头像上方） */}
                        <Text size="xs" fw={700} ta="center" lh={1.1} mt={2}>
                          {player.role}
                        </Text>
                        {/* 综合评分 */}
                        <Badge
                          size="xs"
                          variant={isHighest ? "filled" : "light"}
                          color={isHighest ? "yellow" : getScoreColor(score)}
                          style={isHighest ? { boxShadow: "0 0 12px rgba(251, 191, 36, 0.5)" } : undefined}
                          mt={2}
                        >
                          {score}
                        </Badge>
                        {/* 名字标签 */}
                        <Text
                          size="xs"
                          ta="center"
                          c={player.id === "user" ? "orange.3" : "dimmed"}
                          fw={player.id === "user" ? 800 : 400}
                          mt={2}
                        >
                          {player.name}
                        </Text>
                        {player.id === "user" ? (
                          <Text size="xs" c="orange.3" fw={700} ta="center">
                            真人玩家
                          </Text>
                        ) : player.agent ? (
                          <Text size="xs" c="dimmed" ta="center">
                            AI Agent
                          </Text>
                        ) : (
                          <Text size="xs" c="dimmed" ta="center">
                            玩家
                          </Text>
                        )}
                      </Box>
                    );
                  })}
                </Box>

                <Text size="sm" c="dimmed">
                  点击角色头像查看 DM 详细评分维度 · 金色光环为最高分
                </Text>
              </Stack>
            </Paper>
          </Tabs.Panel>

          {/* ==================== Tab 2：基因胶囊面板 ==================== */}
          <Tabs.Panel value="capsules" pt="md">
            <Paper radius="xl" className="industrial-card" p="xl">
              <Stack gap="lg">
                <Group justify="space-between">
                  <Box>
                    <Group gap="xs">
                      <IconDna size={18} color="#fbbf24" />
                      <Text className="monospace-label" size="xs" c="yellow.3">
                        gene capsule dashboard
                      </Text>
                    </Group>
                    <Title order={3} mt={4}>基因胶囊 · 经验可视化</Title>
                    <Text size="sm" c="dimmed" mt={4}>
                      每局结束后，Agent 生成原始经验（Gene）→ DM 评审打分 → 高质量经验提炼为普适胶囊，可在新局中复用。
                    </Text>
                  </Box>
                  <Badge color="yellow" variant="light" size="lg">
                    {MOCK_CAPSULES.length} 个胶囊
                  </Badge>
                </Group>

                <Box className="agent-masonry">
                  {MOCK_CAPSULES.map((capsule) => (
                    <Box key={capsule.id} className="agent-masonry__item">
                      <Card
                        radius="lg"
                        className="tone-panel"
                        p="md"
                        style={{ cursor: "pointer" }}
                        onClick={() => setSelectedCapsule(capsule)}
                      >
                        <Stack gap="sm" h="100%">
                          <Group justify="space-between">
                            <Badge
                              size="sm"
                              variant="filled"
                              color={CATEGORY_COLORS[capsule.category] || "gray"}
                              leftSection={CATEGORY_ICONS[capsule.category]}
                            >
                              {capsule.categoryLabel}
                            </Badge>
                            <Badge size="sm" variant="light" color={getScoreColor(capsule.score * 100)}>
                              {capsule.score.toFixed(2)}
                            </Badge>
                          </Group>

                          <Text fw={700} size="sm" lh={1.4}>
                            {capsule.title}
                          </Text>

                          <Text size="xs" c="dimmed" lh={1.6} lineClamp={3} style={{ flex: 1 }}>
                            {capsule.content}
                          </Text>

                          <Group gap={4}>
                            {capsule.signals.slice(0, 3).map((tag) => (
                              <Badge key={tag} size="xs" variant="outline" color="gray">
                                {tag}
                              </Badge>
                            ))}
                          </Group>

                          <Group justify="space-between">
                            <Text size="xs" c="dimmed">
                              {capsule.publisherName} · 已用 {capsule.usageCount} 次
                            </Text>
                            <IconEye size={14} style={{ opacity: 0.4 }} />
                          </Group>
                        </Stack>
                      </Card>
                    </Box>
                  ))}
                </Box>
              </Stack>
            </Paper>
          </Tabs.Panel>
        </Tabs>
      </Stack>

      {/* ==================== 弹窗：评分维度详情 ==================== */}
      <Modal
        opened={!!selectedPlayerId}
        onClose={() => setSelectedPlayerId(null)}
        title={null}
        radius="xl"
        size="md"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
      >
        {selectedPlayer && selectedReview && (
          <Paper radius="xl" className="industrial-card" p="lg">
            <Stack gap="md">
              <Group align="flex-start" wrap="nowrap">
                {characterPortraits[selectedPlayer.role] ? (
                  <Avatar
                    src={characterPortraits[selectedPlayer.role]}
                    size={64}
                    radius="xl"
                    imageProps={{ style: { objectPosition: "top" } }}
                  />
                ) : (
                  <Avatar size={64} radius="xl" color={selectedPlayer.color}>
                    {selectedPlayer.role.slice(0, 1)}
                  </Avatar>
                )}
                <Box style={{ flex: 1 }}>
                  <Text className="monospace-label" size="xs" c="orange.3">
                    dm score detail
                  </Text>
                  <Title order={3}>{selectedPlayer.role} · {selectedPlayer.name}</Title>
                  <Group gap="xs" mt={4}>
                    <Badge size="sm" color={selectedPlayer.agent ? "blue" : "orange"} variant="light">
                      {selectedPlayer.id === "user" ? "真人玩家" : selectedPlayer.agent ? "AI Agent" : "玩家"}
                    </Badge>
                    <Badge
                      size="sm"
                      color={getScoreColor(selectedReview.compositeScore)}
                      variant="filled"
                      leftSection={<IconStarFilled size={12} />}
                    >
                      综合 {selectedReview.compositeScore}
                    </Badge>
                  </Group>
                </Box>
              </Group>

              <Stack gap="sm">
                {SCORE_DIMENSIONS.map((dim) => {
                  const value = selectedReview.dimensions[dim.key] ?? 0;
                  return (
                    <Box key={dim.key}>
                      <Group justify="space-between" mb={4}>
                        <Group gap={6}>
                          {dim.icon}
                          <Text size="sm" fw={500}>{dim.label}</Text>
                        </Group>
                        <Text size="sm" fw={700} c={`${getScoreColor(value)}.3`}>
                          {value}
                        </Text>
                      </Group>
                      <Progress value={value} color={getScoreColor(value)} size="sm" radius="xl" />
                      <Text size="xs" c="dimmed" mt={2}>{dim.description}</Text>
                    </Box>
                  );
                })}
              </Stack>

              <Card radius="lg" className="ambient-grid" p="md">
                <Group gap="xs" mb="sm">
                  <IconMessageCircle size={16} />
                  <Text fw={700} size="sm">DM 评语</Text>
                </Group>
                <Text size="sm" c="dimmed" lh={1.7}>
                  {selectedReview.dmComment}
                </Text>
              </Card>
            </Stack>
          </Paper>
        )}
      </Modal>

      {/* ==================== 弹窗：胶囊详情 ==================== */}
      <Modal
        opened={!!selectedCapsule}
        onClose={() => setSelectedCapsule(null)}
        title={null}
        radius="xl"
        size="md"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
      >
        {selectedCapsule && (
          <Paper radius="xl" className="industrial-card" p="lg">
            <Stack gap="md">
              <Group justify="space-between">
                <Badge
                  variant="filled"
                  color={CATEGORY_COLORS[selectedCapsule.category] || "gray"}
                  leftSection={CATEGORY_ICONS[selectedCapsule.category]}
                >
                  {selectedCapsule.categoryLabel}
                </Badge>
                <Badge variant="light" color={getScoreColor(selectedCapsule.score * 100)}>
                  评分 {selectedCapsule.score.toFixed(2)}
                </Badge>
              </Group>

              <Title order={3}>{selectedCapsule.title}</Title>

              <Text size="sm" c="dimmed">
                发布者：{selectedCapsule.publisherName}（{selectedCapsule.publisherRole === "dm" ? "DM" : "陪玩 Agent"}）
              </Text>

              <Card radius="lg" className="ambient-grid" p="md">
                <Text fw={700} size="sm" mb="sm">经验内容</Text>
                <Text size="sm" c="dimmed" lh={1.7}>{selectedCapsule.content}</Text>
              </Card>

              {selectedCapsule.strategy && (
                <Card radius="lg" className="ambient-grid" p="md">
                  <Text fw={700} size="sm" mb="sm">策略方法</Text>
                  <Text size="sm" c="dimmed" lh={1.7} style={{ whiteSpace: "pre-wrap" }}>
                    {selectedCapsule.strategy}
                  </Text>
                </Card>
              )}

              <Group gap={4}>
                {selectedCapsule.signals.map((tag) => (
                  <Badge key={tag} size="xs" variant="light" color="gray">{tag}</Badge>
                ))}
              </Group>

              <Group justify="space-between">
                <Text size="xs" c="dimmed">创建于 {selectedCapsule.createdAt}</Text>
                <Text size="xs" c="dimmed">已使用 {selectedCapsule.usageCount} 次</Text>
              </Group>
            </Stack>
          </Paper>
        )}
      </Modal>
    </Box>
  );
}

export default ReviewPage;
