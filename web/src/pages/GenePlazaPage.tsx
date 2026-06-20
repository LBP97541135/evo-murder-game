/**
 * EvoMap Murder Game — 基因胶囊广场
 *
 * 从后端 API 拉取胶囊数据，展示基因胶囊资产：
 * DM 评审通过的普适经验，可搜索、可按分类筛选。
 */

import React from "react";
import {
  Badge,
  Box,
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

import { listCapsules, type CapsuleData } from "../api/invoke";
import { StudioShell } from "./StudioShell";

// ============================
// 映射
// ============================

const PUBLISHER_NAMES: Record<string, string> = {
  "an_82f0573f": "雾港主理人", "an_f4a5d067": "DM-Persist",
  "an_8728817a": "暮烛引导员", "an_c77341f7": "白鸦",
  "an_29300d18": "夜蝉", "an_22f237c1": "纸鸮",
  "an_eeacbc59": "影织者", "an_491f3a73": "燧石",
  "an_a5ae5d92": "燧石", "an_37cdf042": "回声",
  "an_b60343eb": "回声", "local_dm_test": "测试DM",
};

const CATEGORY_LABELS: Record<string, string> = {
  reasoning: "推理技巧", "role-playing": "角色扮演",
  hosting: "主持技巧", collaboration: "协作技巧", strategy: "策略",
};

const CATEGORY_COLORS: Record<string, string> = {
  reasoning: "blue", "role-playing": "grape", hosting: "orange",
  collaboration: "green", strategy: "red",
};

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  reasoning: <IconBrain size={14} />, "role-playing": <IconHeart size={14} />,
  hosting: <IconStarFilled size={14} />, collaboration: <IconUsers size={14} />,
  strategy: <IconBulb size={14} />,
};

const CATEGORY_OPTIONS = [
  { value: "all", label: "全部" }, { value: "reasoning", label: "推理技巧" },
  { value: "role-playing", label: "角色扮演" }, { value: "hosting", label: "主持技巧" },
  { value: "collaboration", label: "协作技巧" }, { value: "strategy", label: "策略" },
];

const SORT_OPTIONS = [
  { value: "score", label: "评分最高" },
  { value: "usage", label: "使用最多" },
  { value: "newest", label: "最新发布" },
];

interface DisplayCapsule {
  id: string; title: string; category: string; categoryLabel: string;
  publisherName: string; publisherRole: string; score: number;
  content: string; strategy: string; signals: string[];
  usageCount: number; createdAt: string;
}

function capsuleToDisplay(c: CapsuleData): DisplayCapsule {
  return {
    id: c.id, title: c.title, category: c.category,
    categoryLabel: CATEGORY_LABELS[c.category] || c.category,
    publisherName: PUBLISHER_NAMES[c.publisherId] || c.publisherId,
    publisherRole: c.publisherRole, score: c.score,
    content: c.content, strategy: c.strategy || "",
    signals: c.signals || [], usageCount: c.usageCount || 0,
    createdAt: c.createdAt ? c.createdAt.slice(0, 10) : "",
  };
}

function getScoreColor(score: number): string {
  if (score >= 0.9) return "yellow"; if (score >= 0.8) return "teal";
  if (score >= 0.7) return "blue"; if (score >= 0.6) return "orange";
  return "red";
}

// ============================
// 主页面
// ============================

export function GenePlazaPage() {
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState("all");
  const [sort, setSort] = React.useState("score");
  const [selectedCapsule, setSelectedCapsule] = React.useState<DisplayCapsule | null>(null);
  const [capsules, setCapsules] = React.useState<DisplayCapsule[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    setLoading(true); setError("");
    listCapsules({ reviewStatus: "approved" })
      .then((data) => { setCapsules(data.map(capsuleToDisplay)); setLoading(false); })
      .catch((err) => { setError(err instanceof Error ? err.message : String(err)); setLoading(false); });
  }, []);

  const filtered = React.useMemo(() => {
    let list = [...capsules];
    if (category !== "all") list = list.filter((c) => c.category === category);
    if (query.trim()) {
      const kw = query.trim().toLowerCase();
      list = list.filter((c) =>
        c.title.toLowerCase().includes(kw) || c.content.toLowerCase().includes(kw) ||
        c.signals.some((s) => s.toLowerCase().includes(kw)) || c.publisherName.toLowerCase().includes(kw));
    }
    if (sort === "score") list.sort((a, b) => b.score - a.score);
    if (sort === "usage") list.sort((a, b) => b.usageCount - a.usageCount);
    if (sort === "newest") list.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    return list;
  }, [query, category, sort, capsules]);

  const stats = React.useMemo(() => [
    { label: "胶囊总数", value: `${capsules.length}` },
    { label: "平均评分", value: capsules.length > 0 ? (capsules.reduce((s, c) => s + c.score, 0) / capsules.length).toFixed(2) : "0.00" },
    { label: "累计使用", value: `${capsules.reduce((s, c) => s + c.usageCount, 0)} 次` },
    { label: "分类", value: `${new Set(capsules.map((c) => c.category)).size} 类` },
  ], [capsules]);

  return (
    <StudioShell
      title="基因胶囊广场"
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
              value={query} onChange={(e) => setQuery(e.currentTarget.value)}
              radius="xl" style={{ flex: 1, minWidth: 220 }}
            />
            <SegmentedControl value={category} onChange={setCategory} data={CATEGORY_OPTIONS} />
            <SegmentedControl value={sort} onChange={setSort} data={SORT_OPTIONS} />
          </Group>
        </Paper>

        {/* 加载/错误状态 */}
        {(loading || error) && (
          <Paper radius="xl" p="sm" className="industrial-card">
            <Text size="sm" c={error ? "red" : "dimmed"}>
              {loading ? "正在从后端加载基因胶囊…" : `加载失败：${error}`}
            </Text>
          </Paper>
        )}

        {/* 胶囊卡片网格 */}
        {!loading && filtered.length > 0 ? (
          <Box className="agent-masonry">
            {filtered.map((capsule) => (
              <Box key={capsule.id} className="agent-masonry__item">
                <Card radius="lg" className="tone-panel" p="md"
                  style={{ cursor: "pointer" }} onClick={() => setSelectedCapsule(capsule)}>
                  <Stack gap="sm">
                    <Group justify="space-between">
                      <Badge size="sm" variant="filled"
                        color={CATEGORY_COLORS[capsule.category] || "gray"}
                        leftSection={CATEGORY_ICONS[capsule.category]}>
                        {capsule.categoryLabel}
                      </Badge>
                      <Badge size="sm" variant="light" color={getScoreColor(capsule.score)}>
                        {capsule.score.toFixed(2)}
                      </Badge>
                    </Group>
                    <Text fw={700} size="sm" lh={1.4}>{capsule.title}</Text>
                    <Text size="xs" c="dimmed" lh={1.6} lineClamp={3}>{capsule.content}</Text>
                    <Group gap={4}>
                      {capsule.signals.slice(0, 3).map((tag) => (
                        <Badge key={tag} size="xs" variant="outline" color="gray">{tag}</Badge>))}
                    </Group>
                    <Group justify="space-between">
                      <Text size="xs" c="dimmed">{capsule.publisherName} · 已用 {capsule.usageCount} 次</Text>
                      <Group gap={4}><IconSparkles size={12} style={{ opacity: 0.5 }} /><IconEye size={14} style={{ opacity: 0.4 }} /></Group>
                    </Group>
                  </Stack>
                </Card>
              </Box>
            ))}
          </Box>
        ) : !loading ? (
          <Paper radius="xl" p="xl" className="industrial-card">
            <Text ta="center" c="dimmed">没有符合当前筛选条件的基因胶囊。</Text>
          </Paper>
        ) : null}
      </Stack>

      {/* 胶囊详情弹窗 */}
      <Modal opened={!!selectedCapsule} onClose={() => setSelectedCapsule(null)}
        title={null} radius="xl" size="md" overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}>
        {selectedCapsule && (
          <Paper radius="xl" className="industrial-card" p="lg">
            <Stack gap="md">
              <Group justify="space-between">
                <Badge variant="filled" color={CATEGORY_COLORS[selectedCapsule.category] || "gray"}
                  leftSection={CATEGORY_ICONS[selectedCapsule.category]}>{selectedCapsule.categoryLabel}</Badge>
                <Badge variant="light" color={getScoreColor(selectedCapsule.score)}>评分 {selectedCapsule.score.toFixed(2)}</Badge>
              </Group>
              <Group gap="xs"><IconDna size={20} color="#fbbf24" /><Title order={3}>{selectedCapsule.title}</Title></Group>
              <Text size="sm" c="dimmed">
                发布者：{selectedCapsule.publisherName}（{selectedCapsule.publisherRole === "dm" ? "DM Agent" : "陪玩 Agent"}）
              </Text>
              <Card radius="lg" className="ambient-grid" p="md">
                <Text fw={700} size="sm" mb="sm">经验内容</Text>
                <Text size="sm" c="dimmed" lh={1.7}>{selectedCapsule.content}</Text>
              </Card>
              {selectedCapsule.strategy && (
                <Card radius="lg" className="ambient-grid" p="md">
                  <Text fw={700} size="sm" mb="sm">策略方法</Text>
                  <Text size="sm" c="dimmed" lh={1.7} style={{ whiteSpace: "pre-wrap" }}>{selectedCapsule.strategy}</Text>
                </Card>)}
              <Group gap={4}>{selectedCapsule.signals.map((tag) => <Badge key={tag} size="xs" variant="light" color="gray">{tag}</Badge>)}</Group>
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
