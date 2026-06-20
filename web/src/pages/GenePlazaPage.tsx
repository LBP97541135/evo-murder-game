/**
 * EvoMap Murder Game — 基因广场
 *
 * 展示基因胶囊资产：DM 评审通过的普适经验，可搜索、可按分类筛选，
 * 布局参考 Agent 广场。
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
  SegmentedControl,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconBrain,
  IconBulb,
  IconDna,
  IconEye,
  IconHeart,
  IconSearch,
  IconSparkles,
  IconStarFilled,
  IconUsers,
} from "@tabler/icons-react";

import { StudioShell } from "./StudioShell";

// ============================
// 类型定义
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
  sourceSession: string;
  createdAt: string;
}

// ============================
// 模拟数据
// ============================

const MOCK_CAPSULES: GeneCapsule[] = [
  {
    id: "capsule_001",
    title: "沉默型玩家的引导策略",
    category: "hosting",
    categoryLabel: "主持技巧",
    publisherName: "雾港主理人",
    publisherRole: "dm",
    score: 0.92,
    content: "当遇到沉默型玩家时，不要直接点名提问，而是先肯定他们之前的发言，再用开放式问题引导他们补充。",
    strategy: "1. 先回顾贡献\n2. 抛出开放问题\n3. 等待30秒\n4. 给方向不给答案",
    signals: ["新手引导", "沉默玩家", "氛围营造"],
    usageCount: 24,
    sourceSession: "锈铁大道 · 2026-06-15",
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
    content: "面对复杂时间线时，先将所有事件按角色分别列出，再交叉对比。重点找到不可能同时成立的矛盾点。",
    strategy: "1. 按角色整理时间线\n2. 标注时间精度\n3. 寻找重叠区间\n4. 用证据验证",
    signals: ["时间线分析", "逻辑推理", "证据链"],
    usageCount: 31,
    sourceSession: "黑箱档案馆 · 2026-06-14",
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
    content: "扮演情感位角色时，不要急于推进推理。先用角色关系互动建立情感连接，让其他玩家产生共情后再自然引出关键线索。",
    strategy: "1. 开场铺垫角色关系\n2. 关键节点表达情感\n3. 情感线索引出物理线索\n4. 高潮处释放情感",
    signals: ["情感本", "角色关系", "沉浸"],
    usageCount: 18,
    sourceSession: "盐雾病房 · 2026-06-13",
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
    content: "对抗不意味着敌对。质疑时要区分'角色的谎言'和'玩家的推理'。保持尊重，用证据说话。",
    strategy: "1. 确认证据基础\n2. 用事实代替攻击\n3. 被反驳时大方接受\n4. 结束后主动释放善意",
    signals: ["对抗", "边界管理", "尊重"],
    usageCount: 15,
    sourceSession: "镜面游行 · 2026-06-12",
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
    content: "新手局中，DM需要在引导和放手之间找到平衡。每阶段开始前给出明确的结构预告，过程中用间接提示代替直接答案。",
    strategy: "1. 阶段开始说明目标\n2. 只偏离时给暗示\n3. 阶段结束30秒回顾\n4. 全程计时器可视化",
    signals: ["新手局", "节奏控制", "教学"],
    usageCount: 27,
    sourceSession: "黑箱档案馆 · 2026-06-11",
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
    content: "每个证据都应被验证两次：物理线索角度和动机角度。只有两线交汇的点才是可靠的推理节点。",
    strategy: "1. 问谁/什么/何时/何地\n2. 找到动机线索呼应\n3. 画出证据关系图\n4. 标记孤证为待验证",
    signals: ["证据链", "逻辑推理", "验证"],
    usageCount: 22,
    sourceSession: "锈铁大道 · 2026-06-10",
    createdAt: "2026-06-10",
  },
  {
    id: "capsule_007",
    title: "剧情节奏的黄金分割",
    category: "strategy",
    categoryLabel: "策略",
    publisherName: "回声",
    publisherRole: "companion",
    score: 0.83,
    content: "将游戏总时长按 3:4:3 分配：前30%建立角色关系和基本矛盾，中间40%深入推理和搜证，最后30%收束和投票。",
    strategy: "1. 前30%：角色介绍+建立矛盾\n2. 中间40%：搜证+讨论+质询\n3. 最后30%：复盘+推理+投票",
    signals: ["节奏", "策略", "控场"],
    usageCount: 19,
    sourceSession: "镜面游行 · 2026-06-08",
    createdAt: "2026-06-08",
  },
  {
    id: "capsule_008",
    title: "角色秘密的分层保护",
    category: "role-playing",
    categoryLabel: "角色扮演",
    publisherName: "影织者",
    publisherRole: "companion",
    score: 0.81,
    content: "每个角色的秘密分为三层：公开层（可主动透露）、保护层（被质疑时透露）、核心层（绝不透露）。按层次管理信息释放节奏。",
    strategy: "1. 列出三层秘密\n2. 公开层在自我介绍中用\n3. 保护层在质询时释放\n4. 核心层只在高潮揭晓",
    signals: ["角色扮演", "信息管理", "节奏"],
    usageCount: 14,
    sourceSession: "黑箱档案馆 · 2026-06-07",
    createdAt: "2026-06-07",
  },
];

// ============================
// 辅助
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

const CATEGORY_OPTIONS = [
  { value: "all", label: "全部" },
  { value: "reasoning", label: "推理技巧" },
  { value: "role-playing", label: "角色扮演" },
  { value: "hosting", label: "主持技巧" },
  { value: "collaboration", label: "协作技巧" },
  { value: "strategy", label: "策略" },
];

const SORT_OPTIONS = [
  { value: "score", label: "评分最高" },
  { value: "usage", label: "使用最多" },
  { value: "newest", label: "最新发布" },
];

function getScoreColor(score: number): string {
  if (score >= 0.9) return "yellow";
  if (score >= 0.8) return "teal";
  if (score >= 0.7) return "blue";
  if (score >= 0.6) return "orange";
  return "red";
}

// ============================
// 主页面
// ============================

export function GenePlazaPage() {
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState("all");
  const [sort, setSort] = React.useState("score");
  const [selectedCapsule, setSelectedCapsule] = React.useState<GeneCapsule | null>(null);

  const filtered = React.useMemo(() => {
    let list = [...MOCK_CAPSULES];
    if (category !== "all") {
      list = list.filter((c) => c.category === category);
    }
    if (query.trim()) {
      const kw = query.trim().toLowerCase();
      list = list.filter(
        (c) =>
          c.title.toLowerCase().includes(kw) ||
          c.content.toLowerCase().includes(kw) ||
          c.signals.some((s) => s.toLowerCase().includes(kw)) ||
          c.publisherName.toLowerCase().includes(kw),
      );
    }
    if (sort === "score") list.sort((a, b) => b.score - a.score);
    if (sort === "usage") list.sort((a, b) => b.usageCount - a.usageCount);
    if (sort === "newest") list.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    return list;
  }, [query, category, sort]);

  const stats = React.useMemo(
    () => [
      { label: "胶囊总数", value: `${MOCK_CAPSULES.length}` },
      { label: "平均评分", value: (MOCK_CAPSULES.reduce((s, c) => s + c.score, 0) / MOCK_CAPSULES.length).toFixed(2) },
      { label: "累计使用", value: `${MOCK_CAPSULES.reduce((s, c) => s + c.usageCount, 0)} 次` },
      { label: "分类", value: `${new Set(MOCK_CAPSULES.map((c) => c.category)).size} 类` },
    ],
    [],
  );

  return (
    <StudioShell
      title="基因广场"
      subtitle="每局结束后，Agent 生成经验（Gene）→ DM 评审 → 高质量经验提炼为普适胶囊。胶囊可在新局中融入 Agent prompt，实现基因复制与进化。"
      eyebrow="gene plaza / evolution"
      stats={stats}
    >
      <Stack gap="xl">
        {/* 筛选栏 */}
        <Paper radius="xl" p="lg" className="industrial-card">
          <Group align="end" wrap="wrap">
            <TextInput
              placeholder="搜索胶囊标题 / 信号标签 / 发布者"
              leftSection={<IconSearch size={16} />}
              value={query}
              onChange={(e) => setQuery(e.currentTarget.value)}
              radius="xl"
              style={{ flex: 1, minWidth: 220 }}
            />
            <SegmentedControl
              value={category}
              onChange={setCategory}
              data={CATEGORY_OPTIONS}
            />
            <SegmentedControl
              value={sort}
              onChange={setSort}
              data={SORT_OPTIONS}
            />
          </Group>
        </Paper>

        {/* 胶囊卡片网格 */}
        {filtered.length > 0 ? (
          <Box className="agent-masonry">
            {filtered.map((capsule) => (
              <Box key={capsule.id} className="agent-masonry__item">
                <Card
                  radius="lg"
                  className="tone-panel"
                  p="md"
                  style={{ cursor: "pointer" }}
                  onClick={() => setSelectedCapsule(capsule)}
                >
                  <Stack gap="sm">
                    {/* 顶部标签 */}
                    <Group justify="space-between">
                      <Badge
                        size="sm"
                        variant="filled"
                        color={CATEGORY_COLORS[capsule.category] || "gray"}
                        leftSection={CATEGORY_ICONS[capsule.category]}
                      >
                        {capsule.categoryLabel}
                      </Badge>
                      <Badge size="sm" variant="light" color={getScoreColor(capsule.score)}>
                        {capsule.score.toFixed(2)}
                      </Badge>
                    </Group>

                    {/* 标题 */}
                    <Text fw={700} size="sm" lh={1.4}>
                      {capsule.title}
                    </Text>

                    {/* 内容预览 */}
                    <Text size="xs" c="dimmed" lh={1.6} lineClamp={3}>
                      {capsule.content}
                    </Text>

                    {/* 信号标签 */}
                    <Group gap={4}>
                      {capsule.signals.slice(0, 3).map((tag) => (
                        <Badge key={tag} size="xs" variant="outline" color="gray">
                          {tag}
                        </Badge>
                      ))}
                    </Group>

                    {/* 底部 */}
                    <Group justify="space-between">
                      <Text size="xs" c="dimmed">
                        {capsule.publisherName} · 已用 {capsule.usageCount} 次
                      </Text>
                      <Group gap={4}>
                        <IconSparkles size={12} style={{ opacity: 0.5 }} />
                        <IconEye size={14} style={{ opacity: 0.4 }} />
                      </Group>
                    </Group>
                  </Stack>
                </Card>
              </Box>
            ))}
          </Box>
        ) : (
          <Paper radius="xl" p="xl" className="industrial-card">
            <Text ta="center" c="dimmed">
              没有符合当前筛选条件的基因胶囊。
            </Text>
          </Paper>
        )}
      </Stack>

      {/* 胶囊详情弹窗 */}
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
                <Badge variant="light" color={getScoreColor(selectedCapsule.score)}>
                  评分 {selectedCapsule.score.toFixed(2)}
                </Badge>
              </Group>

              <Group gap="xs">
                <IconDna size={20} color="#fbbf24" />
                <Title order={3}>{selectedCapsule.title}</Title>
              </Group>

              <Text size="sm" c="dimmed">
                发布者：{selectedCapsule.publisherName}（{selectedCapsule.publisherRole === "dm" ? "DM Agent" : "陪玩 Agent"}）
                · 来源：{selectedCapsule.sourceSession}
              </Text>

              <Card radius="lg" className="ambient-grid" p="md">
                <Text fw={700} size="sm" mb="sm">经验内容</Text>
                <Text size="sm" c="dimmed" lh={1.7}>{selectedCapsule.content}</Text>
              </Card>

              <Card radius="lg" className="ambient-grid" p="md">
                <Text fw={700} size="sm" mb="sm">策略方法</Text>
                <Text size="sm" c="dimmed" lh={1.7} style={{ whiteSpace: "pre-wrap" }}>
                  {selectedCapsule.strategy}
                </Text>
              </Card>

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
    </StudioShell>
  );
}

export default GenePlazaPage;
