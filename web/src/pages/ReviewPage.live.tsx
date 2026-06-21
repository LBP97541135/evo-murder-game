/**
 * 复盘页（API 驱动）：DM 真相揭示 · 圆桌评分 · 基因胶囊
 */

import React from "react";
import {
  Avatar,
  Badge,
  Box,
  Button,
  Card,
  Group,
  Loader,
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
  IconDeviceGamepad2,
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
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import { scripts } from "./scriptData";
import { buildPlayPath, getStoredGameSession } from "../utils/gameNavigation";
import {
  getGameReview,
  runGameReview,
  type CharacterScore,
  type GameReviewBundle,
  type ReviewCapsule,
  type ReviewGene,
  type ScoreDimensionKey,
} from "../api/reviewApi";

const characterPortraits: Record<string, string> = {
  "周野": new URL("../Character/周野.png", import.meta.url).href,
  "顾沉": new URL("../Character/顾沉.png", import.meta.url).href,
  "沈禾": new URL("../Character/沈禾.png", import.meta.url).href,
  "周岚": new URL("../Character/周岚.png", import.meta.url).href,
  "秦野": new URL("../Character/秦野.png", import.meta.url).href,
  "林远": new URL("../Character/林远.png", import.meta.url).href,
};

const dmPortrait = new URL("../video_picture/雾港主理人.png", import.meta.url).href;

const SCORE_DIMENSIONS: Array<{
  key: ScoreDimensionKey;
  label: string;
  icon: React.ReactNode;
  description: string;
}> = [
  { key: "evidenceCount", label: "搜证数量", icon: <IconSearch size={16} />, description: "主动搜索与发现的线索数量" },
  { key: "clueMastery", label: "线索掌握度", icon: <IconLink size={16} />, description: "对线索的理解深度与关联能力" },
  { key: "logicClarity", label: "条理清晰度", icon: <IconBulb size={16} />, description: "发言结构与推理链完整度" },
  { key: "activity", label: "活跃度", icon: <IconFlame size={16} />, description: "发言频率与参与讨论的积极性" },
  { key: "progress", label: "推进度", icon: <IconChartBar size={16} />, description: "对游戏进程的关键推动程度" },
  { key: "roleImmersion", label: "角色代入度", icon: <IconUserCircle size={16} />, description: "是否始终以角色身份行动和发言" },
  { key: "collaboration", label: "协作度", icon: <IconUsers size={16} />, description: "与其他玩家配合程度" },
  { key: "reasoningAccuracy", label: "推理准确度", icon: <IconBrain size={16} />, description: "最终结论与真相的接近程度" },
];

const CATEGORY_COLORS: Record<string, string> = {
  reasoning: "blue",
  "role-playing": "grape",
  hosting: "orange",
  collaboration: "green",
  strategy: "red",
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

function categoryLabel(cat?: string) {
  const map: Record<string, string> = {
    reasoning: "推理技巧",
    "role-playing": "角色扮演",
    hosting: "主持技巧",
    collaboration: "协作技巧",
    strategy: "策略",
  };
  return map[cat || ""] || cat || "经验";
}

export function ReviewPage() {
  const navigate = useNavigate();
  const { id = "xiutie-avenue-missing-three-minutes" } = useParams();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session") || getStoredGameSession(id);
  const scriptTitle = scripts.find((s) => s.id === id)?.title || "未知剧本";

  const [reviewTab, setReviewTab] = React.useState<string | null>("truth");
  const [bundle, setBundle] = React.useState<GameReviewBundle | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [running, setRunning] = React.useState(false);
  const [error, setError] = React.useState("");
  const [selectedRole, setSelectedRole] = React.useState<string | null>(null);
  const [selectedCapsule, setSelectedCapsule] = React.useState<ReviewCapsule | null>(null);

  const loadReview = React.useCallback(async (generate = false) => {
    if (!sessionId) {
      setLoading(false);
      setError("缺少游戏会话 ID，请从「我的游戏」或完成对局后进入复盘。");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const data = generate ? await runGameReview(sessionId) : await getGameReview(sessionId);
      if (!generate && data.message === "review_not_generated") {
        setRunning(true);
        const generated = await runGameReview(sessionId);
        setBundle(generated);
      } else {
        setBundle(data);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
      setRunning(false);
    }
  }, [sessionId]);

  React.useEffect(() => {
    void loadReview(false);
  }, [loadReview]);

  const scores = bundle?.character_scores || [];
  const truth = bundle?.truth_review;
  const capsules = bundle?.capsules || [];
  const genes = bundle?.genes || [];

  const evolutionRows = React.useMemo(() => {
    const byAgent = new Map<string, { gene?: ReviewGene; capsule?: ReviewCapsule }>();
    for (const gene of genes) {
      const key = gene.agent_key || gene.agent_name || gene.id || gene.gene_id || "unknown";
      byAgent.set(key, { ...(byAgent.get(key) || {}), gene });
    }
    for (const cap of capsules) {
      const key = cap.agent_key || cap.agent_name || cap.geneId || cap.id;
      byAgent.set(key, { ...(byAgent.get(key) || {}), capsule: cap });
    }
    return Array.from(byAgent.entries()).map(([key, row]) => ({ key, ...row }));
  }, [genes, capsules]);

  const highestRole = React.useMemo(() => {
    if (!scores.length) return "";
    return scores.reduce((a, b) => (b.compositeScore > a.compositeScore ? b : a)).role_name;
  }, [scores]);

  const selectedScore = scores.find((s) => s.role_name === selectedRole) || null;

  return (
    <Box
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, rgba(157, 28, 28, 0.28), transparent 26%), " +
          "linear-gradient(180deg, #0c0808 0%, #130d0d 42%, #090606 100%)",
      }}
    >
      <Stack gap="xl" p="lg" maw={1200} mx="auto">
        <Group justify="space-between" wrap="wrap">
          <Group gap="xs">
            <Button variant="subtle" leftSection={<IconArrowLeft size={16} />} radius="xl" onClick={() => navigate("/games")}>
              返回我的游戏
            </Button>
            <Button variant="subtle" leftSection={<IconDeviceGamepad2 size={16} />} radius="xl" onClick={() => navigate(buildPlayPath(id))}>
              回到对局
            </Button>
          </Group>
          <Stack gap={2} align="flex-end">
            <Badge color="red" variant="filled">复盘 · 自进化</Badge>
            <Text size="sm" fw={700}>{scriptTitle}</Text>
            {sessionId && <Badge size="sm" variant="outline">会话 {sessionId.slice(0, 10)}…</Badge>}
          </Stack>
        </Group>

        {(loading || running) && (
          <Paper radius="xl" p="xl" className="industrial-card">
            <Group justify="center" gap="md">
              <Loader color="red" />
              <Text c="dimmed">{running ? "DM 正在复盘评分并生成基因胶囊…" : "加载复盘数据…"}</Text>
            </Group>
          </Paper>
        )}

        {error && (
          <Paper radius="xl" p="lg" className="industrial-card">
            <Text c="red">{error}</Text>
            <Button mt="md" radius="xl" onClick={() => void loadReview(true)}>重新生成复盘</Button>
          </Paper>
        )}

        {!loading && !error && bundle && (
          <Tabs value={reviewTab} onChange={setReviewTab}>
            <Tabs.List grow mb="md">
              <Tabs.Tab value="truth">DM 揭示真相</Tabs.Tab>
              <Tabs.Tab value="table" leftSection={<IconUsers size={16} />}>圆桌评分</Tabs.Tab>
              <Tabs.Tab value="capsules" leftSection={<IconDna size={16} />}>基因胶囊</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="truth" pt="md">
              <Paper radius="xl" p="xl" className="industrial-card">
                <Stack gap="lg">
                  <Group align="flex-start" wrap="nowrap">
                    <Avatar src={dmPortrait} size={72} radius="xl" />
                    <Box>
                      <Text className="monospace-label" size="xs" c="dimmed">dm truth reveal</Text>
                      <Title order={3}>雾港主理人 · 完整复盘</Title>
                      {bundle.truth_killer && (
                        <Badge mt="xs" color="red" variant="light">真凶：{bundle.truth_killer}</Badge>
                      )}
                    </Box>
                  </Group>

                  <Card radius="lg" className="ambient-grid" p="lg">
                    <Text fw={700} mb="sm">真相还原</Text>
                    <Text size="sm" lh={1.8} style={{ whiteSpace: "pre-wrap" }}>
                      {truth?.truth_narrative || "（暂无）"}
                    </Text>
                  </Card>

                  <Card radius="lg" className="tone-panel" p="lg">
                    <Text fw={700} mb="sm" c="orange.3">讨论过程不足</Text>
                    <Text size="sm" lh={1.8} style={{ whiteSpace: "pre-wrap" }}>
                      {truth?.discussion_critique || "（暂无）"}
                    </Text>
                  </Card>

                  {truth?.key_lessons && truth.key_lessons.length > 0 && (
                    <Stack gap="xs">
                      <Text fw={700}>改进要点</Text>
                      {truth.key_lessons.map((item) => (
                        <Text key={item} size="sm" c="dimmed">· {item}</Text>
                      ))}
                    </Stack>
                  )}

                  {truth?.vote_analysis && (
                    <Text size="sm" c="dimmed" lh={1.7}>投票分析：{truth.vote_analysis}</Text>
                  )}

                  {bundle.evolution_summary && (
                    <Group gap="md">
                      <Badge color="teal" variant="light">基因 {bundle.evolution_summary.genes_created ?? 0}</Badge>
                      <Badge color="yellow" variant="light">胶囊 {bundle.evolution_summary.capsules_created ?? 0}</Badge>
                    </Group>
                  )}
                </Stack>
              </Paper>
            </Tabs.Panel>

            <Tabs.Panel value="table" pt="md">
              <Paper radius="xl" p="xl" className="industrial-card">
                <Stack gap="lg" align="center">
                  <Title order={3}>DM 综合评分圆桌</Title>
                  <Text size="sm" c="dimmed">仅对玩家与陪玩角色评分，DM 主持位不参与。</Text>
                  <Box className="round-table" style={{ width: 420, height: 420 }}>
                    <Box className="round-table__surface" />
                    <Box style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", textAlign: "center", zIndex: 5 }}>
                      <Avatar src={dmPortrait} size={64} radius="xl" style={{ border: "3px solid rgba(250,82,82,0.45)" }} />
                      <Text size="xs" c="dimmed" mt={2}>DM</Text>
                    </Box>
                    {scores.map((item, index) => {
                      const pos = getSeatPosition(index, scores.length);
                      const isTop = item.role_name === highestRole;
                      const portrait = characterPortraits[item.role_name];
                      return (
                        <Box
                          key={item.role_name}
                          className="round-table__seat"
                          style={{ left: pos.left, top: pos.top, cursor: "pointer" }}
                          onClick={() => setSelectedRole(item.role_name)}
                        >
                          <RingProgress
                            size={84}
                            thickness={4}
                            roundCaps
                            sections={[{ value: item.compositeScore, color: getRingColor(item.compositeScore) }]}
                            label={
                              portrait ? (
                                <Avatar src={portrait} size={52} radius="xl" imageProps={{ style: { objectPosition: "top" } }} />
                              ) : (
                                <Avatar size={52} radius="xl">{item.role_name.slice(0, 1)}</Avatar>
                              )
                            }
                          />
                          <Text size="xs" fw={700} ta="center" mt={2}>{item.role_name}</Text>
                          <Badge size="xs" color={isTop ? "yellow" : getScoreColor(item.compositeScore)} mt={2}>
                            {item.compositeScore}
                          </Badge>
                        </Box>
                      );
                    })}
                  </Box>
                  <Text size="sm" c="dimmed">点击角色查看 8 维度评分与 DM 评语</Text>
                </Stack>
              </Paper>
            </Tabs.Panel>

            <Tabs.Panel value="capsules" pt="md">
              <Paper radius="xl" p="xl" className="industrial-card">
                <Stack gap="lg">
                  <Group justify="space-between">
                    <Title order={3}>本局基因 · 胶囊</Title>
                    <Group gap="xs">
                      <Badge color="grape" variant="light">{genes.length} 基因</Badge>
                      <Badge color="yellow" variant="light">{capsules.length} 胶囊</Badge>
                    </Group>
                  </Group>
                  <Text size="sm" c="dimmed" lh={1.7}>
                    流程：陪玩 Agent 听取 DM 真相复盘后自我分析 → 生成 Gene → DM 评审 → 提炼 Capsule（未达入库标准也会在本页展示）。
                    DM 不参与评分与自进化。
                  </Text>
                  {evolutionRows.length === 0 ? (
                    <Text c="dimmed">暂无基因/胶囊，请点击下方重新生成或完成对局后自动触发。</Text>
                  ) : (
                    <Stack gap="md">
                      {evolutionRows.map(({ key, gene, capsule }) => (
                        <Card key={key} radius="lg" className="tone-panel" p="md">
                          <Group justify="space-between" mb="sm">
                            <Text fw={700}>{gene?.agent_name || capsule?.agent_name || key}</Text>
                            <Group gap={6}>
                              {gene ? <Badge size="sm" color="grape" variant="light">Gene</Badge> : null}
                              {capsule ? (
                                <Badge size="sm" color={capsule.stored_in_db === false ? "gray" : "yellow"} variant="light">
                                  {capsule.stored_in_db === false ? "胶囊（仅展示）" : "胶囊（已入库）"}
                                </Badge>
                              ) : null}
                            </Group>
                          </Group>
                          {gene ? (
                            <Stack gap={4} mb="sm">
                              <Text size="sm" fw={600}>{gene.summary || "（无摘要）"}</Text>
                              <Text size="xs" c="dimmed" lineClamp={4}>{gene.detail}</Text>
                              {gene.dmComment ? (
                                <Text size="xs" c="orange.3">DM 评审：{gene.dmComment}</Text>
                              ) : null}
                            </Stack>
                          ) : null}
                          {capsule ? (
                            <Card
                              radius="md"
                              p="sm"
                              className="ambient-grid"
                              style={{ cursor: "pointer" }}
                              onClick={() => setSelectedCapsule(capsule)}
                            >
                              <Badge color={CATEGORY_COLORS[capsule.category || ""] || "gray"} size="sm">
                                {categoryLabel(capsule.category)}
                              </Badge>
                              <Text fw={700} size="sm" mt="sm">{capsule.title}</Text>
                              <Text size="xs" c="dimmed" lineClamp={3} mt={4}>{capsule.content}</Text>
                              <Badge size="xs" variant="light" mt="sm">评分 {(capsule.score ?? 0).toFixed(2)}</Badge>
                            </Card>
                          ) : (
                            <Text size="xs" c="dimmed">胶囊生成中或失败，请重新运行复盘。</Text>
                          )}
                        </Card>
                      ))}
                    </Stack>
                  )}
                </Stack>
              </Paper>
            </Tabs.Panel>
          </Tabs>
        )}

        {!loading && bundle && (
          <Group justify="center">
            <Button variant="light" radius="xl" onClick={() => void loadReview(true)} loading={running}>
              重新运行 DM 复盘与胶囊生成
            </Button>
          </Group>
        )}
      </Stack>

      <Modal opened={!!selectedRole} onClose={() => setSelectedRole(null)} radius="xl" size="md" title={selectedRole ? `${selectedRole} · DM 评分` : ""}>
        {selectedScore && (
          <Stack gap="sm">
            {SCORE_DIMENSIONS.map((dim) => {
              const value = selectedScore.dimensions[dim.key] ?? 0;
              return (
                <Box key={dim.key}>
                  <Group justify="space-between">
                    <Text size="sm">{dim.label}</Text>
                    <Text fw={700}>{value}</Text>
                  </Group>
                  <Progress value={value} color={getScoreColor(value)} size="sm" />
                </Box>
              );
            })}
            <Card radius="lg" p="md" className="ambient-grid" mt="md">
              <Text fw={700} size="sm" mb="xs">DM 评语</Text>
              <Text size="sm" c="dimmed" lh={1.7}>{selectedScore.dmComment}</Text>
            </Card>
          </Stack>
        )}
      </Modal>

      <Modal opened={!!selectedCapsule} onClose={() => setSelectedCapsule(null)} radius="xl" size="md" title={selectedCapsule?.title}>
        {selectedCapsule && (
          <Stack gap="sm">
            <Text size="sm" lh={1.8}>{selectedCapsule.content}</Text>
            {selectedCapsule.strategy && (
              <>
                <Text fw={700} size="sm">策略</Text>
                <Text size="sm" c="dimmed" style={{ whiteSpace: "pre-wrap" }}>{selectedCapsule.strategy}</Text>
              </>
            )}
          </Stack>
        )}
      </Modal>
    </Box>
  );
}
