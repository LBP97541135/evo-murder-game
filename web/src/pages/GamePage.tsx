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
import { backendEvidenceToGameEvidence } from "../api/adapters";
import {
  createEvidence,
  createGameSession,
  forceGamePhase,
  getGamePhase,
  getEvidences,
  presentEvidence,
  saveConversation,
  submitGameVote,
} from "../api/invoke";
import { AgentCastingPanel } from "../components/AgentCastingPanel";
import { StudioShell } from "./StudioShell";

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

const scriptMap: Record<string, string> = {
  "iron-avenue": "锈铁大道",
  "black-archive": "黑箱档案馆",
  "mirror-parade": "镜面游行",
  "salt-ward": "盐雾病房",
  "wolf-assembly": "狼群集会",
  "paper-cathedral": "纸穹教堂",
};

type PublicEvent =
  | { id: number; type: "speech"; speaker: string; text: string; tone: string; suspectId?: string; evidenceId?: string }
  | { id: number; type: "system"; title: string; text: string }
  | { id: number; type: "evidence"; speaker: string; evidence: Evidence; reason?: string; suspectId?: string }
  | { id: number; type: "forced"; asker: string; agent: string; question: string }
  | { id: number; type: "private"; agent: string; text: string }
  | { id: number; type: "accusation"; actor: string; target: string; sourceTitle: string; reason?: string }
  | { id: number; type: "inquiry"; asker: string; target: string; sourceTitle: string; question: string; answer: string };

type PublicEventInput =
  | { type: "speech"; speaker: string; text: string; tone: string; suspectId?: string; evidenceId?: string }
  | { type: "system"; title: string; text: string }
  | { type: "evidence"; speaker: string; evidence: Evidence; reason?: string; suspectId?: string }
  | { type: "forced"; asker: string; agent: string; question: string }
  | { type: "private"; agent: string; text: string }
  | { type: "accusation"; actor: string; target: string; sourceTitle: string; reason?: string }
  | { type: "inquiry"; asker: string; target: string; sourceTitle: string; question: string; answer: string };

type DialogType =
  | "private"
  | "force"
  | "evidence"
  | "evidence-detail"
  | "discussion-detail"
  | "point"
  | "inquiry"
  | "rules"
  | "script"
  | null;

type InquiryRecord = {
  id: number;
  sourceEventId: number;
  sourceType: "证据" | "关键发言";
  sourceTitle: string;
  evidence?: Evidence;
  targetId: string;
  targetName: string;
  question: string;
  answer: string;
};

type ScriptHighlight = {
  id: string;
  chapter: number;
  text: string;
};

const initialEvents: PublicEvent[] = [
  { id: 1, type: "system", title: "阶段开始", text: "公共讨论已开启，所有发言按照队列顺序进行。" },
  {
    id: 2,
    type: "speech",
    speaker: "陈墨",
    text: "我保管的事故档案里，值班表在十二年前归档时就已经缺失了一页。最近出现的这张表不是原件，我想先确认它究竟是什么时候被替换的，以及谁有机会接触旧档案室。",
    tone: "teal",
    suspectId: "echo",
  },
  {
    id: 3,
    type: "speech",
    speaker: "白鸦 Agent",
    text: "访客卡背面的锈迹呈现规则的长方形边框，更像地下储物柜的编号牌，而不是宿舍门牌。卡片断口还有新鲜摩擦痕迹，说明它最近曾被人从狭窄金属缝隙中取出。",
    tone: "blue",
    suspectId: "echo",
    evidenceId: "visitor-card",
  },
  { id: 4, type: "evidence", speaker: "白鸦 Agent", evidence: INITIAL_EVIDENCE[0], reason: "访客卡背面的锈迹可能对应地下储物柜。" },
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
  const [sessionId, setSessionId] = React.useState(
    () => window.localStorage.getItem(`game-session:${id}`) || "",
  );
  const phase = GAME_PHASES[phaseIndex];
  const [selectedRole, setSelectedRole] = React.useState("");
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
  const [evidence, setEvidence] = React.useState<Evidence[]>([]);
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
  const [selectedEvidenceId, setSelectedEvidenceId] = React.useState("");
  const [evidenceVisibility, setEvidenceVisibility] = React.useState("所有人");
  const [evidenceReason, setEvidenceReason] = React.useState("");
  const [privateThreads, setPrivateThreads] = React.useState(PRIVATE_THREADS);
  const [activeThreadId, setActiveThreadId] = React.useState(PRIVATE_THREADS[0].id);
  const [privateMessage, setPrivateMessage] = React.useState("");
  const [publicMessage, setPublicMessage] = React.useState("");
  const [feedback, setFeedback] = React.useState("欢迎进入游戏，请点击圆桌席位选择你喜欢的角色");
  const [settingsOpen, setSettingsOpen] = React.useState(false);
  const [speakerSeconds, setSpeakerSeconds] = React.useState(90);
  const [voteSuspect, setVoteSuspect] = React.useState("");
  const [voteReason, setVoteReason] = React.useState("");
  const [voteEvidence, setVoteEvidence] = React.useState<string[]>([]);
  const [voteSubmitted, setVoteSubmitted] = React.useState(false);
  const [introSpotlight, setIntroSpotlight] = React.useState<(typeof GAME_PLAYERS)[number] | null>(null);
  const [selectedDiscussionEventId, setSelectedDiscussionEventId] = React.useState<number | null>(null);
  const [selectedDetailEvidence, setSelectedDetailEvidence] = React.useState<Evidence | null>(null);
  const [pointTargetId, setPointTargetId] = React.useState("chen");
  const [pointReason, setPointReason] = React.useState("");
  const [inquiryTargetId, setInquiryTargetId] = React.useState("crow");
  const [inquiryQuestion, setInquiryQuestion] = React.useState("");
  const [inquiryRecords, setInquiryRecords] = React.useState<InquiryRecord[]>([]);
  const [privateInviteStatus, setPrivateInviteStatus] = React.useState<"未处理" | "稍后处理" | "已接受" | "已拒绝">("未处理");
  const [chatHistoryOpen, setChatHistoryOpen] = React.useState(false);

  React.useEffect(() => {
    const timer = window.setInterval(() => {
      setSpeakerSeconds((value) => (value > 0 ? value - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [currentSpeaker]);

  React.useEffect(() => {
    if (!sessionId) return;
    getEvidences(id, sessionId)
      .then((result) => {
        const records = result.evidences.map(backendEvidenceToGameEvidence);
        setEvidence(records);
        setSelectedEvidenceId((current) => current || records[0]?.id || "");
      })
      .catch((error) => {
        showFeedback(`后端证物加载失败：${error instanceof Error ? error.message : String(error)}`);
      });
  }, [id, sessionId]);

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

  const confirmRoleSelection = async () => {
    if (!selectedRole) return;
    try {
      let activeSessionId = sessionId;
      if (activeSessionId) {
        await getGamePhase(activeSessionId);
      } else {
        const session = await createGameSession(id, `剧本游戏：${scriptTitle}`);
        activeSessionId = session.sessionId;
        setSessionId(activeSessionId);
        window.localStorage.setItem(`game-session:${id}`, activeSessionId);
      }
      setRoleConfirmed(true);
      setPhaseIndex(1);
      showFeedback(`角色已确认，后端游戏会话 ${activeSessionId} 可用。`);
    } catch (error) {
      showFeedback(`无法确认角色：后端游戏会话创建或恢复失败：${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const backendPhaseForIndex = (index: number) => {
    if (index <= 2) return "intro";
    if (index <= 4) return "investigation";
    return "voting";
  };

  const goToPhase = async (index: number) => {
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
    if (!sessionId) {
      showFeedback("无法切换阶段：尚未创建后端游戏会话。");
      return;
    }
    try {
      await forceGamePhase(sessionId, backendPhaseForIndex(index));
    } catch (error) {
      showFeedback(`后端阶段切换失败：${error instanceof Error ? error.message : String(error)}`);
      return;
    }
    setPhaseIndex(index);
    setSpeakerSeconds(90);
    if (GAME_PHASES[index].id === "discussion") {
      setCurrentSpeaker("chen");
      setQueue(["chen", "crow"]);
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
    if (!introPlayer) return;
    setIntroduced((items) => [...items, currentIntroId]);
    addEvent({ type: "speech", speaker: introPlayer.name, text: INTRO_LINES[currentIntroId], tone: introPlayer.color || "gray" });
    setIntroSpotlight(introPlayer);
    showFeedback(`${introPlayer.name} 已完成自我介绍。`);
  };

  const randomSearch = async () => {
    if (searchesLeft <= 0) return;
    if (!sessionId) return showFeedback("搜证失败：尚未创建后端游戏会话。");
    const available = SEARCH_EVIDENCE.filter((item) => !evidence.some((owned) => owned.id === item.id));
    const found = available[Math.floor(Math.random() * available.length)] || SEARCH_EVIDENCE[0];
    try {
      const result = await createEvidence({
        scriptId: id,
        sessionId,
        name: found.name,
        basicDescription: found.description,
        category: found.icon || "physical",
        importance: "medium",
        relatedActors: [],
        discoveredBy: "player",
      });
      const saved = result.evidence ? backendEvidenceToGameEvidence(result.evidence) : found;
      setEvidence((items) => [...items, saved]);
      setSelectedEvidenceId((currentId) => currentId || saved.id);
      setNewEvidence(saved);
      setSearchesLeft((value) => value - 1);
      showFeedback(`搜证成功：后端已保存“${saved.name}”。`);
    } catch (error) {
      showFeedback(`后端搜证失败：${error instanceof Error ? error.message : String(error)}`);
    }
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

  const showEvidence = async () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能出示证物。");
    if (!sessionId) return showFeedback("出示证物失败：尚未创建后端游戏会话。");
    const item = evidence.find((entry) => entry.id === selectedEvidenceId);
    if (!item) return;
    const reason = evidenceReason.trim();
    try {
      await presentEvidence(
        item.id,
        evidenceVisibility === "指定角色" ? targetId : "all",
        "player",
        reason,
        evidenceVisibility,
      );
    } catch (error) {
      showFeedback(`后端出示证物失败：${error instanceof Error ? error.message : String(error)}`);
      return;
    }
    setEvidence((items) => items.map((entry) => entry.id === item.id ? { ...entry, visibility: evidenceVisibility as Evidence["visibility"] } : entry));
    addEvent({
      type: "evidence",
      speaker: "林晓青",
      evidence: { ...item, visibility: evidenceVisibility as Evidence["visibility"] },
      reason: evidenceReason.trim() || undefined,
    });
    setDialog(null);
    setEvidenceReason("");
    showFeedback(`后端已记录出示“${item.name}”，公开范围：${evidenceVisibility}。`);
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
    setRightTab("chat");
    setDialog(null);
    showFeedback(`已与 ${player.name} 建立私聊，公共发言队列未受影响。`);
  };

  const sendPublicMessage = async () => {
    if (!publicMessage.trim()) return;
    if (!isUserSpeaking) return showFeedback("当前没有公共发言权，请先进入发言队列。");
    if (!sessionId) return showFeedback("发送失败：尚未创建后端游戏会话。");
    const content = publicMessage.trim();
    try {
      await saveConversation({
        sessionId,
        actorName: "player",
        chatMessages: [{ role: "user", content }],
        finalResponse: content,
      });
      addEvent({ type: "speech", speaker: "林晓青", text: content, tone: "orange" });
      setPublicMessage("");
    } catch (error) {
      showFeedback(`后端保存公开发言失败：${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const sendPrivateMessage = async () => {
    if (!privateMessage.trim() || !activeThread) return;
    if (!sessionId) return showFeedback("发送失败：尚未创建后端游戏会话。");
    const content = privateMessage.trim();
    try {
      await saveConversation({
        sessionId,
        actorName: activeThread.playerId,
        chatMessages: [{ role: "user", content }],
      });
      setPrivateThreads((threads) => threads.map((thread) =>
        thread.id === activeThread.id ? { ...thread, messages: [...thread.messages, `我：${content}`] } : thread,
      ));
      setPrivateMessage("");
    } catch (error) {
      showFeedback(`后端保存私聊失败：${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const submitVote = async () => {
    if (!voteSuspect || !voteReason.trim() || voteEvidence.length === 0) {
      return showFeedback("请选择嫌疑人、填写推理理由并勾选至少一件关键证物。");
    }
    if (!sessionId) return showFeedback("投票失败：尚未创建后端游戏会话。");
    try {
      await forceGamePhase(sessionId, "voting");
      const result = await submitGameVote(sessionId, voteSuspect, voteReason);
      setVoteSubmitted(true);
      showFeedback(result.message || "推理投票已写入后端。");
    } catch (error) {
      showFeedback(`后端投票失败：${error instanceof Error ? error.message : String(error)}`);
    }
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

  const discussionSource = (eventId: number | null) => {
    const event = events.find((item) => item.id === eventId);
    if (!event || (event.type !== "speech" && event.type !== "evidence")) return null;
    return event;
  };

  const discussionSourceTitle = (event: Extract<PublicEvent, { type: "speech" | "evidence" }>) =>
    event.type === "evidence" ? event.evidence.name : `${event.speaker} 的发言`;

  const openEvidenceDetail = (item: Evidence) => {
    setSelectedDetailEvidence(item);
    setDialog("evidence-detail");
  };

  const openPointDialog = (eventId: number) => {
    setSelectedDiscussionEventId(eventId);
    setPointTargetId("chen");
    setPointReason("");
    setDialog("point");
  };

  const openDiscussionDetail = (eventId: number) => {
    setSelectedDiscussionEventId(eventId);
    setDialog("discussion-detail");
  };

  const confirmPoint = () => {
    const source = discussionSource(selectedDiscussionEventId);
    const target = playerById(pointTargetId);
    if (!source || !target) return;
    setEvents((items) => items.map((item) =>
      item.id === source.id && (item.type === "speech" || item.type === "evidence")
        ? { ...item, suspectId: target.id }
        : item,
    ));
    addEvent({
      type: "accusation",
      actor: "林晓青",
      target: `${target.role} · ${target.name}`,
      sourceTitle: discussionSourceTitle(source),
      reason: pointReason.trim() || undefined,
    });
    setDialog(null);
    showFeedback(`已将“${discussionSourceTitle(source)}”指向 ${target.role}。`);
  };

  const openInquiryDialog = (eventId: number) => {
    setSelectedDiscussionEventId(eventId);
    setInquiryTargetId("crow");
    setInquiryQuestion("");
    setDialog("inquiry");
  };

  const confirmInquiry = () => {
    const source = discussionSource(selectedDiscussionEventId);
    const target = playerById(inquiryTargetId);
    if (!source || !target || !inquiryQuestion.trim()) {
      showFeedback("请选择质询对象并填写问题。");
      return;
    }
    const sourceTitle = discussionSourceTitle(source);
    const answer = source.type === "evidence"
      ? `我检查过“${source.evidence.name}”的来源。它能证明时间和地点存在关联，但还不能单独证明持有人身份。`
      : `关于这段发言，我的判断是其中有一处时间顺序需要复核。我愿意把相关行动记录公开出来接受比对。`;
    const record: InquiryRecord = {
      id: Date.now(),
      sourceEventId: source.id,
      sourceType: source.type === "evidence" ? "证据" : "关键发言",
      sourceTitle,
      evidence: source.type === "evidence" ? source.evidence : undefined,
      targetId: target.id,
      targetName: `${target.role} · ${target.name}`,
      question: inquiryQuestion.trim(),
      answer,
    };
    setInquiryRecords((items) => [...items, record]);
    addEvent({
      type: "inquiry",
      asker: "林晓青",
      target: record.targetName,
      sourceTitle,
      question: record.question,
      answer,
    });
    setRightTab("chat");
    setDialog(null);
    setInquiryQuestion("");
    showFeedback(`已完成对 ${target.role} 的质询，记录已保存到证物栏。`);
  };

  const selectedDiscussionSource = discussionSource(selectedDiscussionEventId);
  const selectedDiscussionSpeaker = selectedDiscussionSource
    ? GAME_PLAYERS.find((player) =>
      selectedDiscussionSource.type === "speech"
        ? selectedDiscussionSource.speaker.includes(player.name)
        : selectedDiscussionSource.speaker.includes(player.name),
    )
    : undefined;
  const selectedDiscussionSuspect = selectedDiscussionSource?.suspectId
    ? playerById(selectedDiscussionSource.suspectId)
    : undefined;
  const selectedDiscussionEvidence = selectedDiscussionSource?.type === "evidence"
    ? selectedDiscussionSource.evidence
    : selectedDiscussionSource?.type === "speech" && selectedDiscussionSource.evidenceId
      ? evidence.find((item) => item.id === selectedDiscussionSource.evidenceId)
      : undefined;

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
        <Paper
          key={event.id}
          radius="lg"
          p="sm"
          className="game-chat-row game-discussion-entry"
          onClick={() => phase.id === "discussion" && openDiscussionDetail(event.id)}
        >
          <Group align="flex-start" wrap="nowrap">
            {(() => {
              const speakerPlayer = GAME_PLAYERS.find((p) => p.name === event.speaker || `${p.name} Agent` === event.speaker);
              const speakerPortrait = speakerPlayer ? characterPortraits[speakerPlayer.role] : undefined;
              return speakerPortrait ? (
                <Avatar src={speakerPortrait} size="sm" imageProps={{ style: { objectPosition: "top" } }} />
              ) : (
                <Avatar size="sm" color={event.tone}>{event.speaker.slice(0, 1)}</Avatar>
              );
            })()}
            <Box style={{ flex: 1 }}>
              <Text size="sm" fw={800} c={`${event.tone}.3`}>{event.speaker}</Text>
              <Text size="sm" c="gray.3" lh={1.65}>{event.text}</Text>
              {phase.id === "discussion" && <Text size="xs" c="dimmed" mt={6}>点击查看发言详情</Text>}
            </Box>
          </Group>
        </Paper>
      );
    }
    if (event.type === "evidence") {
      return (
        <Paper
          key={event.id}
          radius="xl"
          p="md"
          className="game-evidence-event game-discussion-entry"
          onClick={() => phase.id === "discussion" && openDiscussionDetail(event.id)}
        >
          <Text className="monospace-label" size="xs" c="orange.3">evidence presented</Text>
          <Group justify="space-between" mt={5}>
            <Button
              variant="transparent"
              color="orange"
              p={0}
              onClick={(clickEvent) => {
                clickEvent.stopPropagation();
                openEvidenceDetail(event.evidence);
              }}
              className="game-evidence-link"
            >
              {event.evidence.name}
            </Button>
            <Badge>{event.evidence.visibility}</Badge>
          </Group>
          <Text size="sm" c="dimmed" mt={6}>{event.evidence.description}</Text>
          {event.reason && <Text size="sm" mt={6}>出示理由：{event.reason}</Text>}
          <Group gap="lg" mt="sm"><Text size="xs">出示者：{event.speaker}</Text><Text size="xs">地点：{event.evidence.location}</Text><Text size="xs">时间：{event.evidence.time}</Text></Group>
          {phase.id === "discussion" && <Text size="xs" c="dimmed" mt="sm">点击查看证据与发言详情</Text>}
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
    if (event.type === "accusation") {
      return (
        <Paper key={event.id} radius="lg" p="sm" className="game-accusation-event">
          <Text fw={900}>{event.actor} 将“{event.sourceTitle}”指向 {event.target}</Text>
          {event.reason && <Text size="sm" c="dimmed" mt={5}>理由：{event.reason}</Text>}
        </Paper>
      );
    }
    if (event.type === "inquiry") {
      return (
        <Paper key={event.id} radius="lg" p="md" className="game-inquiry-event">
          <Text size="xs" c="blue.3" className="monospace-label">cross examination</Text>
          <Text fw={900} mt={4}>{event.asker} → {event.target}</Text>
          <Text size="sm" mt={6}>针对：{event.sourceTitle}</Text>
          <Text size="sm" mt={6}>问：“{event.question}”</Text>
          <Text size="sm" c="dimmed" mt={6}>答：“{event.answer}”</Text>
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
          <AgentCastingPanel
            roles={ROLE_OPTIONS}
            selectedPlayerRoleId={selectedRole}
            onPlayerRoleChange={setSelectedRole}
          />
          <Button
            radius="xl"
            disabled={!selectedRole}
            onClick={confirmRoleSelection}
          >
            {selectedRole ? "确认阵容并进入剧本" : "请先在圆桌中选择自己扮演的角色"}
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
          {introPlayer && <Button onClick={completeIntro}>{introPlayer.id === "user" ? "发言" : "下一位"}</Button>}
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
              <Text fw={700}>选择嫌疑人</Text>
              <Radio.Group value={voteSuspect} onChange={setVoteSuspect}>
                <Box className="game-suspect-grid" mt="xs">
                  {GAME_PLAYERS.filter((player) => !player.agent && player.id !== "user").map((player) => (
                    <Paper
                      key={player.id}
                      component="label"
                      radius="lg"
                      p="sm"
                      className={voteSuspect === player.id ? "game-suspect-option is-selected" : "game-suspect-option"}
                    >
                      <Group wrap="nowrap">
                        {characterPortraits[player.role] ? (
                          <Avatar src={characterPortraits[player.role]} size={40} radius="xl" imageProps={{ style: { objectPosition: "top" } }} />
                        ) : (
                          <Avatar color={player.color}>{player.role.slice(0, 1)}</Avatar>
                        )}
                        <Box style={{ flex: 1 }}>
                          <Text fw={900}>{player.role}</Text>
                          <Text size="xs" c="dimmed">{player.name}</Text>
                        </Box>
                        <Radio value={player.id} aria-label={`选择 ${player.role}`} />
                      </Group>
                    </Paper>
                  ))}
                </Box>
              </Radio.Group>
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
        <Stack gap="xs">{events.filter((event) => event.type !== "accusation").map(renderEvent)}</Stack>
      </Stack>
    );
  };

  const renderRightPanel = () => (
    <Tabs value={rightTab} onChange={setRightTab} className="game-right-tabs">
      <Tabs.List grow>
        <Tabs.Tab value="script">剧本</Tabs.Tab><Tabs.Tab value="tasks">任务</Tabs.Tab><Tabs.Tab value="evidence">证物</Tabs.Tab><Tabs.Tab value="chat" className={privateInviteStatus === "未处理" || privateInviteStatus === "稍后处理" ? "game-chat-tab has-pending-invite" : "game-chat-tab"}>聊天 <Badge size="xs">{privateThreads.reduce((sum, item) => sum + item.unread, 0) + (privateInviteStatus === "未处理" || privateInviteStatus === "稍后处理" ? 1 : 0)}</Badge></Tabs.Tab>
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
        <Tabs.Panel value="evidence" pt="md">
          <Stack gap="md">
            <Group justify="space-between">
              <Text fw={900}>我的证物</Text>
              <Badge variant="light">{evidence.length}</Badge>
            </Group>
            <Stack gap="sm">
              {evidence.map((item) => (
                <Paper key={item.id} p="sm" radius="lg" className="game-clue-item">
                  <Group justify="space-between">
                    <Button variant="transparent" p={0} onClick={() => openEvidenceDetail(item)}>
                      {item.name}
                    </Button>
                    <Badge size="xs">{item.visibility}</Badge>
                  </Group>
                  <Text size="sm" c="dimmed" mt={5}>{item.description}</Text>
                  <Text size="xs" mt="sm">获得方式：{item.source}</Text>
                  <Group gap={6} mt="sm">
                    <Button size="compact-xs" variant="light" onClick={() => openEvidenceDetail(item)}>查看详情</Button>
                    <Button
                      size="compact-xs"
                      variant="light"
                      onClick={() => {
                        if (phase.id !== "discussion") {
                          showFeedback("只有在线索交流阶段才能出示证物。");
                          return;
                        }
                        if (!isUserSpeaking) {
                          showFeedback("请先申请发言，轮到你时即可出示证物。");
                          return;
                        }
                        setSelectedEvidenceId(item.id);
                        setDialog("evidence");
                      }}
                    >
                      出示证物
                    </Button>
                  </Group>
                </Paper>
              ))}
            </Stack>

            <Divider />
            <Group justify="space-between">
              <Box>
                <Text fw={900}>已质询线索</Text>
                <Text size="xs" c="dimmed">证据与关键发言的问答记录</Text>
              </Box>
              <Badge color="blue" variant="light">{inquiryRecords.length}</Badge>
            </Group>
            {inquiryRecords.length > 0 ? (
              <Stack gap="sm">
                {inquiryRecords.map((record) => (
                  <Paper key={record.id} p="sm" radius="lg" className="game-inquiry-record">
                    <Group justify="space-between" align="flex-start">
                      <Box>
                        <Badge size="xs" color={record.sourceType === "证据" ? "orange" : "blue"} variant="light">
                          {record.sourceType}
                        </Badge>
                        <Text fw={800} mt={5}>{record.sourceTitle}</Text>
                      </Box>
                      {record.evidence && (
                        <Button size="compact-xs" variant="subtle" onClick={() => openEvidenceDetail(record.evidence!)}>
                          详情
                        </Button>
                      )}
                    </Group>
                    <Text size="xs" c="dimmed" mt="sm">质询对象：{record.targetName}</Text>
                    <Text size="sm" mt={6}>问：{record.question}</Text>
                    <Text size="sm" c="dimmed" mt={6}>答：{record.answer}</Text>
                  </Paper>
                ))}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">尚未对证据或关键发言发起质询。</Text>
            )}
          </Stack>
        </Tabs.Panel>
        <Tabs.Panel value="chat" pt="md">
          <Stack gap="md">
            <Paper p="sm" radius="lg" className="game-private-event">
              <Group justify="space-between" align="flex-start">
                <Box>
                  <Group gap={6}>
                    <Text fw={900}>白鸦 Agent 申请私聊</Text>
                    <Badge
                      size="xs"
                      color={privateInviteStatus === "未处理" || privateInviteStatus === "稍后处理" ? "orange" : privateInviteStatus === "已接受" ? "teal" : "gray"}
                    >
                      {privateInviteStatus}
                    </Badge>
                  </Group>
                  <Text size="sm" c="dimmed" mt={5}>“我发现门禁记录存在一个不适合公开讨论的时间矛盾。”</Text>
                </Box>
              </Group>
              {(privateInviteStatus === "未处理" || privateInviteStatus === "稍后处理") && (
                <Group gap={6} mt="sm">
                  <Button size="compact-xs" onClick={() => { setPrivateInviteStatus("已接受"); acceptPrivateInvite("crow"); }}>允许</Button>
                  <Button size="compact-xs" variant="light" onClick={() => setPrivateInviteStatus("稍后处理")}>稍后</Button>
                  <Button size="compact-xs" variant="subtle" color="red" onClick={() => setPrivateInviteStatus("已拒绝")}>拒绝</Button>
                </Group>
              )}
            </Paper>

            <Box>
              <Group
                justify="space-between"
                mb={chatHistoryOpen ? "xs" : 0}
                className="game-chat-history-toggle"
                onClick={() => setChatHistoryOpen((value) => !value)}
              >
                <Group gap="xs">
                  <Text fw={900}>公共聊天与线索记录</Text>
                  <Text size="xs" c="dimmed">{chatHistoryOpen ? "收起" : "展开"}</Text>
                </Group>
                <Badge variant="light">{events.filter((event) => ["speech", "evidence", "accusation", "inquiry"].includes(event.type)).length}</Badge>
              </Group>
              {chatHistoryOpen && (
                <Stack gap="xs">
                  {events.filter((event) => ["speech", "evidence", "accusation", "inquiry"].includes(event.type)).map((event) => (
                    <Paper key={`chat-${event.id}`} p="sm" radius="lg" className="game-chat-history-item">
                      {event.type === "speech" && <><Text fw={800}>{event.speaker}</Text><Text size="sm" c="dimmed">{event.text}</Text></>}
                      {event.type === "evidence" && <><Text fw={800}>{event.speaker} 出示证据：{event.evidence.name}</Text><Text size="sm" c="dimmed">{event.reason || event.evidence.description}</Text></>}
                      {event.type === "accusation" && <><Text fw={800}>怀疑记录</Text><Text size="sm" c="dimmed">{event.actor} 将“{event.sourceTitle}”指向 {event.target}{event.reason ? `：${event.reason}` : ""}</Text></>}
                      {event.type === "inquiry" && <><Text fw={800}>质询记录 · {event.asker} → {event.target}</Text><Text size="sm">问：{event.question}</Text><Text size="sm" c="dimmed">答：{event.answer}</Text></>}
                    </Paper>
                  ))}
                </Stack>
              )}
            </Box>

            <Divider />
            <Box>
              <Text fw={900} mb="xs">私聊会话</Text>
              <Group gap="xs" mb="sm">{privateThreads.map((thread) => <Button key={thread.id} size="xs" variant={thread.id === activeThreadId ? "filled" : "light"} onClick={() => { setActiveThreadId(thread.id); setPrivateThreads((items) => items.map((item) => item.id === thread.id ? { ...item, unread: 0 } : item)); }}>{thread.name}{thread.unread > 0 && ` (${thread.unread})`}</Button>)}</Group>
              {activeThread ? <Stack gap="sm"><Text fw={900}>{activeThread.name}</Text><Stack gap="xs">{activeThread.messages.map((text, index) => <Paper key={index} p="sm" radius="lg" className="game-private-chat"><Text size="sm">{text}</Text></Paper>)}</Stack><TextInput value={privateMessage} onChange={(event) => setPrivateMessage(event.currentTarget.value)} placeholder="输入私聊内容…" rightSection={<ActionIcon onClick={sendPrivateMessage}><IconSend size={15} /></ActionIcon>} /></Stack> : <Text c="dimmed">暂无私聊会话。</Text>}
            </Box>
          </Stack>
        </Tabs.Panel>
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
                <Box className="game-dm-anchor">
                  <Paper className="game-dm-header-card" radius="lg" px="sm" py={6}>
                    <Group gap="xs" wrap="nowrap">
                      <Avatar src={dmPortrait} size="sm" color={dm?.color || "red"} imageProps={{ style: { objectPosition: "top" } }}>{dm?.name.slice(0, 1)}</Avatar>
                      <Box className="game-dm-header-copy">
                        <Group gap={5}>
                          <Text size="xs" fw={900}>DM · {dm?.role}</Text>
                          <Badge size="xs" color="red" variant="light">AI</Badge>
                        </Group>
                        <Text size="xs" c="dimmed">{dm?.name} · 主持中</Text>
                        {feedback && <Text size="xs" className="game-dm-progress">{feedback}</Text>}
                      </Box>
                    </Group>
                  </Paper>
                </Box>
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
                          <Box className="game-avatar-wrap">{characterPortraits[player.role] ? <Avatar src={characterPortraits[player.role]} size={40} radius="xl" imageProps={{ style: { objectPosition: "top" } }} /> : <Avatar color={player.color}>{player.role.slice(0, 1)}</Avatar>}<Box className="game-online-dot" /></Box>
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
              {selectedPlayer && selectedPlayer.id !== "dm" && <Paper p="sm" radius="lg" className="game-player-actions"><Group justify="space-between"><Text fw={800}>{selectedPlayer.role} · 快捷操作</Text><Badge color={selectedPlayer.agent ? "blue" : "orange"} variant="light">{selectedPlayer.agent ? "AI 玩家" : "真人玩家"}</Badge></Group><Group gap={5} mt="sm"><Button size="xs" variant="light" onClick={() => showFeedback(`${selectedPlayer.role} 的公开身份：${selectedPlayer.publicIdentity}`)}>公开信息</Button>{selectedPlayer.id !== "user" && <Button size="xs" variant="light" onClick={() => { setTargetId(selectedPlayer.id); setDialog("private"); }}>发起私聊</Button>}{selectedPlayer.agent && <Button size="xs" variant="light" disabled={!isUserSpeaking} onClick={() => { setTargetId(selectedPlayer.id); setDialog("force"); }}>指定回答</Button>}</Group></Paper>}
            </aside>

            <section className="game-core-panel"><ScrollArea className="game-core-scroll" offsetScrollbars>{renderStage()}</ScrollArea></section>
            <aside className="game-side-panel game-personal-panel">{renderRightPanel()}</aside>
          </main>

          <footer className="game-workspace__footer game-workspace__footer--actions">{footerActions()}</footer>
        </Paper>
      </Box>

      <Modal opened={dialog === "force"} onClose={() => setDialog(null)} title="指定 Agent 回答" centered><Stack><Select label="选择 Agent" value={targetId} onChange={(value) => setTargetId(value || "crow")} data={agents.map((agent) => ({ value: agent.id, label: `${agent.name} · ${agent.role}` }))} /><Textarea label="需要回答的问题" value={question} onChange={(event) => setQuestion(event.currentTarget.value)} minRows={4} /><Button onClick={confirmForcedAnswer}>确认指定</Button></Stack></Modal>
      <Modal opened={dialog === "evidence"} onClose={() => setDialog(null)} title="出示证物" centered><Stack><Select label="选择证物" value={selectedEvidenceId} onChange={(value) => setSelectedEvidenceId(value || evidence[0]?.id)} data={evidence.map((item) => ({ value: item.id, label: item.name }))} /><Textarea label="出示理由" placeholder="说明这项证据支持或反驳了什么观点" value={evidenceReason} onChange={(event) => setEvidenceReason(event.currentTarget.value)} minRows={3} /><Radio.Group label="公开范围" value={evidenceVisibility} onChange={setEvidenceVisibility}><Stack mt="xs"><Radio value="所有人" label="公开给所有人" /><Radio value="指定角色" label="只分享给指定角色" /></Stack></Radio.Group>{evidenceVisibility === "指定角色" && <Select label="指定角色" value={targetId} onChange={(value) => setTargetId(value || "chen")} data={GAME_PLAYERS.filter((player) => player.id !== "user").map((player) => ({ value: player.id, label: player.name }))} />}<Button onClick={showEvidence}>确认出示</Button></Stack></Modal>
      <Modal
        opened={dialog === "evidence-detail"}
        onClose={() => setDialog(null)}
        title="证据详情"
        centered
        size="lg"
      >
        {selectedDetailEvidence && (
          <Stack gap="md">
            <Group justify="space-between">
              <Box>
                <Text className="monospace-label" size="xs" c="orange.3">evidence archive</Text>
                <Title order={2}>{selectedDetailEvidence.name}</Title>
              </Box>
              <Badge color="orange" variant="light">{selectedDetailEvidence.visibility}</Badge>
            </Group>
            <Paper radius="lg" p="lg" className="game-evidence-detail">
              <Text lh={1.8}>{selectedDetailEvidence.description}</Text>
              <Divider my="md" />
              <Stack gap={6}>
                <Group justify="space-between"><Text c="dimmed">发现地点</Text><Text fw={700}>{selectedDetailEvidence.location}</Text></Group>
                <Group justify="space-between"><Text c="dimmed">记录时间</Text><Text fw={700}>{selectedDetailEvidence.time}</Text></Group>
                <Group justify="space-between"><Text c="dimmed">获得方式</Text><Text fw={700}>{selectedDetailEvidence.source}</Text></Group>
              </Stack>
            </Paper>
          </Stack>
        )}
      </Modal>
      <Modal
        opened={dialog === "discussion-detail"}
        onClose={() => setDialog(null)}
        title="公共讨论详情"
        centered
        size="xl"
      >
        {selectedDiscussionSource && (
          <Stack gap="lg">
            <Group justify="space-between" align="flex-start">
              <Group gap="sm">
                <Avatar size="lg" color={selectedDiscussionSpeaker?.color || (selectedDiscussionSource.type === "evidence" ? "orange" : selectedDiscussionSource.tone)}>
                  {(selectedDiscussionSpeaker?.role || selectedDiscussionSource.speaker).slice(0, 1)}
                </Avatar>
                <Box>
                  <Text className="monospace-label" size="xs" c="dimmed">
                    {selectedDiscussionSource.type === "evidence" ? "evidence statement" : "public statement"}
                  </Text>
                  <Title order={3}>{selectedDiscussionSource.speaker}</Title>
                  {selectedDiscussionSpeaker && <Text size="sm" c="dimmed">{selectedDiscussionSpeaker.role} · {selectedDiscussionSpeaker.publicIdentity}</Text>}
                </Box>
              </Group>
              {selectedDiscussionSuspect && (
                <Paper p="sm" radius="lg" className="game-discussion-suspect">
                  <Text size="xs" c="dimmed">当前怀疑对象</Text>
                  <Group gap="xs" mt={5}>
                    <Avatar size="sm" color={selectedDiscussionSuspect.color}>{selectedDiscussionSuspect.role.slice(0, 1)}</Avatar>
                    <Box>
                      <Text size="sm" fw={800}>{selectedDiscussionSuspect.role}</Text>
                      <Text size="xs" c="dimmed">{selectedDiscussionSuspect.name}</Text>
                    </Box>
                  </Group>
                </Paper>
              )}
            </Group>

            <Paper p="lg" radius="lg" className="game-discussion-copy">
              <Text lh={1.85}>
                {selectedDiscussionSource.type === "speech"
                  ? selectedDiscussionSource.text
                  : selectedDiscussionSource.reason || selectedDiscussionSource.evidence.description}
              </Text>
            </Paper>

            {selectedDiscussionEvidence && (
              <Paper p="md" radius="lg" className="game-discussion-evidence">
                <Box className="game-discussion-evidence-image">
                  <Text className="monospace-label" size="xs" c="dimmed">evidence image</Text>
                  <Text c="dimmed">证据图片占位</Text>
                </Box>
                <Box>
                  <Group justify="space-between">
                    <Title order={4}>{selectedDiscussionEvidence.name}</Title>
                    <Badge color="orange" variant="light">{selectedDiscussionEvidence.visibility}</Badge>
                  </Group>
                  <Text size="sm" c="dimmed" mt="sm" lh={1.7}>{selectedDiscussionEvidence.description}</Text>
                  <Group gap="lg" mt="sm">
                    <Text size="xs">地点：{selectedDiscussionEvidence.location}</Text>
                    <Text size="xs">时间：{selectedDiscussionEvidence.time}</Text>
                  </Group>
                </Box>
              </Paper>
            )}

            <Group justify="flex-end">
              <Button variant="light" onClick={() => openPointDialog(selectedDiscussionSource.id)}>指向嫌疑人</Button>
              <Button color="blue" onClick={() => openInquiryDialog(selectedDiscussionSource.id)}>
                {selectedDiscussionSource.type === "evidence" ? "针对此证据质询" : "针对此发言质询"}
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
      <Modal opened={dialog === "point"} onClose={() => setDialog(null)} title="将线索指向嫌疑人" centered>
        <Stack>
          <Text size="sm" c="dimmed">
            来源：{discussionSource(selectedDiscussionEventId) ? discussionSourceTitle(discussionSource(selectedDiscussionEventId)!) : "未选择"}
          </Text>
          <Select
            label="你怀疑谁"
            value={pointTargetId}
            onChange={(value) => setPointTargetId(value || "chen")}
            data={GAME_PLAYERS.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({
              value: player.id,
              label: `${player.role} · ${player.name}`,
            }))}
          />
          <Textarea
            label="怀疑理由（可选）"
            value={pointReason}
            onChange={(event) => setPointReason(event.currentTarget.value)}
            minRows={3}
          />
          <Button onClick={confirmPoint}>确认指向</Button>
        </Stack>
      </Modal>
      <Modal opened={dialog === "inquiry"} onClose={() => setDialog(null)} title="针对线索发起质询" centered size="lg">
        <Stack>
          <Text size="sm" c="dimmed">
            质询来源：{discussionSource(selectedDiscussionEventId) ? discussionSourceTitle(discussionSource(selectedDiscussionEventId)!) : "未选择"}
          </Text>
          <Select
            label="质询对象"
            value={inquiryTargetId}
            onChange={(value) => setInquiryTargetId(value || "crow")}
            data={GAME_PLAYERS.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({
              value: player.id,
              label: `${player.role} · ${player.name}${player.agent ? " · AI" : " · 真人"}`,
            }))}
          />
          <Textarea
            label="质询问题"
            placeholder="说明这项证据或发言与你的疑问之间有什么关系"
            value={inquiryQuestion}
            onChange={(event) => setInquiryQuestion(event.currentTarget.value)}
            minRows={4}
          />
          <Button onClick={confirmInquiry}>发起质询并保存记录</Button>
        </Stack>
      </Modal>
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
      {introSpotlight && (
        <Box
          className="game-intro-spotlight"
          role="button"
          tabIndex={0}
          aria-label="关闭角色自我介绍"
          onClick={() => setIntroSpotlight(null)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") setIntroSpotlight(null);
          }}
        >
          <Box className="game-intro-portrait" aria-hidden="true">
            {characterPortraits[introSpotlight.role] ? (
              <img
                src={characterPortraits[introSpotlight.role]}
                alt={introSpotlight.role}
                style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", objectPosition: "top" }}
              />
            ) : (
              <>
                <Text className="monospace-label" size="xs" c="dimmed">character portrait</Text>
                <Text c="dimmed">角色立绘占位</Text>
              </>
            )}
          </Box>
          <Paper className="game-intro-speech" radius="xl" p="lg">
            <Group gap="sm">
              {characterPortraits[introSpotlight.role] ? (
                <Avatar src={characterPortraits[introSpotlight.role]} size={48} radius="xl" imageProps={{ style: { objectPosition: "top" } }} />
              ) : (
                <Avatar color={introSpotlight.color}>{introSpotlight.role.slice(0, 1)}</Avatar>
              )}
              <Box>
                <Title order={3}>{introSpotlight.role}</Title>
                <Text size="sm" c="dimmed">{introSpotlight.name} · {introSpotlight.agent ? "AI 玩家" : "真人玩家"}</Text>
              </Box>
            </Group>
            <Text fz="lg" lh={1.8} mt="md">“{INTRO_LINES[introSpotlight.id]}”</Text>
            <Text size="xs" c="dimmed" ta="center" mt="md">点击任意位置继续</Text>
          </Paper>
        </Box>
      )}
    </StudioShell>
  );
}

export { GamePage };
