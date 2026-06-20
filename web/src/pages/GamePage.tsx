import React from "react";
import {
  ActionIcon,
  Avatar,
  Badge,
  Box,
  Button,
  Checkbox,
  Divider,
  Group,
  Modal,
  Paper,
  Progress,
  Radio,
  ScrollArea,
  Select,
  Stack,
  Tabs,
  Text,
  Textarea,
  TextInput,
  Title,
  Tooltip,
} from "@mantine/core";
import { useFullscreen } from "@mantine/hooks";
import {
  IconBook2,
  IconCheck,
  IconClock,
  IconHighlight,
  IconMaximize,
  IconSearch,
  IconSend,
  IconSettings,
  IconUsers,
  IconX,
} from "@tabler/icons-react";
import { useNavigate, useParams } from "react-router-dom";

import {
  Evidence,
  GAME_PHASES,
  GAME_PLAYERS,
  INITIAL_EVIDENCE,
  INTRO_LINES,
  PRIVATE_THREADS,
  ROLE_OPTIONS,
  SCRIPT_CHAPTERS,
  SEARCH_EVIDENCE,
} from "./gameMockData";
import { StudioShell } from "./StudioShell";

const scriptMap: Record<string, string> = {
  "iron-avenue": "锈铁大道",
  "black-archive": "黑箱档案馆",
  "mirror-parade": "镜面游行",
  "salt-ward": "盐雾病房",
  "wolf-assembly": "狼群集会",
  "paper-cathedral": "纸穹教堂",
};

type PublicEvent =
  | { id: number; type: "speech"; speaker: string; text: string; tone: string }
  | { id: number; type: "system"; title: string; text: string }
  | { id: number; type: "evidence"; speaker: string; evidence: Evidence; reason?: string }
  | { id: number; type: "forced"; asker: string; agent: string; question: string }
  | { id: number; type: "private"; agent: string; text: string };

type PublicEventInput =
  | { type: "speech"; speaker: string; text: string; tone: string }
  | { type: "system"; title: string; text: string }
  | { type: "evidence"; speaker: string; evidence: Evidence; reason?: string }
  | { type: "forced"; asker: string; agent: string; question: string }
  | { type: "private"; agent: string; text: string };

type DialogType = "private" | "force" | "evidence" | "rules" | "script" | null;

type ScriptHighlight = {
  id: string;
  chapter: number;
  text: string;
};

const initialEvents: PublicEvent[] = [
  { id: 1, type: "system", title: "阶段开始", text: "公共讨论已开启，所有发言按照队列顺序进行。" },
  { id: 2, type: "speech", speaker: "陈墨", text: "我想先确认值班表究竟是什么时候被替换的。", tone: "teal" },
  { id: 3, type: "speech", speaker: "白鸦 Agent", text: "访客卡背面的锈迹更像是储物柜编号，而不是门牌号。", tone: "blue" },
];

function formatTime(totalSeconds: number) {
  return `${String(Math.floor(totalSeconds / 60)).padStart(2, "0")}:${String(totalSeconds % 60).padStart(2, "0")}`;
}

function GamePage() {
  const navigate = useNavigate();
  const { id = "iron-avenue" } = useParams();
  const scriptTitle = scriptMap[id] || "未知剧本";
  const gameMode = id === "black-archive" ? "单人游戏" : "真人组队";
  const { ref: fullscreenRef, toggle: toggleFullscreen, fullscreen } = useFullscreen();

  const [phaseIndex, setPhaseIndex] = React.useState(0);
  const phase = GAME_PHASES[phaseIndex];
  const [selectedRole, setSelectedRole] = React.useState("user");
  const [roleConfirmed, setRoleConfirmed] = React.useState(false);
  const [chapter, setChapter] = React.useState(0);
  const [readingDone, setReadingDone] = React.useState(false);
  const highlightStorageKey = `game-script-highlights:${id}`;
  const [scriptHighlights, setScriptHighlights] = React.useState<ScriptHighlight[]>(() => {
    try {
      const saved = window.localStorage.getItem(highlightStorageKey);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [selectedScriptText, setSelectedScriptText] = React.useState("");
  const [selectedScriptChapter, setSelectedScriptChapter] = React.useState(0);
  const [introduced, setIntroduced] = React.useState<string[]>([]);
  const [searchesLeft, setSearchesLeft] = React.useState(2);
  const [evidence, setEvidence] = React.useState<Evidence[]>(INITIAL_EVIDENCE);
  const [newEvidence, setNewEvidence] = React.useState<Evidence | null>(null);
  const [queue, setQueue] = React.useState<string[]>(["chen", "crow"]);
  const [currentSpeaker, setCurrentSpeaker] = React.useState<string | null>("chen");
  const [forcedAnswer, setForcedAnswer] = React.useState<{ asker: string; agentId: string; question: string } | null>(null);
  const [events, setEvents] = React.useState<PublicEvent[]>(initialEvents);
  const [rightTab, setRightTab] = React.useState<string | null>("script");
  const [dialog, setDialog] = React.useState<DialogType>(null);
  const [selectedPlayerId, setSelectedPlayerId] = React.useState<string | null>(null);
  const [targetId, setTargetId] = React.useState("crow");
  const [question, setQuestion] = React.useState("");
  const [selectedEvidenceId, setSelectedEvidenceId] = React.useState(INITIAL_EVIDENCE[0].id);
  const [evidenceVisibility, setEvidenceVisibility] = React.useState("所有人");
  const [privateThreads, setPrivateThreads] = React.useState(PRIVATE_THREADS);
  const [activeThreadId, setActiveThreadId] = React.useState(PRIVATE_THREADS[0].id);
  const [privateMessage, setPrivateMessage] = React.useState("");
  const [publicMessage, setPublicMessage] = React.useState("");
  const [feedback, setFeedback] = React.useState("欢迎进入游戏，请从选角开始体验完整流程。");
  const [settingsOpen, setSettingsOpen] = React.useState(false);
  const [speakerSeconds, setSpeakerSeconds] = React.useState(90);
  const [voteSuspect, setVoteSuspect] = React.useState("");
  const [voteReason, setVoteReason] = React.useState("");
  const [voteEvidence, setVoteEvidence] = React.useState<string[]>([]);
  const [voteSubmitted, setVoteSubmitted] = React.useState(false);

  React.useEffect(() => {
    const timer = window.setInterval(() => {
      setSpeakerSeconds((value) => (value > 0 ? value - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [currentSpeaker]);

  const playerById = (playerId: string | null) => GAME_PLAYERS.find((item) => item.id === playerId);
  const current = playerById(currentSpeaker);
  const isUserSpeaking = currentSpeaker === "user";
  const userQueued = queue.includes("user");
  const currentIntroId = ["user", "chen", "crow", "su", "echo"].find((playerId) => !introduced.includes(playerId));
  const selectedPlayer = playerById(selectedPlayerId);
  const activeThread = privateThreads.find((item) => item.id === activeThreadId);
  const agents = GAME_PLAYERS.filter((player) => player.agent && player.id !== "dm");
  const dm = playerById("dm");

  React.useEffect(() => {
    try {
      window.localStorage.setItem(highlightStorageKey, JSON.stringify(scriptHighlights));
    } catch {
      // 浏览器禁用本地存储时仍允许继续游戏，只是不跨刷新保存。
    }
  }, [highlightStorageKey, scriptHighlights]);

  const addEvent = (event: PublicEventInput) => {
    setEvents((items) => [...items, { ...event, id: Date.now() } as PublicEvent]);
  };

  const showFeedback = (text: string) => setFeedback(text);

  const goToPhase = (index: number) => {
    if (phase.id === "role-selection" && index > 0 && !roleConfirmed) {
      showFeedback("请先确认角色，选角完成后才能进入后续阶段。");
      return;
    }
    if (index === 0 && roleConfirmed) {
      showFeedback("角色已确认，选角阶段不可再次进入。");
      return;
    }
    if (index > phaseIndex + 1) {
      showFeedback("请先完成当前阶段，不能跳过尚未完成的流程。");
      return;
    }
    setPhaseIndex(index);
    setSpeakerSeconds(90);
    if (GAME_PHASES[index].id === "discussion") {
      setCurrentSpeaker("chen");
      setQueue(["chen", "crow"]);
      addEvent({ type: "system", title: "阶段切换", text: "进入线索交流阶段，发言、私聊和证物操作已全部开放。" });
    }
  };

  const advancePhase = () => {
    if (phase.id === "role-selection" && !roleConfirmed) return showFeedback("请先确认角色。");
    if (phase.id === "script-reading" && !readingDone) return showFeedback("请阅读全部章节并确认完成。");
    if (phase.id === "intro" && introduced.length < 5) return showFeedback("仍有角色尚未完成自我介绍。");
    if (phase.id === "search" && searchesLeft > 0) return showFeedback("请使用完本阶段的搜证次数。");
    if (phaseIndex < GAME_PHASES.length - 1) goToPhase(phaseIndex + 1);
  };

  const joinQueue = () => {
    if (phase.id === "vote") return showFeedback("投票阶段已经停止新的发言申请。");
    if (forcedAnswer) return showFeedback("当前为强制回答，其他角色暂时不可插队。");
    if (userQueued || isUserSpeaking) return;
    setQueue((items) => [...items, "user"]);
    showFeedback(`已进入发言队列，当前排位 ${queue.length + 1}。`);
  };

  const cancelQueue = () => {
    setQueue((items) => items.filter((item) => item !== "user"));
    showFeedback("已取消发言申请。");
  };

  const finishSpeaker = () => {
    if (forcedAnswer && currentSpeaker === forcedAnswer.agentId) {
      addEvent({
        type: "speech",
        speaker: `${playerById(forcedAnswer.agentId)?.name} Agent`,
        text: `关于“${forcedAnswer.question}”，我认为值班表压痕说明修改发生在旧终端，而钥匙的持有者需要重点排查。`,
        tone: "blue",
      });
      setForcedAnswer(null);
    }
    setQueue((items) => {
      const remaining = items.filter((item) => item !== currentSpeaker);
      setCurrentSpeaker(remaining[0] || null);
      return remaining;
    });
    setSpeakerSeconds(90);
    showFeedback("当前发言已结束，发言权已交给队列中的下一位。");
  };

  const completeIntro = () => {
    if (!currentIntroId) return;
    const introPlayer = playerById(currentIntroId);
    setIntroduced((items) => [...items, currentIntroId]);
    addEvent({ type: "speech", speaker: introPlayer?.name || "", text: INTRO_LINES[currentIntroId], tone: introPlayer?.color || "gray" });
    showFeedback(`${introPlayer?.name} 已完成自我介绍。`);
  };

  const randomSearch = () => {
    if (searchesLeft <= 0) return;
    const available = SEARCH_EVIDENCE.filter((item) => !evidence.some((owned) => owned.id === item.id));
    const found = available[Math.floor(Math.random() * available.length)] || SEARCH_EVIDENCE[0];
    setEvidence((items) => [...items, found]);
    setNewEvidence(found);
    setSearchesLeft((value) => value - 1);
    showFeedback(`搜证成功：获得“${found.name}”，已存入我的证物。`);
  };

  const confirmForcedAnswer = () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能指定 Agent 回答。");
    const agent = playerById(targetId);
    if (!question.trim() || !agent) return showFeedback("请选择 Agent 并填写问题。");
    setForcedAnswer({ asker: "林晓青", agentId: targetId, question });
    setQueue((items) => [targetId, ...items.filter((item) => item !== targetId && item !== currentSpeaker)]);
    addEvent({ type: "forced", asker: "林晓青", agent: agent.name, question });
    setDialog(null);
    setQuestion("");
    showFeedback(`${agent.name} 已被指定为下一位发言者，其他角色不可插队。`);
  };

  const showEvidence = () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能出示证物。");
    const item = evidence.find((entry) => entry.id === selectedEvidenceId);
    if (!item) return;
    setEvidence((items) => items.map((entry) => entry.id === item.id ? { ...entry, visibility: evidenceVisibility as Evidence["visibility"] } : entry));
    addEvent({ type: "evidence", speaker: "林晓青", evidence: { ...item, visibility: evidenceVisibility as Evidence["visibility"] } });
    setDialog(null);
    showFeedback(`已出示“${item.name}”，公开范围：${evidenceVisibility}。`);
  };

  const acceptPrivateInvite = (playerId = targetId) => {
    const player = playerById(playerId);
    if (!player) return;
    const existing = privateThreads.find((thread) => thread.playerId === playerId);
    if (!existing) {
      const thread = {
        id: `${playerId}-thread-${Date.now()}`,
        playerId,
        name: player.name,
        unread: 0,
        permission: "主动发言" as const,
        messages: ["私聊已建立。公共讨论仍在继续，本会话内容仅双方可见。"],
      };
      setPrivateThreads((items) => [...items, thread]);
      setActiveThreadId(thread.id);
    } else {
      setActiveThreadId(existing.id);
    }
    setRightTab("private");
    setDialog(null);
    showFeedback(`已与 ${player.name} 建立私聊，公共发言队列未受影响。`);
  };

  const sendPublicMessage = () => {
    if (!publicMessage.trim()) return;
    if (!isUserSpeaking) return showFeedback("当前没有公共发言权，请先进入发言队列。");
    addEvent({ type: "speech", speaker: "林晓青", text: publicMessage.trim(), tone: "orange" });
    setPublicMessage("");
  };

  const sendPrivateMessage = () => {
    if (!privateMessage.trim() || !activeThread) return;
    setPrivateThreads((threads) => threads.map((thread) =>
      thread.id === activeThread.id ? { ...thread, messages: [...thread.messages, `我：${privateMessage.trim()}`] } : thread,
    ));
    setPrivateMessage("");
  };

  const submitVote = () => {
    if (!voteSuspect || !voteReason.trim() || voteEvidence.length === 0) {
      return showFeedback("请选择嫌疑人、填写推理理由并勾选至少一件关键证物。");
    }
    setVoteSubmitted(true);
    showFeedback("推理投票已提交。Agent 将独立提交推理，但不会替你修改选择。");
  };

  const playerStatus = (playerId: string) => {
    if (currentSpeaker === playerId) return "正在发言";
    if (queue.includes(playerId)) return "等待发言";
    return "思考中";
  };

  const captureScriptSelection = (chapterIndex: number) => {
    const selected = window.getSelection()?.toString().trim() || "";
    setSelectedScriptText(selected);
    setSelectedScriptChapter(chapterIndex);
  };

  const addScriptHighlight = () => {
    if (!selectedScriptText) {
      showFeedback("请先在剧本文本中选中需要高亮的语句。");
      return;
    }
    const duplicate = scriptHighlights.some(
      (item) => item.chapter === selectedScriptChapter && item.text === selectedScriptText,
    );
    if (!duplicate) {
      setScriptHighlights((items) => [
        ...items,
        {
          id: `${selectedScriptChapter}-${Date.now()}`,
          chapter: selectedScriptChapter,
          text: selectedScriptText,
        },
      ]);
    }
    setSelectedScriptText("");
    window.getSelection()?.removeAllRanges();
    showFeedback("高亮文段已保存。");
  };

  const removeScriptHighlight = (highlightId: string) => {
    setScriptHighlights((items) => items.filter((item) => item.id !== highlightId));
    showFeedback("高亮文段已删除。");
  };

  const renderHighlightedScript = (content: string, chapterIndex: number) => {
    const highlights = scriptHighlights
      .filter((item) => item.chapter === chapterIndex && content.includes(item.text))
      .sort((a, b) => content.indexOf(a.text) - content.indexOf(b.text));
    if (highlights.length === 0) return content;

    const parts: React.ReactNode[] = [];
    let cursor = 0;
    highlights.forEach((highlight) => {
      const start = content.indexOf(highlight.text, cursor);
      if (start < 0) return;
      if (start > cursor) parts.push(content.slice(cursor, start));
      parts.push(
        <mark key={highlight.id} className="game-script-highlight">
          {highlight.text}
        </mark>,
      );
      cursor = start + highlight.text.length;
    });
    if (cursor < content.length) parts.push(content.slice(cursor));
    return parts;
  };

  const renderEvent = (event: PublicEvent) => {
    if (event.type === "speech") {
      return (
        <Paper key={event.id} radius="lg" p="sm" className="game-chat-row">
          <Group align="flex-start" wrap="nowrap">
            <Avatar size="sm" color={event.tone}>{event.speaker.slice(0, 1)}</Avatar>
            <Box><Text size="sm" fw={800} c={`${event.tone}.3`}>{event.speaker}</Text><Text size="sm" c="gray.3">{event.text}</Text></Box>
          </Group>
        </Paper>
      );
    }
    if (event.type === "evidence") {
      return (
        <Paper key={event.id} radius="xl" p="md" className="game-evidence-event">
          <Text className="monospace-label" size="xs" c="orange.3">evidence presented</Text>
          <Group justify="space-between" mt={5}><Text fw={900}>{event.evidence.name}</Text><Badge>{event.evidence.visibility}</Badge></Group>
          <Text size="sm" c="dimmed" mt={6}>{event.evidence.description}</Text>
          <Group gap="lg" mt="sm"><Text size="xs">出示者：{event.speaker}</Text><Text size="xs">地点：{event.evidence.location}</Text><Text size="xs">时间：{event.evidence.time}</Text></Group>
        </Paper>
      );
    }
    if (event.type === "forced") {
      return (
        <Paper key={event.id} radius="xl" p="md" className="game-forced-event">
          <Text fw={900}>指定回答：{event.asker} → {event.agent}</Text>
          <Text size="sm" mt={5}>“{event.question}”</Text>
          <Text size="xs" c="red.3" mt={6}>被指定 Agent 必须成为下一位发言者，其他角色不可插队。</Text>
        </Paper>
      );
    }
    return (
      <Paper key={event.id} radius="lg" p="sm" className={event.type === "private" ? "game-private-event" : "game-system-event"}>
        <Text size="sm" fw={800}>{event.type === "private" ? `私聊申请 · ${event.agent}` : event.title}</Text>
        <Text size="sm" c="dimmed">{event.text}</Text>
      </Paper>
    );
  };

  const renderStage = () => {
    if (phase.id === "role-selection") {
      return (
        <Stack gap="md">
          <Group justify="space-between"><Box><Title order={3}>选择你的角色</Title><Text c="dimmed">查看公开身份与标签，确认后进入剧本阅读。</Text></Box><Badge>{roleConfirmed ? "已确认" : "待确认"}</Badge></Group>
          <Box className="game-role-grid">
            {ROLE_OPTIONS.map((role) => (
              <Paper key={role.id} radius="xl" p="md" className={selectedRole === role.id ? "game-role-card is-selected" : "game-role-card"}>
                <Group justify="space-between"><Avatar color={role.color}>{role.role.slice(0, 1)}</Avatar>{role.agent && <Badge color="blue">Agent</Badge>}</Group>
                <Text fw={900} mt="sm">{role.role}</Text><Text size="sm" c="dimmed">{role.publicIdentity}</Text>
                <Group gap={5} mt="sm">{role.tags.map((tag) => <Badge key={tag} size="xs" variant="light" color="gray">{tag}</Badge>)}</Group>
                <Text size="sm" mt="sm" lineClamp={3}>{role.background}</Text>
                <Button fullWidth mt="md" radius="xl" variant={selectedRole === role.id ? "filled" : "light"} disabled={roleConfirmed || Boolean(role.selectedBy && role.id !== selectedRole)} onClick={() => setSelectedRole(role.id)}>
                  {role.selectedBy && role.id !== selectedRole ? `已由 ${role.selectedBy} 选择` : selectedRole === role.id ? "当前选择" : "选择角色"}
                </Button>
              </Paper>
            ))}
          </Box>
          <Button
            radius="xl"
            onClick={() => {
              setRoleConfirmed(true);
              setPhaseIndex(1);
              showFeedback("角色已确认并锁定，已进入阅读剧本阶段。");
            }}
          >
            确认选角并进入剧本
          </Button>
        </Stack>
      );
    }
    if (phase.id === "script-reading") {
      const item = SCRIPT_CHAPTERS[chapter];
      return (
        <Stack gap="md">
          <Paper radius="xl" p="xl" className="game-reading-card">
            <Text className="monospace-label" size="xs" c="red.3">private script / chapter {chapter + 1}</Text>
            <Title order={2} mt="sm">{item.title}</Title>
            <Text
              fz="lg"
              lh={1.9}
              mt="lg"
              className="game-script-selectable"
              onMouseUp={() => captureScriptSelection(chapter)}
            >
              {renderHighlightedScript(item.content, chapter)}
            </Text>
            <Group justify="space-between" mt="xl">
              <Text size="sm" c="dimmed">
                选中剧本中的具体语句后，可保存为个人高亮。
              </Text>
              <Button
                size="xs"
                variant="light"
                color="yellow"
                leftSection={<IconHighlight size={15} />}
                disabled={!selectedScriptText || selectedScriptChapter !== chapter}
                onClick={addScriptHighlight}
              >
                高亮选中文段
              </Button>
            </Group>
          </Paper>
          <Group justify="space-between">
            <Button variant="light" disabled={chapter === 0} onClick={() => setChapter((value) => value - 1)}>上一章节</Button>
            <Text size="sm" c="dimmed">{chapter + 1} / {SCRIPT_CHAPTERS.length}</Text>
            {chapter < SCRIPT_CHAPTERS.length - 1
              ? <Button onClick={() => setChapter((value) => value + 1)}>下一章节</Button>
              : <Button color="teal" leftSection={<IconCheck size={16} />} onClick={() => { setReadingDone(true); showFeedback("已确认阅读完成。"); }}>确认阅读完成</Button>}
          </Group>
        </Stack>
      );
    }
    if (phase.id === "intro") {
      const introPlayer = playerById(currentIntroId || null);
      return (
        <Stack gap="md">
          <Paper radius="xl" p="lg" className="game-speaker-control">
            <Group justify="space-between"><Box><Text size="xs" c="dimmed">当前自我介绍</Text><Title order={3}>{introPlayer?.name || "全部完成"} · {introPlayer?.role}</Title></Box><Badge color="orange">{introduced.length} / 5 已完成</Badge></Group>
            {introPlayer && <Text mt="md" c="dimmed">本阶段仅允许自我介绍和指定 Agent 自我介绍，不可出示证物、搜证或深入私聊。</Text>}
          </Paper>
          <Stack gap="xs">{events.filter((event) => event.type === "speech" && INTRO_LINES && Object.values(INTRO_LINES).includes(event.text)).map(renderEvent)}</Stack>
          {introPlayer && <Button onClick={completeIntro}>{introPlayer.id === "user" ? "完成我的自我介绍" : `模拟 ${introPlayer.name} 完成介绍`}</Button>}
        </Stack>
      );
    }
    if (phase.id === "search") {
      return (
        <Stack gap="md" align="center">
          <Paper radius="xl" p="xl" className="game-search-stage">
            <IconSearch size={42} /><Title order={2} mt="md">随机搜证</Title><Text c="dimmed" mt="sm">剩余搜证次数：{searchesLeft}</Text>
            <Progress value={(2 - searchesLeft) * 50} mt="lg" color="orange" />
            <Button size="lg" radius="xl" mt="xl" disabled={searchesLeft === 0} loading={false} onClick={randomSearch}>开始随机搜证</Button>
          </Paper>
          {newEvidence && <Paper radius="xl" p="lg" className="game-evidence-event"><Badge color="teal">新证物</Badge><Title order={3} mt="sm">{newEvidence.name}</Title><Text c="dimmed" mt="sm">{newEvidence.description}</Text><Text size="sm" mt="sm">默认公开范围：仅自己</Text></Paper>}
        </Stack>
      );
    }
    if (phase.id === "vote") {
      return (
        <Stack gap="md">
          <Paper radius="xl" p="lg" className="game-speaker-control"><Title order={3}>推理投票</Title><Text c="dimmed">新发言、私聊和证物出示已停止。请独立提交判断。</Text></Paper>
          {voteSubmitted ? (
            <Paper radius="xl" p="xl" className="game-vote-success"><IconCheck size={44} /><Title order={2} mt="md">投票已提交</Title><Text c="dimmed" mt="sm">等待其他玩家与 Agent 完成独立推理。</Text></Paper>
          ) : (
            <Paper radius="xl" p="lg" className="game-vote-form">
              <Select label="选择嫌疑人" value={voteSuspect} onChange={(value) => setVoteSuspect(value || "")} data={GAME_PLAYERS.filter((player) => !player.agent && player.id !== "user").map((player) => ({ value: player.id, label: `${player.role} · ${player.name}` }))} />
              <Textarea label="推理理由" mt="md" minRows={5} value={voteReason} onChange={(event) => setVoteReason(event.currentTarget.value)} />
              <Text fw={700} mt="md">选择关键证物</Text>
              <Checkbox.Group value={voteEvidence} onChange={setVoteEvidence}><Stack gap="xs" mt="xs">{evidence.map((item) => <Checkbox key={item.id} value={item.id} label={item.name} />)}</Stack></Checkbox.Group>
              <Button mt="xl" radius="xl" onClick={submitVote}>确认提交投票</Button>
            </Paper>
          )}
        </Stack>
      );
    }
    return (
      <Stack gap="md">
        <Paper radius="xl" p="md" className={forcedAnswer ? "game-speaker-control is-forced" : "game-speaker-control"}>
          <Group justify="space-between" align="flex-start">
            <Box><Text size="xs" c="dimmed">{forcedAnswer ? "强制回答中" : current ? "当前发言人" : "当前暂无角色发言"}</Text><Title order={3}>{current ? `${current.name} · ${current.role}` : `下一位：${playerById(queue[0])?.name || "等待申请"}`}</Title>{forcedAnswer && <Text size="sm" mt={5}>问题：{forcedAnswer.question}</Text>}</Box>
            <Stack gap={4} align="flex-end"><Badge color={forcedAnswer ? "red" : "orange"} leftSection={<IconClock size={13} />}>{formatTime(speakerSeconds)}</Badge><Text size="xs" c="dimmed">队列：{queue.map((item) => playerById(item)?.name).join(" → ") || "空"}</Text></Stack>
          </Group>
          <Group mt="md">{currentSpeaker && <Button size="xs" variant="light" onClick={finishSpeaker}>{current?.agent ? forcedAnswer ? "结束强制回答" : "跳过 Agent" : "结束发言"}</Button>}{current?.agent && <Button size="xs" variant="subtle">暂停 Agent</Button>}</Group>
        </Paper>
        <Paper className="game-scene-card" radius="xl"><Box className="game-scene-card__image" /><Stack className="game-scene-card__copy" gap="xs"><Badge color="red" variant="filled">DM 场景</Badge><Title order={3}>被雨水冲开的旧门</Title><Text c="gray.3">墙上的值班表缺失了一页，地面新鲜鞋印通向封死的 103 室。</Text></Stack></Paper>
        <Group justify="space-between"><Text fw={900}>公共讨论与事件</Text><Badge variant="light">自动记录</Badge></Group>
        <Stack gap="xs">{events.map(renderEvent)}</Stack>
        {phase.id === "discussion" && <Paper radius="xl" p="md" className="game-private-event"><Group justify="space-between"><Box><Text fw={900}>白鸦 Agent 申请私聊</Text><Text size="sm" c="dimmed">“我发现门禁记录存在一个不适合公开讨论的时间矛盾。”</Text></Box><Group><Button size="xs" onClick={() => { setTargetId("crow"); setDialog("private"); }}>允许</Button><Button size="xs" variant="light">稍后</Button><Button size="xs" variant="subtle" color="red">拒绝</Button></Group></Group></Paper>}
      </Stack>
    );
  };

  const renderRightPanel = () => (
    <Tabs value={rightTab} onChange={setRightTab} className="game-right-tabs">
      <Tabs.List grow>
        <Tabs.Tab value="script">剧本</Tabs.Tab><Tabs.Tab value="tasks">任务</Tabs.Tab><Tabs.Tab value="evidence">证物</Tabs.Tab><Tabs.Tab value="private">私聊 <Badge size="xs">{privateThreads.reduce((sum, item) => sum + item.unread, 0)}</Badge></Tabs.Tab>
      </Tabs.List>
      <ScrollArea className="game-right-tab-scroll" offsetScrollbars>
        <Tabs.Panel value="script" pt="md">
          <Stack gap="md">
            <Box>
              <Text className="monospace-label" size="xs" c="dimmed">my private script</Text>
              <Title order={3}>周野的剧本</Title>
              <Text size="sm" c="dimmed">可随时打开完整剧本，并管理已经保存的高亮文段。</Text>
            </Box>
            <Button
              fullWidth
              radius="xl"
              leftSection={<IconBook2 size={17} />}
              onClick={() => setDialog("script")}
            >
              打开我的剧本
            </Button>
            <Divider />
            <Group justify="space-between">
              <Text fw={800}>已保存高亮</Text>
              <Badge color="yellow" variant="light">{scriptHighlights.length}</Badge>
            </Group>
            {scriptHighlights.length > 0 ? (
              <Stack gap="xs">
                {scriptHighlights.map((highlight) => (
                  <Paper key={highlight.id} p="sm" radius="lg" className="game-highlight-summary">
                    <Group justify="space-between" align="flex-start" wrap="nowrap">
                      <Box>
                        <Text size="xs" c="dimmed">{SCRIPT_CHAPTERS[highlight.chapter]?.title}</Text>
                        <Text size="sm" mt={4}>{highlight.text}</Text>
                      </Box>
                      <ActionIcon
                        size="sm"
                        variant="subtle"
                        color="red"
                        aria-label="删除高亮"
                        onClick={() => removeScriptHighlight(highlight.id)}
                      >
                        <IconX size={14} />
                      </ActionIcon>
                    </Group>
                  </Paper>
                ))}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">尚未高亮任何剧本文段。</Text>
            )}
          </Stack>
        </Tabs.Panel>
        <Tabs.Panel value="tasks" pt="md"><Stack gap="sm">{[{ label: "主线任务", text: "找到原始门禁记录", done: evidence.some((item) => item.id === "duty-sheet") }, { label: "隐藏任务", text: "避免过早暴露数据删除交易", done: false }, { label: "阶段任务", text: phase.id === "search" ? "完成两次搜证" : "推进当前游戏阶段", done: phase.id === "search" && searchesLeft === 0 }].map((task) => <Paper key={task.label} p="sm" radius="lg" className="game-clue-item"><Group justify="space-between"><Text fw={800}>{task.label}</Text><Badge color={task.done ? "teal" : "gray"}>{task.done ? "已完成" : "进行中"}</Badge></Group><Text size="sm" c="dimmed" mt={5}>{task.text}</Text></Paper>)}</Stack></Tabs.Panel>
        <Tabs.Panel value="evidence" pt="md"><Stack gap="sm">{evidence.map((item) => <Paper key={item.id} p="sm" radius="lg" className="game-clue-item"><Group justify="space-between"><Text fw={800}>{item.name}</Text><Badge size="xs">{item.visibility}</Badge></Group><Text size="sm" c="dimmed" mt={5}>{item.description}</Text><Text size="xs" mt="sm">获得方式：{item.source}</Text><Button size="xs" mt="sm" variant="light" disabled={!isUserSpeaking || phase.id !== "discussion"} onClick={() => { setSelectedEvidenceId(item.id); setDialog("evidence"); }}>出示证物</Button></Paper>)}</Stack></Tabs.Panel>
        <Tabs.Panel value="private" pt="md"><Group gap="xs" mb="sm">{privateThreads.map((thread) => <Button key={thread.id} size="xs" variant={thread.id === activeThreadId ? "filled" : "light"} onClick={() => { setActiveThreadId(thread.id); setPrivateThreads((items) => items.map((item) => item.id === thread.id ? { ...item, unread: 0 } : item)); }}>{thread.name}{thread.unread > 0 && ` (${thread.unread})`}</Button>)}</Group>{activeThread ? <Stack gap="sm"><Group justify="space-between"><Text fw={900}>{activeThread.name}</Text><Button size="xs" variant="subtle" color="red" onClick={() => setPrivateThreads((items) => items.filter((item) => item.id !== activeThread.id))}>结束私聊</Button></Group><Stack gap="xs">{activeThread.messages.map((text, index) => <Paper key={index} p="sm" radius="lg" className="game-private-chat"><Text size="sm">{text}</Text></Paper>)}</Stack><TextInput value={privateMessage} onChange={(event) => setPrivateMessage(event.currentTarget.value)} placeholder="输入私聊内容…" rightSection={<ActionIcon onClick={sendPrivateMessage}><IconSend size={15} /></ActionIcon>} /></Stack> : <Text c="dimmed">暂无私聊会话。</Text>}</Tabs.Panel>
      </ScrollArea>
    </Tabs>
  );

  const footerActions = () => {
    if (phase.id === "vote") return <Text c="dimmed">投票阶段：公共发言、私聊和证物操作已锁定。</Text>;
    if (phase.id !== "discussion") return <Group><Button radius="xl" onClick={advancePhase} disabled={(phase.id === "role-selection" && !roleConfirmed) || (phase.id === "script-reading" && !readingDone) || (phase.id === "intro" && introduced.length < 5) || (phase.id === "search" && searchesLeft > 0)}>进入下一阶段</Button><Text size="sm" c="dimmed">完成当前阶段要求后继续</Text></Group>;
    return (
      <Group gap="xs" wrap="nowrap" style={{ width: "100%" }}>
        {!isUserSpeaking && !userQueued && <Button radius="xl" onClick={joinQueue} disabled={Boolean(forcedAnswer)}>选择发言</Button>}
        {userQueued && !isUserSpeaking && <Button radius="xl" variant="light" onClick={cancelQueue}>取消申请 · 排位 {queue.indexOf("user") + 1}</Button>}
        {isUserSpeaking && <Button radius="xl" color="orange" onClick={finishSpeaker}>结束发言</Button>}
        <Button radius="xl" variant="light" onClick={() => setDialog("private")}>发起私聊</Button>
        <Button radius="xl" variant="light" disabled={!isUserSpeaking} onClick={() => setDialog("force")}>指定 Agent 回答</Button>
        <Button radius="xl" variant="light" disabled={!isUserSpeaking} onClick={() => setDialog("evidence")}>出示证物</Button>
        <Button radius="xl" variant="subtle" color="orange" disabled={Boolean(forcedAnswer)} onClick={() => goToPhase(5)}>进入推理投票</Button>
        <TextInput value={publicMessage} onChange={(event) => setPublicMessage(event.currentTarget.value)} placeholder={isUserSpeaking ? "输入当前公共发言…" : "轮到你发言后可输入内容"} disabled={!isUserSpeaking} className="game-message-input" radius="xl" />
        <ActionIcon size="lg" radius="xl" onClick={sendPublicMessage} disabled={!isUserSpeaking}><IconSend size={17} /></ActionIcon>
      </Group>
    );
  };

  return (
    <StudioShell title="游戏主界面" subtitle={`当前剧本：${scriptTitle}。`} eyebrow="live game / interactive demo" stats={[{ label: "当前阶段", value: phase.shortLabel }, { label: "当前发言人", value: current?.name || "暂无" }, { label: "发言倒计时", value: formatTime(speakerSeconds) }, { label: "游戏模式", value: gameMode }]}>
      <Box className="game-stage-wrap">
        <Paper ref={fullscreenRef} radius={fullscreen ? 0 : "xl"} className={fullscreen ? "game-workspace is-fullscreen" : "game-workspace"}>
          <header className="game-workspace__header game-workspace__header--expanded">
            <Group justify="space-between" wrap="nowrap">
              <Group gap="md" wrap="nowrap">
                <Box>
                  <Text className="monospace-label" size="xs" c="red.3">live session / room 071</Text>
                  <Group gap="sm"><Title order={3}>{scriptTitle}</Title><Badge>{gameMode}</Badge></Group>
                </Box>
                <Divider orientation="vertical" visibleFrom="md" />
                <Paper className="game-dm-header-card" radius="lg" px="sm" py={6} visibleFrom="md">
                  <Group gap="xs" wrap="nowrap">
                    <Avatar size="sm" color={dm?.color || "red"}>{dm?.name.slice(0, 1)}</Avatar>
                    <Box>
                      <Group gap={5}>
                        <Text size="xs" fw={900}>DM · {dm?.role}</Text>
                        <Badge size="xs" color="red" variant="light">Agent</Badge>
                      </Group>
                      <Text size="xs" c="dimmed">{dm?.name} · 主持中</Text>
                    </Box>
                  </Group>
                </Paper>
                <Box visibleFrom="sm">
                  <Text size="xs" c="dimmed">当前发言 / 下一位</Text>
                  <Text fw={800}>{current?.role || "暂无"} → {playerById(queue.find((item) => item !== currentSpeaker) || null)?.role || "等待申请"}</Text>
                </Box>
              </Group>
              <Group gap="xs"><Badge size="lg" color="orange" leftSection={<IconClock size={13} />}>{formatTime(speakerSeconds)}</Badge><Button size="xs" variant="light" onClick={() => setDialog("rules")}>游戏规则</Button><Tooltip label={fullscreen ? "退出全屏" : "全屏"}><ActionIcon size="lg" onClick={toggleFullscreen}>{fullscreen ? <IconX size={18} /> : <IconMaximize size={18} />}</ActionIcon></Tooltip><ActionIcon size="lg" variant={settingsOpen ? "filled" : "light"} onClick={() => setSettingsOpen((value) => !value)}><IconSettings size={18} /></ActionIcon><Button size="xs" color="red" variant="subtle" onClick={() => navigate("/games")}>退出</Button></Group>
            </Group>
            <Box className="game-phase-track">{GAME_PHASES.map((item, index) => <button key={item.id} disabled={index === 0 && roleConfirmed} className={`${index < phaseIndex ? "game-phase-step is-complete" : index === phaseIndex ? "game-phase-step is-active" : "game-phase-step"}${index === 0 && roleConfirmed ? " is-locked" : ""}`} onClick={() => goToPhase(index)}><span>{index < phaseIndex ? "✓" : index + 1}</span><Text size="xs">{item.shortLabel}</Text></button>)}</Box>
          </header>

          {settingsOpen && (
            <Paper className="game-settings-strip game-settings-strip--phased" radius={0} px="lg" py="sm">
              <Group justify="space-between">
                <Group gap="xs">
                  <Badge variant="light">字幕：开启</Badge>
                  <Badge variant="light">音效：70%</Badge>
                  <Badge variant="light">Agent 节奏：适中</Badge>
                </Group>
                <Text size="sm" c="dimmed">演示设置仅保存在当前页面状态。</Text>
              </Group>
            </Paper>
          )}

          {feedback && <Paper className="game-feedback" radius="md" px="md" py={6}><Group justify="space-between"><Text size="sm">{feedback}</Text><ActionIcon size="xs" variant="subtle" onClick={() => setFeedback("")}><IconX size={13} /></ActionIcon></Group></Paper>}

          <main className="game-workspace__body game-workspace__body--phased">
            <aside className="game-side-panel game-people-panel">
              <Group justify="space-between" mb="md"><Group gap="xs"><IconUsers size={18} /><Text fw={900}>玩家与 Agent</Text></Group><Badge color="teal">6 在线</Badge></Group>
              <ScrollArea className="game-panel-scroll" offsetScrollbars>
                <Stack gap="xs">
                  {GAME_PLAYERS.filter((player) => player.id !== "dm").map((player) => {
                    const status = playerStatus(player.id);
                    const isSelf = player.id === "user";
                    const classNames = [
                      "game-player",
                      currentSpeaker === player.id ? "is-speaking" : "",
                      selectedPlayerId === player.id ? "is-selected" : "",
                      isSelf ? "is-self" : "",
                    ].filter(Boolean).join(" ");
                    return (
                      <Paper key={player.id} p="sm" radius="lg" className={classNames} onClick={() => setSelectedPlayerId(player.id)} style={{ cursor: "pointer" }}>
                        <Group wrap="nowrap">
                          <Box className="game-avatar-wrap"><Avatar color={player.color}>{player.role.slice(0, 1)}</Avatar><Box className="game-online-dot" /></Box>
                          <Box style={{ flex: 1, minWidth: 0 }}>
                            <Group gap={5}>
                              <Text fw={900} truncate>{player.role}</Text>
                              {isSelf && <Badge size="xs" color="orange" variant="filled">我</Badge>}
                            </Group>
                            <Text size="xs" c="dimmed" truncate>玩家：{player.name}</Text>
                          </Box>
                          <Badge size="xs" color={status === "正在发言" ? "orange" : status === "思考中" ? "blue" : "gray"} variant="dot">{status}</Badge>
                        </Group>
                      </Paper>
                    );
                  })}
                </Stack>
              </ScrollArea>
              {selectedPlayer && selectedPlayer.id !== "dm" && <Paper p="sm" radius="lg" className="game-player-actions"><Text fw={800}>{selectedPlayer.role} · 快捷操作</Text><Group gap={5} mt="sm"><Button size="xs" variant="light" onClick={() => showFeedback(`${selectedPlayer.role} 的公开身份：${selectedPlayer.publicIdentity}`)}>公开信息</Button>{selectedPlayer.id !== "user" && <Button size="xs" variant="light" onClick={() => { setTargetId(selectedPlayer.id); setDialog("private"); }}>发起私聊</Button>}{selectedPlayer.agent && <Button size="xs" variant="light" disabled={!isUserSpeaking} onClick={() => { setTargetId(selectedPlayer.id); setDialog("force"); }}>指定回答</Button>}</Group></Paper>}
            </aside>

            <section className="game-core-panel"><ScrollArea className="game-core-scroll" offsetScrollbars>{renderStage()}</ScrollArea></section>
            <aside className="game-side-panel game-personal-panel">{renderRightPanel()}</aside>
          </main>

          <footer className="game-workspace__footer game-workspace__footer--actions">{footerActions()}</footer>
        </Paper>
      </Box>

      <Modal opened={dialog === "force"} onClose={() => setDialog(null)} title="指定 Agent 回答" centered><Stack><Select label="选择 Agent" value={targetId} onChange={(value) => setTargetId(value || "crow")} data={agents.map((agent) => ({ value: agent.id, label: `${agent.name} · ${agent.role}` }))} /><Textarea label="需要回答的问题" value={question} onChange={(event) => setQuestion(event.currentTarget.value)} minRows={4} /><Button onClick={confirmForcedAnswer}>确认指定</Button></Stack></Modal>
      <Modal opened={dialog === "evidence"} onClose={() => setDialog(null)} title="出示证物" centered><Stack><Select label="选择证物" value={selectedEvidenceId} onChange={(value) => setSelectedEvidenceId(value || evidence[0]?.id)} data={evidence.map((item) => ({ value: item.id, label: item.name }))} /><Radio.Group label="公开范围" value={evidenceVisibility} onChange={setEvidenceVisibility}><Stack mt="xs"><Radio value="所有人" label="公开给所有人" /><Radio value="指定角色" label="只分享给指定角色" /></Stack></Radio.Group>{evidenceVisibility === "指定角色" && <Select label="指定角色" value={targetId} onChange={(value) => setTargetId(value || "chen")} data={GAME_PLAYERS.filter((player) => player.id !== "user").map((player) => ({ value: player.id, label: player.name }))} />}<Button onClick={showEvidence}>确认出示</Button></Stack></Modal>
      <Modal opened={dialog === "private"} onClose={() => setDialog(null)} title="发起或接受私聊" centered><Stack><Select label="私聊对象" value={targetId} onChange={(value) => setTargetId(value || "crow")} data={GAME_PLAYERS.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({ value: player.id, label: `${player.role} · 玩家：${player.name}` }))} /><Text size="sm" c="dimmed">私聊建立后即可直接对话，不需要额外设置 Agent 发言权限；私聊内容和证物不会自动公开。</Text><Button onClick={() => acceptPrivateInvite()}>建立私聊</Button></Stack></Modal>
      <Modal opened={dialog === "rules"} onClose={() => setDialog(null)} title="游戏规则" centered size="lg"><Stack><Text>公共讨论采用单一发言权，普通发言按申请顺序进行。</Text><Text>被指定回答的 Agent 必须成为下一位发言者，回答结束后恢复原队列。</Text><Text>私聊与公共讨论独立运行，私聊内容和证物仅参与者可见。</Text><Text>进入投票阶段后停止新的发言、私聊和证物出示。</Text></Stack></Modal>
      <Modal
        opened={dialog === "script"}
        onClose={() => {
          setDialog(null);
          setSelectedScriptText("");
        }}
        title="我的剧本 · 周野"
        centered
        size="xl"
        scrollAreaComponent={ScrollArea.Autosize}
      >
        <Stack gap="lg">
          <Text size="sm" c="dimmed">拖动选中具体语句，再点击“高亮选中文段”。高亮会自动保存在当前浏览器。</Text>
          {SCRIPT_CHAPTERS.map((item, chapterIndex) => (
            <Paper key={item.title} radius="xl" p="lg" className="game-script-modal-chapter">
              <Group justify="space-between" align="flex-start">
                <Title order={3}>{item.title}</Title>
                <Badge color="yellow" variant="light">
                  {scriptHighlights.filter((highlight) => highlight.chapter === chapterIndex).length} 处高亮
                </Badge>
              </Group>
              <Text
                mt="md"
                lh={1.9}
                className="game-script-selectable"
                onMouseUp={() => captureScriptSelection(chapterIndex)}
              >
                {renderHighlightedScript(item.content, chapterIndex)}
              </Text>
              <Group justify="flex-end" mt="md">
                <Button
                  size="xs"
                  color="yellow"
                  variant="light"
                  leftSection={<IconHighlight size={15} />}
                  disabled={!selectedScriptText || selectedScriptChapter !== chapterIndex}
                  onClick={addScriptHighlight}
                >
                  高亮选中文段
                </Button>
              </Group>
            </Paper>
          ))}
          {scriptHighlights.length > 0 && (
            <Box>
              <Title order={4}>管理高亮</Title>
              <Stack gap="xs" mt="sm">
                {scriptHighlights.map((highlight) => (
                  <Paper key={highlight.id} radius="lg" p="sm" className="game-highlight-summary">
                    <Group justify="space-between" wrap="nowrap">
                      <Box>
                        <Text size="xs" c="dimmed">{SCRIPT_CHAPTERS[highlight.chapter]?.title}</Text>
                        <Text size="sm">{highlight.text}</Text>
                      </Box>
                      <Button size="xs" variant="subtle" color="red" onClick={() => removeScriptHighlight(highlight.id)}>
                        删除
                      </Button>
                    </Group>
                  </Paper>
                ))}
              </Stack>
            </Box>
          )}
        </Stack>
      </Modal>
    </StudioShell>
  );
}

export { GamePage };
