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
  PRIVATE_THREADS,
  ROLE_OPTIONS,
  SEARCH_EVIDENCE,
} from "./gameMockData";
import { backendEvidenceToGameEvidence } from "../api/adapters";
import {
  getScript,
  createEvidence,
  createGameSession,
  forceGamePhase,
  getGamePhase,
  getEvidences,
  listPersonas,
  presentEvidence,
  saveConversation,
  submitGameVote,
  type AgentPersona,
  type BackendScript,
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
  "black-archive": "黑匣档案馆",
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
  sourceType: "璇佹嵁" | "鍏抽敭鍙戣█";
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

const initialEvents: PublicEvent[] = [];

function formatTime(totalSeconds: number) {
  return `${String(Math.floor(totalSeconds / 60)).padStart(2, "0")}:${String(totalSeconds % 60).padStart(2, "0")}`;
}

function summarizeText(text: string, maxLength = 120) {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (!normalized) return "";
  return normalized.length > maxLength ? `${normalized.slice(0, maxLength).trim()}...` : normalized;
}

function buildScriptReadingContent(script: BackendScript | null) {
  if (!script) return "";

  const sections = [
    script.description,
    script.globalStory,
    script.characters?.length
      ? `角色信息：${script.characters
          .map((character) => `${character.name}：${character.bio || character.context || character.personality || "暂无描述"}`)
          .join("\n")}`
      : "",
    script.evidences?.length
      ? `关键证据：${script.evidences
          .map((item) => `${item.name}：${item.description || "暂无描述"}`)
          .join("\n")}`
      : "",
  ].filter(Boolean);

  return sections.join("\n\n");
}

function GamePage() {
  const navigate = useNavigate();
  const { id = "iron-avenue" } = useParams();
  const fallbackScriptTitle = scriptMap[id] || "鏈煡鍓ф湰";
  const gameMode = id === "black-archive" ? "鍗曚汉娓告垙" : "鐪熶汉缁勯槦";
  const { ref: fullscreenRef, toggle: toggleFullscreen, fullscreen } = useFullscreen();

  const [phaseIndex, setPhaseIndex] = React.useState(0);
  const [scriptData, setScriptData] = React.useState<BackendScript | null>(null);
  const [personas, setPersonas] = React.useState<AgentPersona[]>([]);
  const [sessionId, setSessionId] = React.useState(
    () => window.localStorage.getItem(`game-session:${id}`) || "",
  );
  const scriptTitle = scriptData?.title || fallbackScriptTitle;
  const phase = GAME_PHASES[phaseIndex];
  const [selectedRole, setSelectedRole] = React.useState("");
  const [roleConfirmed, setRoleConfirmed] = React.useState(false);
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
  const [introduced, setIntroduced] = React.useState<string[]>([]);
  const [searchesLeft, setSearchesLeft] = React.useState(2);
  const [evidence, setEvidence] = React.useState<Evidence[]>([]);
  const [newEvidence, setNewEvidence] = React.useState<Evidence | null>(null);
  const [queue, setQueue] = React.useState<string[]>(["chen", "crow"]);
  const [currentSpeaker, setCurrentSpeaker] = React.useState<string | null>("chen");
  const [forcedAnswer, setForcedAnswer] = React.useState<{ asker: string; agentId: string; question: string } | null>(null);
  const [events, setEvents] = React.useState<PublicEvent[]>([]);
  const [rightTab, setRightTab] = React.useState<string | null>("script");
  const [dialog, setDialog] = React.useState<DialogType>(null);
  const [selectedPlayerId, setSelectedPlayerId] = React.useState<string | null>(null);
  const [targetId, setTargetId] = React.useState("crow");
  const [question, setQuestion] = React.useState("");
  const [selectedEvidenceId, setSelectedEvidenceId] = React.useState("");
  const [evidenceVisibility, setEvidenceVisibility] = React.useState("鎵€鏈変汉");
  const [evidenceReason, setEvidenceReason] = React.useState("");
  const [privateThreads, setPrivateThreads] = React.useState(PRIVATE_THREADS);
  const [activeThreadId, setActiveThreadId] = React.useState(PRIVATE_THREADS[0].id);
  const [privateMessage, setPrivateMessage] = React.useState("");
  const [publicMessage, setPublicMessage] = React.useState("");
  const [feedback, setFeedback] = React.useState("娆㈣繋杩涘叆娓告垙锛岃鐐瑰嚮鍦嗘甯綅閫夋嫨浣犲枩娆㈢殑瑙掕壊");
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
  const [privateInviteStatus, setPrivateInviteStatus] = React.useState<string>("未处理");
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
        showFeedback(`鍚庣璇佺墿鍔犺浇澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
        showFeedback(`后端证物加载失败：${error instanceof Error ? error.message : String(error)}`);
  }, [id, sessionId]);

  React.useEffect(() => {
    Promise.all([getScript(id), listPersonas()])
      .then(([script, personaList]) => {
        setScriptData(script);
        setPersonas(personaList);
      })
      .catch((error) => {
        showFeedback(`鍚庣鍓ф湰鎴?Agent 浜鸿鍔犺浇澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
        showFeedback(`后端剧本或 Agent 人设加载失败：${error instanceof Error ? error.message : String(error)}`);
  }, [id]);

  const playerById = (playerId: string | null) => GAME_PLAYERS.find((item) => item.id === playerId);
  const current = playerById(currentSpeaker);
  const isUserSpeaking = currentSpeaker === "user";
  const userQueued = queue.includes("user");
  const currentIntroId = ["user", "chen", "crow", "su", "echo"].find((playerId) => !introduced.includes(playerId));
  const selectedPlayer = playerById(selectedPlayerId);
  const activeThread = privateThreads.find((item) => item.id === activeThreadId);
  const agents = GAME_PLAYERS.filter((player) => player.agent && player.id !== "dm");
  const dm = playerById("dm");
  const scriptReadingContent = React.useMemo(() => buildScriptReadingContent(scriptData), [scriptData]);
  const scriptEvidenceSeed = React.useMemo(
    () => (scriptData?.evidences || []).map((item) => ({
      id: String(item.id || `script-evidence-${item.name}`),
      name: String(item.name || "未命名证据"),
      description: String(item.description || "鏆傛棤鎻忚堪"),
      location: String(item.category || "鍓ф湰璧勬枡"),
      time: String(item.initialState || "鍓ф湰棰勭疆"),
      source: String(item.importance || "鍚庣鍓ф湰"),
      visibility: "仅自己" as Evidence["visibility"],
      icon: String(item.category || "file"),
    })),
    [scriptData],
  );
  const introLines = React.useMemo(() => {
    const personaByKey = new Map(personas.map((item) => [item.key, item]));
    const characterQueue = scriptData?.characters || [];
    return {
      user: summarizeText(
        `${characterQueue[0]?.name || "玩家"}：${characterQueue[0]?.bio || characterQueue[0]?.context || scriptData?.description || ""}`,
        140,
      ),
      chen: summarizeText(
        `${characterQueue[1]?.name || "角色二"}：${characterQueue[1]?.bio || characterQueue[1]?.context || scriptData?.globalStory || ""}`,
        140,
      ),
      crow: summarizeText(
        `${personaByKey.get("white-crow")?.name || "白鸦"}：${personaByKey.get("white-crow")?.style || personaByKey.get("white-crow")?.vibe || ""}`,
        140,
      ),
      su: summarizeText(
        `${characterQueue[2]?.name || "角色三"}：${characterQueue[2]?.bio || characterQueue[2]?.context || scriptData?.description || ""}`,
        140,
      ),
      echo: summarizeText(
        `${personaByKey.get("echo")?.name || "回声"}：${personaByKey.get("echo")?.style || personaByKey.get("echo")?.vibe || ""}`,
        140,
      ),
    } as Record<string, string>;
  }, [personas, scriptData]);
  const sceneCard = React.useMemo(
    () => ({
      badge: "DM 鍦烘櫙",
      title: scriptData?.title || fallbackScriptTitle,
      description: summarizeText(scriptData?.globalStory || scriptData?.description || "", 160),
    }),
    [fallbackScriptTitle, scriptData],
  );

  React.useEffect(() => {
    try {
      window.localStorage.setItem(highlightStorageKey, JSON.stringify(scriptHighlights));
    } catch {
      // 娴忚鍣ㄧ鐢ㄦ湰鍦板瓨鍌ㄦ椂浠嶅厑璁哥户缁父鎴忥紝鍙槸涓嶈法鍒锋柊淇濆瓨銆?    }
    }
  }, [highlightStorageKey, scriptHighlights]);

  React.useEffect(() => {
    if (!scriptData || events.length > 0) return;

    const seededEvidence = scriptEvidenceSeed[0] || INITIAL_EVIDENCE[0];
    const nextEvents: PublicEvent[] = [
      {
        id: 1,
        type: "system",
        title: "阶段开始",
        text: summarizeText(scriptData.description || scriptData.globalStory || "后端剧本已加载，公共讨论已开启。", 140),
      },
      {
        id: 2,
        type: "speech",
        speaker: GAME_PLAYERS.find((item) => item.id === "chen")?.name || "闄堝ⅷ",
        text: introLines.chen || "后端未提供开场介绍。",
        tone: "teal",
        suspectId: "echo",
      },
      {
        id: 3,
        type: "speech",
        speaker: `${personas.find((item) => item.key === "white-crow")?.name || "鐧介甫"} Agent`,
        text: introLines.crow || "后端未提供 Agent 开场介绍。",
        tone: "blue",
        suspectId: "echo",
        evidenceId: seededEvidence?.id,
      },
    ];
    if (seededEvidence) {
      nextEvents.push({
        id: 4,
        type: "evidence",
        speaker: `${personas.find((item) => item.key === "white-crow")?.name || "鐧介甫"} Agent`,
        evidence: seededEvidence,
        reason: summarizeText(seededEvidence.description, 72),
      });
    }
    setEvents(nextEvents);
  }, [events.length, introLines, personas, scriptData, scriptEvidenceSeed]);

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
        const session = await createGameSession(id, `鍓ф湰娓告垙锛?{scriptTitle}`);
        activeSessionId = session.sessionId;
        setSessionId(activeSessionId);
        window.localStorage.setItem(`game-session:${id}`, activeSessionId);
      }
      setRoleConfirmed(true);
      setPhaseIndex(1);
      showFeedback(`角色已确认，后端游戏会话 ${activeSessionId} 可用。`);
    } catch (error) {
      showFeedback(`鏃犳硶纭瑙掕壊锛氬悗绔父鎴忎細璇濆垱寤烘垨鎭㈠澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
      showFeedback(`无法确认角色：${error instanceof Error ? error.message : String(error)}`);
  };

  const backendPhaseForIndex = (index: number) => {
    if (index <= 2) return "intro";
    if (index <= 4) return "investigation";
    return "voting";
  };

  const goToPhase = async (index: number) => {
    if (phase.id === "role-selection" && index > 0 && !roleConfirmed) {
      showFeedback("请先确认角色后再进入后续阶段。");
      return;
    }
    if (index === 0 && roleConfirmed) {
      showFeedback("角色已确认，不能再次进入选角阶段。");
      return;
    }
    if (index > phaseIndex + 1) {
      showFeedback("请先完成当前阶段，不能跳过流程。");
      return;
    }
    if (!sessionId) {
      showFeedback("无法切换阶段：尚未创建后端游戏会话。");
      return;
    }
    try {
      await forceGamePhase(sessionId, backendPhaseForIndex(index));
    } catch (error) {
      showFeedback(`鍚庣闃舵鍒囨崲澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
      showFeedback(`后端阶段切换失败：${error instanceof Error ? error.message : String(error)}`);
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
    if (phase.id === "script-reading" && !readingDone) return showFeedback("请先阅读后端剧本内容并确认完成。");
    if (phase.id === "intro" && introduced.length < 5) return showFeedback("仍有角色尚未完成自我介绍。");
    if (phase.id === "search" && searchesLeft > 0) return showFeedback("请先用完本阶段的搜证次数。");
    if (phaseIndex < GAME_PHASES.length - 1) goToPhase(phaseIndex + 1);
  };

  const joinQueue = () => {
    if (phase.id === "vote") return showFeedback("投票阶段已停止新的发言申请。");
    if (forcedAnswer) return showFeedback("当前为强制回答状态，其他角色暂时不可插队。");
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
        text: `关于“${forcedAnswer.question}”，我认为值班表压痕说明修改发生在旧终端，而钥匙持有者需要重点排查。`,
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
    addEvent({ type: "speech", speaker: introPlayer.name, text: introLines[currentIntroId], tone: introPlayer.color || "gray" });
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
  };

  const confirmForcedAnswer = () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能指定 Agent 回答。");
    const agent = playerById(targetId);
    if (!question.trim() || !agent) return showFeedback("请选择 Agent 并填写问题。");
    setForcedAnswer({ asker: "鏋楁檽闈?, agentId: targetId, question });
    setQueue((items) => [targetId, ...items.filter((item) => item !== targetId && item !== currentSpeaker)]);
    addEvent({ type: "forced", asker: "鏋楁檽闈?, agent: agent.name, question });
    setDialog(null);
    setQuestion("");
    showFeedback(`${agent.name} 宸茶鎸囧畾涓轰笅涓€浣嶅彂瑷€鑰咃紝鍏朵粬瑙掕壊涓嶅彲鎻掗槦銆俙);
    showFeedback(`${agent.name} 已被指定为下一位发言者，其他角色不可插队。`);

  const showEvidence = async () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能出示证物。");
    if (!sessionId) return showFeedback("出示证物失败：尚未创建后端游戏会话。");
    const item = evidence.find((entry) => entry.id === selectedEvidenceId);
    if (!item) return;
    const reason = evidenceReason.trim();
    try {
      await presentEvidence(
        item.id,
        evidenceVisibility === "鎸囧畾瑙掕壊" ? targetId : "all",
        "player",
        reason,
        evidenceVisibility,
      );
    } catch (error) {
      showFeedback(`鍚庣鍑虹ず璇佺墿澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
      showFeedback(`后端出示证物失败：${error instanceof Error ? error.message : String(error)}`);
    }
    setEvidence((items) => items.map((entry) => entry.id === item.id ? { ...entry, visibility: evidenceVisibility as Evidence["visibility"] } : entry));
    addEvent({
      type: "evidence",
      speaker: "鏋楁檽闈?,
      evidence: { ...item, visibility: evidenceVisibility as Evidence["visibility"] },
      reason: evidenceReason.trim() || undefined,
    });
    setDialog(null);
    setEvidenceReason("");
    showFeedback(`鍚庣宸茶褰曞嚭绀衡€?{item.name}鈥濓紝鍏紑鑼冨洿锛?{evidenceVisibility}銆俙);
    showFeedback(`后端已记录出示“${item.name}”，公开范围：${evidenceVisibility}。`);

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
        permission: "涓诲姩鍙戣█" as const,
        messages: ["绉佽亰宸插缓绔嬨€傚叕鍏辫璁轰粛鍦ㄧ户缁紝鏈細璇濆唴瀹逛粎鍙屾柟鍙銆?],
        messages: ["私聊已建立。公共讨论仍在继续，本会话内容仅双方可见。"],
      setPrivateThreads((items) => [...items, thread]);
      setActiveThreadId(thread.id);
    } else {
      setActiveThreadId(existing.id);
    }
    setRightTab("chat");
    setDialog(null);
    showFeedback(`宸蹭笌 ${player.name} 寤虹珛绉佽亰锛屽叕鍏卞彂瑷€闃熷垪鏈彈褰卞搷銆俙);
    showFeedback(`已与 ${player.name} 建立私聊，公共发言队列未受影响。`);

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
      addEvent({ type: "speech", speaker: "鏋楁檽闈?, text: content, tone: "orange" });
      setPublicMessage("");
    } catch (error) {
      showFeedback(`鍚庣淇濆瓨鍏紑鍙戣█澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
      showFeedback(`后端保存公开发言失败：${error instanceof Error ? error.message : String(error)}`);
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
        thread.id === activeThread.id ? { ...thread, messages: [...thread.messages, `鎴戯細${content}`] } : thread,
      ));
      setPrivateMessage("");
    } catch (error) {
      showFeedback(`鍚庣淇濆瓨绉佽亰澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
      showFeedback(`后端保存私聊失败：${error instanceof Error ? error.message : String(error)}`);
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
      showFeedback(result.message || "鎺ㄧ悊鎶曠エ宸插啓鍏ュ悗绔€?);
      showFeedback(result.message || "推理投票已写入后端。");
      showFeedback(`鍚庣鎶曠エ澶辫触锛?{error instanceof Error ? error.message : String(error)}`);
      showFeedback(`后端投票失败：${error instanceof Error ? error.message : String(error)}`);
  };

  const playerStatus = (playerId: string) => {
    if (currentSpeaker === playerId) return "姝ｅ湪鍙戣█";
    if (queue.includes(playerId)) return "绛夊緟鍙戣█";
    return "鎬濊€冧腑";
  };

  const captureScriptSelection = (_chapterIndex: number) => {
    const selected = window.getSelection()?.toString().trim() || "";
    setSelectedScriptText(selected);
  };

  const addScriptHighlight = () => {
    if (!selectedScriptText) {
      showFeedback("请先在剧本文本中选中需要高亮的语句。");
      return;
    }
    const duplicate = scriptHighlights.some(
      (item) => item.chapter === 0 && item.text === selectedScriptText,
    );
    if (!duplicate) {
      setScriptHighlights((items) => [
        ...items,
        {
          id: `0-${Date.now()}`,
          chapter: 0,
          text: selectedScriptText,
        },
      ]);
    }
    setSelectedScriptText("");
    window.getSelection()?.removeAllRanges();
    showFeedback("高亮片段已保存。");
  };

  const removeScriptHighlight = (highlightId: string) => {
    setScriptHighlights((items) => items.filter((item) => item.id !== highlightId));
    showFeedback("高亮片段已删除。");
  };

  const discussionSource = (eventId: number | null) => {
    const event = events.find((item) => item.id === eventId);
    if (!event || (event.type !== "speech" && event.type !== "evidence")) return null;
    return event;
  };

  const discussionSourceTitle = (event: Extract<PublicEvent, { type: "speech" | "evidence" }>) =>
    event.type === "evidence" ? event.evidence.name : `${event.speaker} 鐨勫彂瑷€`;

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
      actor: "鏋楁檽闈?,
      target: `${target.role} 路 ${target.name}`,
      sourceTitle: discussionSourceTitle(source),
      reason: pointReason.trim() || undefined,
    });
    setDialog(null);
    showFeedback(`宸插皢鈥?{discussionSourceTitle(source)}鈥濇寚鍚?${target.role}銆俙);
    showFeedback(`已将“${discussionSourceTitle(source)}”指向 ${target.role}。`);

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
      ? `鎴戞鏌ヨ繃鈥?{source.evidence.name}鈥濈殑鏉ユ簮銆傚畠鑳借瘉鏄庢椂闂村拰鍦扮偣瀛樺湪鍏宠仈锛屼絾杩樹笉鑳藉崟鐙瘉鏄庢寔鏈変汉韬唤銆俙
      : `鍏充簬杩欐鍙戣█锛屾垜鐨勫垽鏂槸鍏朵腑鏈変竴澶勬椂闂撮『搴忛渶瑕佸鏍搞€傛垜鎰挎剰鎶婄浉鍏宠鍔ㄨ褰曞叕寮€鍑烘潵鎺ュ彈姣斿銆俙;
    const record: InquiryRecord = {
      id: Date.now(),
      sourceEventId: source.id,
      sourceType: source.type === "evidence" ? "璇佹嵁" : "鍏抽敭鍙戣█",
      sourceTitle,
      evidence: source.type === "evidence" ? source.evidence : undefined,
      targetId: target.id,
      targetName: `${target.role} 路 ${target.name}`,
      question: inquiryQuestion.trim(),
      answer,
    };
    setInquiryRecords((items) => [...items, record]);
    addEvent({
      type: "inquiry",
      asker: "鏋楁檽闈?,
      target: record.targetName,
      sourceTitle,
      question: record.question,
      answer,
    });
    setRightTab("chat");
    setDialog(null);
    setInquiryQuestion("");
    showFeedback(`宸插畬鎴愬 ${target.role} 鐨勮川璇紝璁板綍宸蹭繚瀛樺埌璇佺墿鏍忋€俙);
    showFeedback(`已完成对 ${target.role} 的质询，记录已保存到证物栏。`);

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
<<<<<<< HEAD
            {(() => {
              const speakerPlayer = GAME_PLAYERS.find((p) => p.name === event.speaker || `${p.name} Agent` === event.speaker);
              const speakerPortrait = speakerPlayer ? characterPortraits[speakerPlayer.role] : undefined;
              return speakerPortrait ? (
                <Avatar src={speakerPortrait} size="sm" imageProps={{ style: { objectPosition: "top" } }} />
              ) : (
                <Avatar size="sm" color={event.tone}>{event.speaker.slice(0, 1)}</Avatar>
              );
            })()}
            <Box><Text size="sm" fw={800} c={`${event.tone}.3`}>{event.speaker}</Text><Text size="sm" c="gray.3">{event.text}</Text></Box>
=======
            <Avatar size="sm" color={event.tone}>{event.speaker.slice(0, 1)}</Avatar>
            <Box style={{ flex: 1 }}>
              <Text size="sm" fw={800} c={`${event.tone}.3`}>{event.speaker}</Text>
              <Text size="sm" c="gray.3" lh={1.65}>{event.text}</Text>
              {phase.id === "discussion" && <Text size="xs" c="dimmed" mt={6}>鐐瑰嚮鏌ョ湅鍙戣█璇︽儏</Text>}
            </Box>
>>>>>>> 45115ae951f37312eb6d6648439e220503b86691
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
          {event.reason && <Text size="sm" mt={6}>鍑虹ず鐞嗙敱锛歿event.reason}</Text>}
          <Group gap="lg" mt="sm"><Text size="xs">鍑虹ず鑰咃細{event.speaker}</Text><Text size="xs">鍦扮偣锛歿event.evidence.location}</Text><Text size="xs">鏃堕棿锛歿event.evidence.time}</Text></Group>
          {phase.id === "discussion" && <Text size="xs" c="dimmed" mt="sm">鐐瑰嚮鏌ョ湅璇佹嵁涓庡彂瑷€璇︽儏</Text>}
        </Paper>
      );
    }
    if (event.type === "forced") {
      return (
        <Paper key={event.id} radius="xl" p="md" className="game-forced-event">
          <Text fw={900}>鎸囧畾鍥炵瓟锛歿event.asker} 鈫?{event.agent}</Text>
          <Text size="sm" mt={5}>鈥渰event.question}鈥?/Text>
          <Text size="xs" c="red.3" mt={6}>琚寚瀹?Agent 蹇呴』鎴愪负涓嬩竴浣嶅彂瑷€鑰咃紝鍏朵粬瑙掕壊涓嶅彲鎻掗槦銆?/Text>
        </Paper>
      );
    }
    if (event.type === "accusation") {
      return (
        <Paper key={event.id} radius="lg" p="sm" className="game-accusation-event">
          <Text fw={900}>{event.actor} 灏嗏€渰event.sourceTitle}鈥濇寚鍚?{event.target}</Text>
          {event.reason && <Text size="sm" c="dimmed" mt={5}>鐞嗙敱锛歿event.reason}</Text>}
        </Paper>
      );
    }
    if (event.type === "inquiry") {
      return (
        <Paper key={event.id} radius="lg" p="md" className="game-inquiry-event">
          <Text size="xs" c="blue.3" className="monospace-label">cross examination</Text>
          <Text fw={900} mt={4}>{event.asker} 鈫?{event.target}</Text>
          <Text size="sm" mt={6}>閽堝锛歿event.sourceTitle}</Text>
          <Text size="sm" mt={6}>闂細鈥渰event.question}鈥?/Text>
          <Text size="sm" c="dimmed" mt={6}>绛旓細鈥渰event.answer}鈥?/Text>
        </Paper>
      );
    }
    return (
      <Paper key={event.id} radius="lg" p="sm" className={event.type === "private" ? "game-private-event" : "game-system-event"}>
        <Text size="sm" fw={800}>{event.type === "private" ? `绉佽亰鐢宠 路 ${event.agent}` : event.title}</Text>
        <Text size="sm" c="dimmed">{event.text}</Text>
      </Paper>
    );
  };

  const renderStage = () => {
    if (phase.id === "role-selection") {
      return (
        <Stack gap="md">
          <Group justify="space-between"><Box><Title order={3}>閫夋嫨浣犵殑瑙掕壊</Title><Text c="dimmed">鏌ョ湅鍏紑韬唤涓庢爣绛撅紝纭鍚庤繘鍏ュ墽鏈槄璇汇€?/Text></Box><Badge>{roleConfirmed ? "宸茬‘璁? : "寰呯‘璁?}</Badge></Group>
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
            {selectedRole ? "纭闃靛骞惰繘鍏ュ墽鏈? : "璇峰厛鍦ㄥ渾妗屼腑閫夋嫨鑷繁鎵紨鐨勮鑹?}
          </Button>
        </Stack>
      );
    }
    if (phase.id === "script-reading") {
      return (
        <Stack gap="md">
          <Paper radius="xl" p="xl" className="game-reading-card">
            <Text className="monospace-label" size="xs" c="red.3">backend script briefing</Text>
            <Title order={2} mt="sm">{scriptTitle}</Title>
            <Text
              fz="lg"
              lh={1.9}
              mt="lg"
              className="game-script-selectable"
              onMouseUp={() => captureScriptSelection(0)}
            >
              {renderHighlightedScript(scriptReadingContent || "后端暂未返回剧本正文。", 0)}
            </Text>
            <Group justify="space-between" mt="xl">
              <Text size="sm" c="dimmed">
                閫変腑鍓ф湰涓殑鍏蜂綋璇彞鍚庯紝鍙繚瀛樹负涓汉楂樹寒銆?              </Text>
              <Button
                size="xs"
                variant="light"
                color="yellow"
                leftSection={<IconHighlight size={15} />}
                disabled={!selectedScriptText}
                onClick={addScriptHighlight}
              >
                楂樹寒閫変腑鏂囨
              </Button>
            </Group>
          </Paper>
          <Group justify="space-between">
            <Text size="sm" c="dimmed">当前阶段直接展示完整后端剧本内容，不再按章节翻页。</Text>
            <Button color="teal" leftSection={<IconCheck size={16} />} onClick={() => { setReadingDone(true); showFeedback("已确认阅读完成。"); }}>
              纭闃呰瀹屾垚
            </Button>
          </Group>
        </Stack>
      );
    }
    if (phase.id === "intro") {
      const introPlayer = playerById(currentIntroId || null);
      return (
        <Stack gap="md">
          <Paper radius="xl" p="lg" className="game-speaker-control">
            <Group justify="space-between"><Box><Text size="xs" c="dimmed">褰撳墠鑷垜浠嬬粛</Text><Title order={3}>{introPlayer?.name || "鍏ㄩ儴瀹屾垚"} 路 {introPlayer?.role}</Title></Box><Badge color="orange">{introduced.length} / 5 宸插畬鎴?/Badge></Group>
            {introPlayer && <Text mt="md" c="dimmed">鏈樁娈典粎鍏佽鑷垜浠嬬粛鍜屾寚瀹?Agent 鑷垜浠嬬粛锛屼笉鍙嚭绀鸿瘉鐗┿€佹悳璇佹垨娣卞叆绉佽亰銆?/Text>}
          </Paper>
          <Stack gap="xs">{events.filter((event) => event.type === "speech" && Object.values(introLines).includes(event.text)).map(renderEvent)}</Stack>
          {introPlayer && <Button onClick={completeIntro}>{introPlayer.id === "user" ? "鍙戣█" : "涓嬩竴浣?}</Button>}
        </Stack>
      );
    }
    if (phase.id === "search") {
      return (
        <Stack gap="md" align="center">
          <Paper radius="xl" p="xl" className="game-search-stage">
            <IconSearch size={42} /><Title order={2} mt="md">闅忔満鎼滆瘉</Title><Text c="dimmed" mt="sm">鍓╀綑鎼滆瘉娆℃暟锛歿searchesLeft}</Text>
            <Progress value={(2 - searchesLeft) * 50} mt="lg" color="orange" />
            <Button size="lg" radius="xl" mt="xl" disabled={searchesLeft === 0} loading={false} onClick={randomSearch}>寮€濮嬮殢鏈烘悳璇?/Button>
          </Paper>
          {newEvidence && <Paper radius="xl" p="lg" className="game-evidence-event"><Badge color="teal">鏂拌瘉鐗?/Badge><Title order={3} mt="sm">{newEvidence.name}</Title><Text c="dimmed" mt="sm">{newEvidence.description}</Text><Text size="sm" mt="sm">榛樿鍏紑鑼冨洿锛氫粎鑷繁</Text></Paper>}
        </Stack>
      );
    }
    if (phase.id === "vote") {
      return (
        <Stack gap="md">
          <Paper radius="xl" p="lg" className="game-speaker-control"><Title order={3}>鎺ㄧ悊鎶曠エ</Title><Text c="dimmed">鏂板彂瑷€銆佺鑱婂拰璇佺墿鍑虹ず宸插仠姝€傝鐙珛鎻愪氦鍒ゆ柇銆?/Text></Paper>
          {voteSubmitted ? (
            <Paper radius="xl" p="xl" className="game-vote-success"><IconCheck size={44} /><Title order={2} mt="md">鎶曠エ宸叉彁浜?/Title><Text c="dimmed" mt="sm">绛夊緟鍏朵粬鐜╁涓?Agent 瀹屾垚鐙珛鎺ㄧ悊銆?/Text></Paper>
          ) : (
            <Paper radius="xl" p="lg" className="game-vote-form">
              <Text fw={700}>閫夋嫨瀚岀枒浜?/Text>
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
                        <Radio value={player.id} aria-label={`閫夋嫨 ${player.role}`} />
                      </Group>
                    </Paper>
                  ))}
                </Box>
              </Radio.Group>
              <Textarea label="鎺ㄧ悊鐞嗙敱" mt="md" minRows={5} value={voteReason} onChange={(event) => setVoteReason(event.currentTarget.value)} />
              <Text fw={700} mt="md">閫夋嫨鍏抽敭璇佺墿</Text>
              <Checkbox.Group value={voteEvidence} onChange={setVoteEvidence}><Stack gap="xs" mt="xs">{evidence.map((item) => <Checkbox key={item.id} value={item.id} label={item.name} />)}</Stack></Checkbox.Group>
              <Button mt="xl" radius="xl" onClick={submitVote}>纭鎻愪氦鎶曠エ</Button>
            </Paper>
          )}
        </Stack>
      );
    }
    return (
      <Stack gap="md">
        <Paper radius="xl" p="md" className={forcedAnswer ? "game-speaker-control is-forced" : "game-speaker-control"}>
          <Group justify="space-between" align="flex-start">
            <Box><Text size="xs" c="dimmed">{forcedAnswer ? "寮哄埗鍥炵瓟涓? : current ? "褰撳墠鍙戣█浜? : "褰撳墠鏆傛棤瑙掕壊鍙戣█"}</Text><Title order={3}>{current ? `${current.name} 路 ${current.role}` : `涓嬩竴浣嶏細${playerById(queue[0])?.name || "绛夊緟鐢宠"}`}</Title>{forcedAnswer && <Text size="sm" mt={5}>闂锛歿forcedAnswer.question}</Text>}</Box>
            <Stack gap={4} align="flex-end"><Badge color={forcedAnswer ? "red" : "orange"} leftSection={<IconClock size={13} />}>{formatTime(speakerSeconds)}</Badge><Text size="xs" c="dimmed">闃熷垪锛歿queue.map((item) => playerById(item)?.name).join(" 鈫?") || "绌?}</Text></Stack>
          </Group>
          <Group mt="md">{currentSpeaker && <Button size="xs" variant="light" onClick={finishSpeaker}>{current?.agent ? forcedAnswer ? "缁撴潫寮哄埗鍥炵瓟" : "璺宠繃 Agent" : "缁撴潫鍙戣█"}</Button>}{current?.agent && <Button size="xs" variant="subtle">鏆傚仠 Agent</Button>}</Group>
        </Paper>
        <Paper className="game-scene-card" radius="xl"><Box className="game-scene-card__image" /><Stack className="game-scene-card__copy" gap="xs"><Badge color="red" variant="filled">{sceneCard.badge}</Badge><Title order={3}>{sceneCard.title}</Title><Text c="gray.3">{sceneCard.description || "鍚庣鏆傛湭杩斿洖鍦烘櫙鎻忚堪銆?}</Text></Stack></Paper>
        <Paper className="game-scene-card" radius="xl"><Box className="game-scene-card__image" /><Stack className="game-scene-card__copy" gap="xs"><Badge color="red" variant="filled">{sceneCard.badge}</Badge><Title order={3}>{sceneCard.title}</Title><Text c="gray.3">{sceneCard.description || "后端暂未返回场景描述。"}</Text></Stack></Paper>
        <Stack gap="xs">{events.filter((event) => event.type !== "accusation").map(renderEvent)}</Stack>
      </Stack>
    );
  };

  const renderRightPanel = () => (
    <Tabs value={rightTab} onChange={setRightTab} className="game-right-tabs">
      <Tabs.List grow>
        <Tabs.Tab value="script">鍓ф湰</Tabs.Tab><Tabs.Tab value="tasks">浠诲姟</Tabs.Tab><Tabs.Tab value="evidence">璇佺墿</Tabs.Tab><Tabs.Tab value="chat" className={privateInviteStatus === "鏈鐞? || privateInviteStatus === "绋嶅悗澶勭悊" ? "game-chat-tab has-pending-invite" : "game-chat-tab"}>鑱婂ぉ <Badge size="xs">{privateThreads.reduce((sum, item) => sum + item.unread, 0) + (privateInviteStatus === "鏈鐞? || privateInviteStatus === "绋嶅悗澶勭悊" ? 1 : 0)}</Badge></Tabs.Tab>
      </Tabs.List>
      <ScrollArea className="game-right-tab-scroll" offsetScrollbars>
        <Tabs.Panel value="script" pt="md">
          <Stack gap="md">
            <Box>
              <Text className="monospace-label" size="xs" c="dimmed">my private script</Text>
              <Title order={3}>鍛ㄩ噹鐨勫墽鏈?/Title>
              <Text size="sm" c="dimmed">鍙殢鏃舵墦寮€瀹屾暣鍓ф湰锛屽苟绠＄悊宸茬粡淇濆瓨鐨勯珮浜枃娈点€?/Text>
            </Box>
            <Button
              fullWidth
              radius="xl"
              leftSection={<IconBook2 size={17} />}
              onClick={() => setDialog("script")}
            >
              鎵撳紑鎴戠殑鍓ф湰
            </Button>
            <Divider />
            <Group justify="space-between">
              <Text fw={800}>宸蹭繚瀛橀珮浜?/Text>
              <Badge color="yellow" variant="light">{scriptHighlights.length}</Badge>
            </Group>
            {scriptHighlights.length > 0 ? (
              <Stack gap="xs">
                {scriptHighlights.map((highlight) => (
                  <Paper key={highlight.id} p="sm" radius="lg" className="game-highlight-summary">
                    <Group justify="space-between" align="flex-start" wrap="nowrap">
                      <Box>
                        <Text size="xs" c="dimmed">{scriptTitle}</Text>
                        <Text size="sm" mt={4}>{highlight.text}</Text>
                      </Box>
                      <ActionIcon
                        size="sm"
                        variant="subtle"
                        color="red"
                        aria-label="鍒犻櫎楂樹寒"
                        onClick={() => removeScriptHighlight(highlight.id)}
                      >
                        <IconX size={14} />
                      </ActionIcon>
                    </Group>
                  </Paper>
                ))}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">灏氭湭楂樹寒浠讳綍鍓ф湰鏂囨銆?/Text>
            )}
          </Stack>
        </Tabs.Panel>
        <Tabs.Panel value="tasks" pt="md"><Stack gap="sm">{[{ label: "涓荤嚎浠诲姟", text: "鎵惧埌鍘熷闂ㄧ璁板綍", done: evidence.some((item) => item.id === "duty-sheet") }, { label: "闅愯棌浠诲姟", text: "閬垮厤杩囨棭鏆撮湶鏁版嵁鍒犻櫎浜ゆ槗", done: false }, { label: "闃舵浠诲姟", text: phase.id === "search" ? "瀹屾垚涓ゆ鎼滆瘉" : "鎺ㄨ繘褰撳墠娓告垙闃舵", done: phase.id === "search" && searchesLeft === 0 }].map((task) => <Paper key={task.label} p="sm" radius="lg" className="game-clue-item"><Group justify="space-between"><Text fw={800}>{task.label}</Text><Badge color={task.done ? "teal" : "gray"}>{task.done ? "宸插畬鎴? : "杩涜涓?}</Badge></Group><Text size="sm" c="dimmed" mt={5}>{task.text}</Text></Paper>)}</Stack></Tabs.Panel>
        <Tabs.Panel value="evidence" pt="md">
          <Stack gap="md">
            <Group justify="space-between">
              <Text fw={900}>鎴戠殑璇佺墿</Text>
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
                  <Text size="xs" mt="sm">鑾峰緱鏂瑰紡锛歿item.source}</Text>
                  <Group gap={6} mt="sm">
                    <Button size="compact-xs" variant="light" onClick={() => openEvidenceDetail(item)}>鏌ョ湅璇︽儏</Button>
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
                      鍑虹ず璇佺墿
                    </Button>
                  </Group>
                </Paper>
              ))}
            </Stack>

            <Divider />
            <Group justify="space-between">
              <Box>
                <Text fw={900}>宸茶川璇㈢嚎绱?/Text>
                <Text size="xs" c="dimmed">璇佹嵁涓庡叧閿彂瑷€鐨勯棶绛旇褰?/Text>
              </Box>
              <Badge color="blue" variant="light">{inquiryRecords.length}</Badge>
            </Group>
            {inquiryRecords.length > 0 ? (
              <Stack gap="sm">
                {inquiryRecords.map((record) => (
                  <Paper key={record.id} p="sm" radius="lg" className="game-inquiry-record">
                    <Group justify="space-between" align="flex-start">
                      <Box>
                        <Badge size="xs" color={record.sourceType === "璇佹嵁" ? "orange" : "blue"} variant="light">
                          {record.sourceType}
                        </Badge>
                        <Text fw={800} mt={5}>{record.sourceTitle}</Text>
                      </Box>
                      {record.evidence && (
                        <Button size="compact-xs" variant="subtle" onClick={() => openEvidenceDetail(record.evidence!)}>
                          璇︽儏
                        </Button>
                      )}
                    </Group>
                    <Text size="xs" c="dimmed" mt="sm">璐ㄨ瀵硅薄锛歿record.targetName}</Text>
                    <Text size="sm" mt={6}>闂細{record.question}</Text>
                    <Text size="sm" c="dimmed" mt={6}>绛旓細{record.answer}</Text>
                  </Paper>
                ))}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">灏氭湭瀵硅瘉鎹垨鍏抽敭鍙戣█鍙戣捣璐ㄨ銆?/Text>
            )}
          </Stack>
        </Tabs.Panel>
        <Tabs.Panel value="chat" pt="md">
          <Stack gap="md">
            <Paper p="sm" radius="lg" className="game-private-event">
              <Group justify="space-between" align="flex-start">
                <Box>
                  <Group gap={6}>
                    <Text fw={900}>鐧介甫 Agent 鐢宠绉佽亰</Text>
                    <Badge
                      size="xs"
                      color={privateInviteStatus === "鏈鐞? || privateInviteStatus === "绋嶅悗澶勭悊" ? "orange" : privateInviteStatus === "宸叉帴鍙? ? "teal" : "gray"}
                    >
                      {privateInviteStatus}
                    </Badge>
                  </Group>
                  <Text size="sm" c="dimmed" mt={5}>鈥滄垜鍙戠幇闂ㄧ璁板綍瀛樺湪涓€涓笉閫傚悎鍏紑璁ㄨ鐨勬椂闂寸煕鐩俱€傗€?/Text>
                </Box>
              </Group>
              {(privateInviteStatus === "鏈鐞? || privateInviteStatus === "绋嶅悗澶勭悊") && (
                <Group gap={6} mt="sm">
                  <Button size="compact-xs" onClick={() => { setPrivateInviteStatus("宸叉帴鍙?); acceptPrivateInvite("crow"); }}>鍏佽</Button>
                  <Button size="compact-xs" variant="light" onClick={() => setPrivateInviteStatus("绋嶅悗澶勭悊")}>绋嶅悗</Button>
                  <Button size="compact-xs" variant="subtle" color="red" onClick={() => setPrivateInviteStatus("宸叉嫆缁?)}>鎷掔粷</Button>
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
                  <Text fw={900}>鍏叡鑱婂ぉ涓庣嚎绱㈣褰?/Text>
                  <Text size="xs" c="dimmed">{chatHistoryOpen ? "鏀惰捣" : "灞曞紑"}</Text>
                </Group>
                <Badge variant="light">{events.filter((event) => ["speech", "evidence", "accusation", "inquiry"].includes(event.type)).length}</Badge>
              </Group>
              {chatHistoryOpen && (
                <Stack gap="xs">
                  {events.filter((event) => ["speech", "evidence", "accusation", "inquiry"].includes(event.type)).map((event) => (
                    <Paper key={`chat-${event.id}`} p="sm" radius="lg" className="game-chat-history-item">
                      {event.type === "speech" && <><Text fw={800}>{event.speaker}</Text><Text size="sm" c="dimmed">{event.text}</Text></>}
                      {event.type === "evidence" && <><Text fw={800}>{event.speaker} 鍑虹ず璇佹嵁锛歿event.evidence.name}</Text><Text size="sm" c="dimmed">{event.reason || event.evidence.description}</Text></>}
                      {event.type === "accusation" && <><Text fw={800}>鎬€鐤戣褰?/Text><Text size="sm" c="dimmed">{event.actor} 灏嗏€渰event.sourceTitle}鈥濇寚鍚?{event.target}{event.reason ? `锛?{event.reason}` : ""}</Text></>}
                      {event.type === "inquiry" && <><Text fw={800}>璐ㄨ璁板綍 路 {event.asker} 鈫?{event.target}</Text><Text size="sm">闂細{event.question}</Text><Text size="sm" c="dimmed">绛旓細{event.answer}</Text></>}
                    </Paper>
                  ))}
                </Stack>
              )}
            </Box>

            <Divider />
            <Box>
              <Text fw={900} mb="xs">绉佽亰浼氳瘽</Text>
              <Group gap="xs" mb="sm">{privateThreads.map((thread) => <Button key={thread.id} size="xs" variant={thread.id === activeThreadId ? "filled" : "light"} onClick={() => { setActiveThreadId(thread.id); setPrivateThreads((items) => items.map((item) => item.id === thread.id ? { ...item, unread: 0 } : item)); }}>{thread.name}{thread.unread > 0 && ` (${thread.unread})`}</Button>)}</Group>
              {activeThread ? <Stack gap="sm"><Text fw={900}>{activeThread.name}</Text><Stack gap="xs">{activeThread.messages.map((text, index) => <Paper key={index} p="sm" radius="lg" className="game-private-chat"><Text size="sm">{text}</Text></Paper>)}</Stack><TextInput value={privateMessage} onChange={(event) => setPrivateMessage(event.currentTarget.value)} placeholder="杈撳叆绉佽亰鍐呭鈥? rightSection={<ActionIcon onClick={sendPrivateMessage}><IconSend size={15} /></ActionIcon>} /></Stack> : <Text c="dimmed">鏆傛棤绉佽亰浼氳瘽銆?/Text>}
              {activeThread ? <Stack gap="sm"><Text fw={900}>{activeThread.name}</Text><Stack gap="xs">{activeThread.messages.map((text, index) => <Paper key={index} p="sm" radius="lg" className="game-private-chat"><Text size="sm">{text}</Text></Paper>)}</Stack><TextInput value={privateMessage} onChange={(event) => setPrivateMessage(event.currentTarget.value)} placeholder="输入私聊内容..." rightSection={<ActionIcon onClick={sendPrivateMessage}><IconSend size={15} /></ActionIcon>} /></Stack> : <Text c="dimmed">暂无私聊会话。</Text>}
          </Stack>
        </Tabs.Panel>
      </ScrollArea>
    </Tabs>
  );

  const footerActions = () => {
    if (phase.id === "vote") return <Text c="dimmed">鎶曠エ闃舵锛氬叕鍏卞彂瑷€銆佺鑱婂拰璇佺墿鎿嶄綔宸查攣瀹氥€?/Text>;
    if (phase.id !== "discussion") return <Group><Button radius="xl" onClick={advancePhase} disabled={(phase.id === "role-selection" && !roleConfirmed) || (phase.id === "script-reading" && !readingDone) || (phase.id === "intro" && introduced.length < 5) || (phase.id === "search" && searchesLeft > 0)}>杩涘叆涓嬩竴闃舵</Button><Text size="sm" c="dimmed">瀹屾垚褰撳墠闃舵瑕佹眰鍚庣户缁?/Text></Group>;
    return (
      <Group gap="xs" wrap="nowrap" style={{ width: "100%" }}>
        {!isUserSpeaking && !userQueued && <Button radius="xl" onClick={joinQueue} disabled={Boolean(forcedAnswer)}>閫夋嫨鍙戣█</Button>}
        {userQueued && !isUserSpeaking && <Button radius="xl" variant="light" onClick={cancelQueue}>鍙栨秷鐢宠 路 鎺掍綅 {queue.indexOf("user") + 1}</Button>}
        {isUserSpeaking && <Button radius="xl" color="orange" onClick={finishSpeaker}>缁撴潫鍙戣█</Button>}
        <Button radius="xl" variant="light" onClick={() => setDialog("private")}>鍙戣捣绉佽亰</Button>
        <Button radius="xl" variant="light" disabled={!isUserSpeaking} onClick={() => setDialog("force")}>鎸囧畾 Agent 鍥炵瓟</Button>
        <Button radius="xl" variant="light" disabled={!isUserSpeaking} onClick={() => setDialog("evidence")}>鍑虹ず璇佺墿</Button>
        <Button radius="xl" variant="subtle" color="orange" disabled={Boolean(forcedAnswer)} onClick={() => goToPhase(5)}>杩涘叆鎺ㄧ悊鎶曠エ</Button>
        <TextInput value={publicMessage} onChange={(event) => setPublicMessage(event.currentTarget.value)} placeholder={isUserSpeaking ? "杈撳叆褰撳墠鍏叡鍙戣█鈥? : "杞埌浣犲彂瑷€鍚庡彲杈撳叆鍐呭"} disabled={!isUserSpeaking} className="game-message-input" radius="xl" />
        <ActionIcon size="lg" radius="xl" onClick={sendPublicMessage} disabled={!isUserSpeaking}><IconSend size={17} /></ActionIcon>
      </Group>
    );
  };

  return (
    <StudioShell title="娓告垙涓荤晫闈? subtitle={`褰撳墠鍓ф湰锛?{scriptTitle}銆俙} eyebrow="live game / interactive demo" stats={[{ label: "褰撳墠闃舵", value: phase.shortLabel }, { label: "褰撳墠鍙戣█浜?, value: current?.name || "鏆傛棤" }, { label: "鍙戣█鍊掕鏃?, value: formatTime(speakerSeconds) }, { label: "娓告垙妯″紡", value: gameMode }]}>
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
                          <Text size="xs" fw={900}>DM 路 {dm?.role}</Text>
                          <Badge size="xs" color="red" variant="light">AI</Badge>
                        </Group>
                        <Text size="xs" c="dimmed">{dm?.name} 路 涓绘寔涓?/Text>
                        {feedback && <Text size="xs" className="game-dm-progress">{feedback}</Text>}
                      </Box>
                    </Group>
                  </Paper>
                </Box>
                <Box visibleFrom="sm">
                  <Text size="xs" c="dimmed">褰撳墠鍙戣█ / 涓嬩竴浣?/Text>
                  <Text fw={800}>{current?.role || "鏆傛棤"} 鈫?{playerById(queue.find((item) => item !== currentSpeaker) || null)?.role || "绛夊緟鐢宠"}</Text>
                </Box>
              </Group>
              <Group gap="xs"><Badge size="lg" color="orange" leftSection={<IconClock size={13} />}>{formatTime(speakerSeconds)}</Badge><Button size="xs" variant="light" onClick={() => setDialog("rules")}>娓告垙瑙勫垯</Button><Tooltip label={fullscreen ? "閫€鍑哄叏灞? : "鍏ㄥ睆"}><ActionIcon size="lg" onClick={toggleFullscreen}>{fullscreen ? <IconX size={18} /> : <IconMaximize size={18} />}</ActionIcon></Tooltip><ActionIcon size="lg" variant={settingsOpen ? "filled" : "light"} onClick={() => setSettingsOpen((value) => !value)}><IconSettings size={18} /></ActionIcon><Button size="xs" color="red" variant="subtle" onClick={() => navigate("/games")}>閫€鍑?/Button></Group>
            </Group>
            <Box className="game-phase-track">{GAME_PHASES.map((item, index) => <button key={item.id} disabled={index === 0 && roleConfirmed} className={`${index < phaseIndex ? "game-phase-step is-complete" : index === phaseIndex ? "game-phase-step is-active" : "game-phase-step"}${index === 0 && roleConfirmed ? " is-locked" : ""}`} onClick={() => goToPhase(index)}><span>{index < phaseIndex ? "鉁? : index + 1}</span><Text size="xs">{item.shortLabel}</Text></button>)}</Box>
          </header>

          {settingsOpen && (
            <Paper className="game-settings-strip game-settings-strip--phased" radius={0} px="lg" py="sm">
              <Group justify="space-between">
                <Group gap="xs">
                  <Badge variant="light">瀛楀箷锛氬紑鍚?/Badge>
                  <Badge variant="light">闊虫晥锛?0%</Badge>
                  <Badge variant="light">Agent 鑺傚锛氶€備腑</Badge>
                </Group>
                <Text size="sm" c="dimmed">婕旂ず璁剧疆浠呬繚瀛樺湪褰撳墠椤甸潰鐘舵€併€?/Text>
              </Group>
            </Paper>
          )}

          <main className="game-workspace__body game-workspace__body--phased">
            <aside className="game-side-panel game-people-panel">
              <Group justify="space-between" mb="md"><Group gap="xs"><IconUsers size={18} /><Text fw={900}>鐜╁涓?Agent</Text></Group><Badge color="teal">6 鍦ㄧ嚎</Badge></Group>
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
                              {isSelf && <Badge size="xs" color="orange" variant="filled">鎴?/Badge>}
                            </Group>
                            <Text size="xs" c="dimmed" truncate>鐜╁锛歿player.name}</Text>
                          </Box>
                          <Badge size="xs" color={status === "姝ｅ湪鍙戣█" ? "orange" : status === "鎬濊€冧腑" ? "blue" : "gray"} variant="dot">{status}</Badge>
                        </Group>
                      </Paper>
                    );
                  })}
                </Stack>
              </ScrollArea>
              {selectedPlayer && selectedPlayer.id !== "dm" && <Paper p="sm" radius="lg" className="game-player-actions"><Group justify="space-between"><Text fw={800}>{selectedPlayer.role} 路 蹇嵎鎿嶄綔</Text><Badge color={selectedPlayer.agent ? "blue" : "orange"} variant="light">{selectedPlayer.agent ? "AI 鐜╁" : "鐪熶汉鐜╁"}</Badge></Group><Group gap={5} mt="sm"><Button size="xs" variant="light" onClick={() => showFeedback(`${selectedPlayer.role} 鐨勫叕寮€韬唤锛?{selectedPlayer.publicIdentity}`)}>鍏紑淇℃伅</Button>{selectedPlayer.id !== "user" && <Button size="xs" variant="light" onClick={() => { setTargetId(selectedPlayer.id); setDialog("private"); }}>鍙戣捣绉佽亰</Button>}{selectedPlayer.agent && <Button size="xs" variant="light" disabled={!isUserSpeaking} onClick={() => { setTargetId(selectedPlayer.id); setDialog("force"); }}>鎸囧畾鍥炵瓟</Button>}</Group></Paper>}
            </aside>

            <section className="game-core-panel"><ScrollArea className="game-core-scroll" offsetScrollbars>{renderStage()}</ScrollArea></section>
            <aside className="game-side-panel game-personal-panel">{renderRightPanel()}</aside>
          </main>

          <footer className="game-workspace__footer game-workspace__footer--actions">{footerActions()}</footer>
        </Paper>
      </Box>

      <Modal opened={dialog === "force"} onClose={() => setDialog(null)} title="鎸囧畾 Agent 鍥炵瓟" centered><Stack><Select label="閫夋嫨 Agent" value={targetId} onChange={(value) => setTargetId(value || "crow")} data={agents.map((agent) => ({ value: agent.id, label: `${agent.name} 路 ${agent.role}` }))} /><Textarea label="闇€瑕佸洖绛旂殑闂" value={question} onChange={(event) => setQuestion(event.currentTarget.value)} minRows={4} /><Button onClick={confirmForcedAnswer}>纭鎸囧畾</Button></Stack></Modal>
      <Modal opened={dialog === "evidence"} onClose={() => setDialog(null)} title="鍑虹ず璇佺墿" centered><Stack><Select label="閫夋嫨璇佺墿" value={selectedEvidenceId} onChange={(value) => setSelectedEvidenceId(value || evidence[0]?.id)} data={evidence.map((item) => ({ value: item.id, label: item.name }))} /><Textarea label="鍑虹ず鐞嗙敱" placeholder="璇存槑杩欓」璇佹嵁鏀寔鎴栧弽椹充簡浠€涔堣鐐? value={evidenceReason} onChange={(event) => setEvidenceReason(event.currentTarget.value)} minRows={3} /><Radio.Group label="鍏紑鑼冨洿" value={evidenceVisibility} onChange={setEvidenceVisibility}><Stack mt="xs"><Radio value="鎵€鏈変汉" label="鍏紑缁欐墍鏈変汉" /><Radio value="鎸囧畾瑙掕壊" label="鍙垎浜粰鎸囧畾瑙掕壊" /></Stack></Radio.Group>{evidenceVisibility === "鎸囧畾瑙掕壊" && <Select label="鎸囧畾瑙掕壊" value={targetId} onChange={(value) => setTargetId(value || "chen")} data={GAME_PLAYERS.filter((player) => player.id !== "user").map((player) => ({ value: player.id, label: player.name }))} />}<Button onClick={showEvidence}>纭鍑虹ず</Button></Stack></Modal>
      <Modal
        opened={dialog === "evidence-detail"}
        onClose={() => setDialog(null)}
        title="璇佹嵁璇︽儏"
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
                <Group justify="space-between"><Text c="dimmed">鍙戠幇鍦扮偣</Text><Text fw={700}>{selectedDetailEvidence.location}</Text></Group>
                <Group justify="space-between"><Text c="dimmed">璁板綍鏃堕棿</Text><Text fw={700}>{selectedDetailEvidence.time}</Text></Group>
                <Group justify="space-between"><Text c="dimmed">鑾峰緱鏂瑰紡</Text><Text fw={700}>{selectedDetailEvidence.source}</Text></Group>
              </Stack>
            </Paper>
          </Stack>
        )}
      </Modal>
      <Modal
        opened={dialog === "discussion-detail"}
        onClose={() => setDialog(null)}
        title="鍏叡璁ㄨ璇︽儏"
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
                  {selectedDiscussionSpeaker && <Text size="sm" c="dimmed">{selectedDiscussionSpeaker.role} 路 {selectedDiscussionSpeaker.publicIdentity}</Text>}
                </Box>
              </Group>
              {selectedDiscussionSuspect && (
                <Paper p="sm" radius="lg" className="game-discussion-suspect">
                  <Text size="xs" c="dimmed">褰撳墠鎬€鐤戝璞?/Text>
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
                  <Text c="dimmed">璇佹嵁鍥剧墖鍗犱綅</Text>
                </Box>
                <Box>
                  <Group justify="space-between">
                    <Title order={4}>{selectedDiscussionEvidence.name}</Title>
                    <Badge color="orange" variant="light">{selectedDiscussionEvidence.visibility}</Badge>
                  </Group>
                  <Text size="sm" c="dimmed" mt="sm" lh={1.7}>{selectedDiscussionEvidence.description}</Text>
                  <Group gap="lg" mt="sm">
                    <Text size="xs">鍦扮偣锛歿selectedDiscussionEvidence.location}</Text>
                    <Text size="xs">鏃堕棿锛歿selectedDiscussionEvidence.time}</Text>
                  </Group>
                </Box>
              </Paper>
            )}

            <Group justify="flex-end">
              <Button variant="light" onClick={() => openPointDialog(selectedDiscussionSource.id)}>鎸囧悜瀚岀枒浜?/Button>
              <Button color="blue" onClick={() => openInquiryDialog(selectedDiscussionSource.id)}>
                {selectedDiscussionSource.type === "evidence" ? "閽堝姝よ瘉鎹川璇? : "閽堝姝ゅ彂瑷€璐ㄨ"}
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
      <Modal opened={dialog === "point"} onClose={() => setDialog(null)} title="灏嗙嚎绱㈡寚鍚戝珜鐤戜汉" centered>
        <Stack>
          <Text size="sm" c="dimmed">
            鏉ユ簮锛歿discussionSource(selectedDiscussionEventId) ? discussionSourceTitle(discussionSource(selectedDiscussionEventId)!) : "鏈€夋嫨"}
          </Text>
          <Select
            label="浣犳€€鐤戣皝"
            value={pointTargetId}
            onChange={(value) => setPointTargetId(value || "chen")}
            data={GAME_PLAYERS.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({
              value: player.id,
              label: `${player.role} 路 ${player.name}`,
            }))}
          />
          <Textarea
            label="鎬€鐤戠悊鐢憋紙鍙€夛級"
            value={pointReason}
            onChange={(event) => setPointReason(event.currentTarget.value)}
            minRows={3}
          />
          <Button onClick={confirmPoint}>纭鎸囧悜</Button>
        </Stack>
      </Modal>
      <Modal opened={dialog === "inquiry"} onClose={() => setDialog(null)} title="閽堝绾跨储鍙戣捣璐ㄨ" centered size="lg">
        <Stack>
          <Text size="sm" c="dimmed">
            璐ㄨ鏉ユ簮锛歿discussionSource(selectedDiscussionEventId) ? discussionSourceTitle(discussionSource(selectedDiscussionEventId)!) : "鏈€夋嫨"}
          </Text>
          <Select
            label="璐ㄨ瀵硅薄"
            value={inquiryTargetId}
            onChange={(value) => setInquiryTargetId(value || "crow")}
            data={GAME_PLAYERS.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({
              value: player.id,
              label: `${player.role} 路 ${player.name}${player.agent ? " 路 AI" : " 路 鐪熶汉"}`,
            }))}
          />
          <Textarea
            label="璐ㄨ闂"
            placeholder="璇存槑杩欓」璇佹嵁鎴栧彂瑷€涓庝綘鐨勭枒闂箣闂存湁浠€涔堝叧绯?
            value={inquiryQuestion}
            onChange={(event) => setInquiryQuestion(event.currentTarget.value)}
            minRows={4}
          />
          <Button onClick={confirmInquiry}>鍙戣捣璐ㄨ骞朵繚瀛樿褰?/Button>
        </Stack>
      </Modal>
      <Modal opened={dialog === "private"} onClose={() => setDialog(null)} title="鍙戣捣鎴栨帴鍙楃鑱? centered><Stack><Select label="绉佽亰瀵硅薄" value={targetId} onChange={(value) => setTargetId(value || "crow")} data={GAME_PLAYERS.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({ value: player.id, label: `${player.role} 路 鐜╁锛?{player.name}` }))} /><Text size="sm" c="dimmed">绉佽亰寤虹珛鍚庡嵆鍙洿鎺ュ璇濓紝涓嶉渶瑕侀澶栬缃?Agent 鍙戣█鏉冮檺锛涚鑱婂唴瀹瑰拰璇佺墿涓嶄細鑷姩鍏紑銆?/Text><Button onClick={() => acceptPrivateInvite()}>寤虹珛绉佽亰</Button></Stack></Modal>
      <Modal opened={dialog === "rules"} onClose={() => setDialog(null)} title="娓告垙瑙勫垯" centered size="lg"><Stack><Text>鍏叡璁ㄨ閲囩敤鍗曚竴鍙戣█鏉冿紝鏅€氬彂瑷€鎸夌敵璇烽『搴忚繘琛屻€?/Text><Text>琚寚瀹氬洖绛旂殑 Agent 蹇呴』鎴愪负涓嬩竴浣嶅彂瑷€鑰咃紝鍥炵瓟缁撴潫鍚庢仮澶嶅師闃熷垪銆?/Text><Text>绉佽亰涓庡叕鍏辫璁虹嫭绔嬭繍琛岋紝绉佽亰鍐呭鍜岃瘉鐗╀粎鍙備笌鑰呭彲瑙併€?/Text><Text>杩涘叆鎶曠エ闃舵鍚庡仠姝㈡柊鐨勫彂瑷€銆佺鑱婂拰璇佺墿鍑虹ず銆?/Text></Stack></Modal>
      <Modal
        opened={dialog === "script"}
        onClose={() => {
          setDialog(null);
          setSelectedScriptText("");
        }}
        title="鎴戠殑鍓ф湰 路 鍛ㄩ噹"
        centered
        size="xl"
        scrollAreaComponent={ScrollArea.Autosize}
      >
        <Stack gap="lg">
          <Text size="sm" c="dimmed">鎷栧姩閫変腑鍏蜂綋璇彞锛屽啀鐐瑰嚮鈥滈珮浜€変腑鏂囨鈥濄€傞珮浜細鑷姩淇濆瓨鍦ㄥ綋鍓嶆祻瑙堝櫒銆?/Text>
          {[{ title: scriptTitle, content: scriptReadingContent || "鍚庣鏆傛湭杩斿洖鍓ф湰姝ｆ枃銆? }].map((item, chapterIndex) => (
          {[{ title: scriptTitle, content: scriptReadingContent || "后端暂未返回剧本正文。" }].map((item, chapterIndex) => (
              <Group justify="space-between" align="flex-start">
                <Title order={3}>{item.title}</Title>
                <Badge color="yellow" variant="light">
                  {scriptHighlights.filter((highlight) => highlight.chapter === chapterIndex).length} 澶勯珮浜?                </Badge>
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
                  disabled={!selectedScriptText}
                  onClick={addScriptHighlight}
                >
                  楂樹寒閫変腑鏂囨
                </Button>
              </Group>
            </Paper>
          ))}
          {scriptHighlights.length > 0 && (
            <Box>
              <Title order={4}>绠＄悊楂樹寒</Title>
              <Stack gap="xs" mt="sm">
                {scriptHighlights.map((highlight) => (
                  <Paper key={highlight.id} radius="lg" p="sm" className="game-highlight-summary">
                    <Group justify="space-between" wrap="nowrap">
                      <Box>
                        <Text size="xs" c="dimmed">{scriptTitle}</Text>
                        <Text size="sm">{highlight.text}</Text>
                      </Box>
                      <Button size="xs" variant="subtle" color="red" onClick={() => removeScriptHighlight(highlight.id)}>
                        鍒犻櫎
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
          aria-label="鍏抽棴瑙掕壊鑷垜浠嬬粛"
          onClick={() => setIntroSpotlight(null)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") setIntroSpotlight(null);
          }}
        >
          <Box className="game-intro-portrait" aria-hidden="true">
<<<<<<< HEAD
            <Text className="monospace-label" size="xs" c="dimmed">character portrait</Text>
            <Text c="dimmed">瑙掕壊绔嬬粯鍗犱綅</Text>
=======
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
>>>>>>> d8cd0c1dbe7aeef883a706fea024dc80cf778d99
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
                <Text size="sm" c="dimmed">{introSpotlight.name} 路 {introSpotlight.agent ? "AI 鐜╁" : "鐪熶汉鐜╁"}</Text>
              </Box>
            </Group>
            <Text fz="lg" lh={1.8} mt="md">鈥渰introLines[introSpotlight.id]}鈥?/Text>
            <Text size="xs" c="dimmed" ta="center" mt="md">鐐瑰嚮浠绘剰浣嶇疆缁х画</Text>
          </Paper>
        </Box>
      )}
    </StudioShell>
  );
}

export { GamePage };
