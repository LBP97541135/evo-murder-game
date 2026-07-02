/**
 * 复盘页（API 驱动）：DM 真相揭示 · 圆桌评分 · 经验技能
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
  type ReviewSkill,
  type ReviewExperience,
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

const agentPortraits: Record<string, string> = {
  "白鸦": new URL("../video_picture/白鸽.png", import.meta.url).href,
  "回声": new URL("../video_picture/回声.png", import.meta.url).href,
  "纸鸮": new URL("../video_picture/纸鸮.png", import.meta.url).href,
  "燧石": new URL("../video_picture/燧石.png", import.meta.url).href,
  "月蛾": new URL("../video_picture/月蛾.png", import.meta.url).href,
  "影织者": new URL("../video_picture/影织者.png", import.meta.url).href,
  "夜蝉": new URL("../video_picture/夜蝉.png", import.meta.url).href,
};

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  reasoning: <IconBrain size={14} />,
  "role-playing": <IconHeart size={14} />,
  hosting: <IconStarFilled size={14} />,
  collaboration: <IconUsers size={14} />,
  strategy: <IconBulb size={14} />,
};

const CATEGORY_COLORS: Record<string, string> = {
  reasoning: "blue",
  "role-playing": "grape",
  hosting: "orange",
  collaboration: "green",
  strategy: "red",
};

function experienceIdOf(experience?: ReviewExperience) {
  return experience?.experience_id || experience?.id || "";
}

function pairExperiencesAndSkills(experiences: ReviewExperience[], skills: ReviewSkill[]) {
  const skillByExperienceId = new Map<string, ReviewSkill>();
  const skillByAgent = new Map<string, ReviewSkill>();
  for (const skill of skills) {
    if (skill.experienceId) skillByExperienceId.set(skill.experienceId, skill);
    if (skill.agent_key) skillByAgent.set(skill.agent_key, skill);
  }

  const rows: Array<{ key: string; experience?: ReviewExperience; skill?: ReviewSkill }> = [];
  const usedSkills = new Set<string>();

  for (const experience of experiences) {
    const eid = experienceIdOf(experience);
    const skill =
      (eid && skillByExperienceId.get(eid))
      || (experience.agent_key && skillByAgent.get(experience.agent_key))
      || skills.find((s) => s.experienceId === eid);
    if (skill) usedSkills.add(skill.id);
    rows.push({
      key: eid || experience.agent_key || experience.agent_name || "unknown",
      experience,
      skill,
    });
  }

  for (const skill of skills) {
    if (usedSkills.has(skill.id)) continue;
    rows.push({
      key: skill.experienceId || skill.agent_key || skill.id,
      skill,
    });
  }

  return rows;
}

function isReviewReady(data: GameReviewBundle) {
  if (!data.success) return false;
  if (data.review_status === "generating") return false;
  const experienceCount = data.experiences?.length ?? 0;
  const skillCount = data.skills?.length ?? 0;
  if (experienceCount === 0 && skillCount === 0) return false;
  if (experienceCount > 0 && skillCount === 0) return false;
  return true;
}

function skillScorePercent(score?: number) {
  const value = score ?? 0;
  return value <= 1 ? value * 100 : value;
}

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

const EXCLUDED_SCORE_ROLES = new Set(["侦探", "DM", "雾港主理人", "dm", "host", "narrator"]);

function isExcludedScoreRole(roleName?: string) {
  const name = (roleName || "").trim();
  if (!name) return true;
  if (EXCLUDED_SCORE_ROLES.has(name)) return true;
  const lower = name.toLowerCase();
  return lower === "dm" || lower === "host" || lower === "detective";
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
  const [selectedSkill, setSelectedSkill] = React.useState<ReviewSkill | null>(null);

  const loadReview = React.useCallback(async (generate = false) => {
    if (!sessionId) {
      setLoading(false);
      setError("缺少游戏会话 ID，请从「我的游戏」或完成对局后进入复盘。");
      return;
    }
    setError("");
    setLoading(true);

    const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

    try {
      if (generate) {
        setRunning(true);
        const generated = await runGameReview(sessionId);
        setBundle(generated);
        return;
      }

      let data = await getGameReview(sessionId);

      if (data.message === "review_generating") {
        setRunning(true);
        for (let attempt = 0; attempt < 120; attempt += 1) {
          await sleep(3000);
          data = await getGameReview(sessionId);
          if (isReviewReady(data)) {
            setBundle(data);
            return;
          }
          if (data.message !== "review_generating") break;
        }
        if (data.success) {
          setBundle(data);
        } else {
          setError("复盘仍在生成中，请稍后再刷新；或点击下方按钮手动触发。");
        }
        return;
      }

      const needsGenerate = data.message === "review_not_generated"
        || ((data.experiences?.length ?? 0) === 0 && (data.skills?.length ?? 0) === 0);

      if (needsGenerate) {
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

  const scores = React.useMemo(
    () => (bundle?.character_scores || []).filter((item) => !isExcludedScoreRole(item.role_name)),
    [bundle?.character_scores],
  );
  const truth = bundle?.truth_review;
  const skills = bundle?.skills || [];
  const experiences = bundle?.experiences || [];

  const evolutionRows = React.useMemo(
    () => pairExperiencesAndSkills(experiences, skills),
    [experiences, skills],
  );

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
              <Text c="dimmed">{running ? "DM 正在复盘评分并生成经验技能…" : "加载复盘数据…"}</Text>
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
              <Tabs.Tab value="skills" leftSection={<IconDna size={16} />}>经验技能</Tabs.Tab>
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
                      <Badge color="teal" variant="light">经验 {bundle.evolution_summary.experiences_created ?? 0}</Badge>
                      <Badge color="yellow" variant="light">技能 {bundle.evolution_summary.skills_created ?? 0}</Badge>
                    </Group>
                  )}
                </Stack>
              </Paper>
            </Tabs.Panel>

            <Tabs.Panel value="table" pt="md">
              <Paper radius="xl" p="xl" className="industrial-card">
                <Stack gap="lg" align="center">
                  <Title order={3}>本局评分圆桌</Title>
                  <Text size="sm" c="dimmed">仅展示玩家与陪玩角色的评分，主持位不参与。</Text>
                  <Box className="round-table" style={{ width: 420, height: 420 }}>
                    <Box className="round-table__surface" />
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

            <Tabs.Panel value="skills" pt="md">
              <Paper radius="xl" p="xl" className="industrial-card">
                <Stack gap="lg">
                  <Group justify="space-between" align="flex-start" wrap="wrap">
                    <Box>
                      <Group gap="xs">
                        <IconDna size={18} color="#fbbf24" />
                        <Text className="monospace-label" size="xs" c="yellow.3">
                          experience skill dashboard
                        </Text>
                      </Group>
                      <Title order={3} mt={4}>经验技能 · 经验可视化</Title>
                      <Text size="sm" c="dimmed" mt={4} maw={640} lh={1.7}>
                        陪玩 Agent 听取 DM 复盘后自我分析 → 生成 Experience → DM 评审 → 提炼 Skill。
                        仅本局参与的 Agent 会产出技能。
                      </Text>
                    </Box>
                    <Group gap="xs">
                      <Badge color="grape" variant="light" size="lg">{experiences.length} 经验</Badge>
                      <Badge color="yellow" variant="light" size="lg">{skills.length} 技能</Badge>
                    </Group>
                  </Group>

                  {evolutionRows.length === 0 ? (
                    <Stack gap="xs">
                      <Text c="dimmed">暂无经验/技能，请点击下方「重新运行复盘与技能生成」。</Text>
                      {bundle.evolution_summary?.errors?.length ? (
                        <Text size="sm" c="orange.3">
                          生成日志：{bundle.evolution_summary.errors.join("；")}
                        </Text>
                      ) : null}
                    </Stack>
                  ) : (
                    <Box className="agent-masonry">
                      {evolutionRows.map(({ key, experience, skill }) => {
                        const agentName = experience?.agent_name || skill?.agent_name || key;
                        const portrait = agentPortraits[agentName];
                        const skillScore = skillScorePercent(skill?.score);
                        return (
                          <Box key={key} className="agent-masonry__item">
                            <Card radius="lg" className="evolution-card tone-panel" p={0}>
                              <Box className="evolution-card__header" p="md">
                                <Group justify="space-between" wrap="nowrap">
                                  <Group gap="sm" wrap="nowrap">
                                    <Avatar src={portrait} size={44} radius="xl" color="grape">
                                      {agentName.slice(0, 1)}
                                    </Avatar>
                                    <Box>
                                      <Text fw={700} size="sm">{agentName}</Text>
                                      <Text size="xs" c="dimmed">Experience → Skill</Text>
                                    </Box>
                                  </Group>
                                  <Group gap={6}>
                                    {experience ? <Badge size="xs" color="grape" variant="dot">Experience</Badge> : null}
                                    {skill ? (
                                      <Badge
                                        size="xs"
                                        color={skill.stored_in_db === false ? "gray" : "yellow"}
                                        variant="dot"
                                      >
                                        {skill.stored_in_db === false ? "预览" : "已入库"}
                                      </Badge>
                                    ) : null}
                                  </Group>
                                </Group>
                              </Box>

                              {experience ? (
                                <Box className="evolution-card__experience" px="md" pb="sm">
                                  <Text size="xs" className="monospace-label" c="grape.3" mb={4}>raw experience</Text>
                                  <Text size="sm" fw={600} lh={1.5}>{experience.summary || "（无摘要）"}</Text>
                                  <Text size="xs" c="dimmed" lineClamp={3} mt={4}>{experience.detail}</Text>
                                  {experience.dmComment ? (
                                    <Text size="xs" c="orange.3" mt={6}>DM：{experience.dmComment}</Text>
                                  ) : null}
                                </Box>
                              ) : null}

                              <Box className="evolution-card__arrow" px="md" py={4}>
                                <IconDna size={16} style={{ opacity: 0.45 }} />
                              </Box>

                              {skill ? (
                                <Box
                                  className="evolution-card__skill ambient-grid"
                                  p="md"
                                  style={{ cursor: "pointer" }}
                                  onClick={() => setSelectedSkill(skill)}
                                >
                                  <Group justify="space-between" mb="xs">
                                    <Badge
                                      size="sm"
                                      variant="filled"
                                      color={CATEGORY_COLORS[skill.category || ""] || "gray"}
                                      leftSection={CATEGORY_ICONS[skill.category || ""]}
                                    >
                                      {categoryLabel(skill.category)}
                                    </Badge>
                                    <Badge size="sm" variant="light" color={getScoreColor(skillScore)}>
                                      {(skill.score ?? 0) <= 1 ? (skill.score ?? 0).toFixed(2) : skillScore.toFixed(0)}
                                    </Badge>
                                  </Group>
                                  <Text fw={700} size="sm" lh={1.45}>{skill.title}</Text>
                                  <Text size="xs" c="dimmed" lineClamp={4} mt={6} lh={1.65}>
                                    {skill.content || "（暂无内容）"}
                                  </Text>
                                  {(skill.signals?.length ?? 0) > 0 && (
                                    <Group gap={4} mt="sm">
                                      {skill.signals!.slice(0, 3).map((tag) => (
                                        <Badge key={tag} size="xs" variant="outline" color="gray">{tag}</Badge>
                                      ))}
                                    </Group>
                                  )}
                                  <Group justify="space-between" mt="sm">
                                    <Text size="xs" c="dimmed">{agentName} · 本局提炼</Text>
                                    <IconEye size={14} style={{ opacity: 0.45 }} />
                                  </Group>
                                </Box>
                              ) : (
                                <Box px="md" pb="md">
                                  <Text size="xs" c="dimmed">技能生成中或失败，请重新运行复盘。</Text>
                                </Box>
                              )}
                            </Card>
                          </Box>
                        );
                      })}
                    </Box>
                  )}
                </Stack>
              </Paper>
            </Tabs.Panel>
          </Tabs>
        )}

        {!loading && bundle && (
          <Group justify="center">
            <Button variant="light" radius="xl" onClick={() => void loadReview(true)} loading={running}>
              重新运行复盘与技能生成
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

      <Modal
        opened={!!selectedSkill}
        onClose={() => setSelectedSkill(null)}
        title={null}
        radius="xl"
        size="md"
        overlayProps={{ backgroundOpacity: 0.55, blur: 4 }}
      >
        {selectedSkill && (
          <Paper radius="xl" className="industrial-card" p="lg">
            <Stack gap="md">
              <Group justify="space-between">
                <Badge
                  variant="filled"
                  color={CATEGORY_COLORS[selectedSkill.category || ""] || "gray"}
                  leftSection={CATEGORY_ICONS[selectedSkill.category || ""]}
                >
                  {categoryLabel(selectedSkill.category)}
                </Badge>
                <Badge variant="light" color={getScoreColor(skillScorePercent(selectedSkill.score))}>
                  评分 {(selectedSkill.score ?? 0) <= 1
                    ? (selectedSkill.score ?? 0).toFixed(2)
                    : skillScorePercent(selectedSkill.score).toFixed(0)}
                </Badge>
              </Group>
              <Title order={3}>{selectedSkill.title}</Title>
              {selectedSkill.agent_name && (
                <Text size="sm" c="dimmed">{selectedSkill.agent_name} · 本局经验技能</Text>
              )}
              <Text size="sm" lh={1.8}>{selectedSkill.content}</Text>
              {selectedSkill.strategy && (
                <>
                  <Text fw={700} size="sm">策略</Text>
                  <Text size="sm" c="dimmed" style={{ whiteSpace: "pre-wrap" }}>{selectedSkill.strategy}</Text>
                </>
              )}
            </Stack>
          </Paper>
        )}
      </Modal>
    </Box>
  );
}
