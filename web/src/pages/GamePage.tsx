import React from "react";
import { StudioShell } from "./StudioShell";
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
  INTRO_LINES,
  PRIVATE_THREADS,
} from "./gameMockData";
import { backendEvidenceToGameEvidence } from "../api/adapters";
import {
  createEvidence,
  discoverEvidence,
  createGameSession,
  forceGamePhase,
  getGamePhase,
  getEvidences,
  presentEvidence,
  saveConversation,
  sendPrivateChatMessage,
  submitGameVote,
  submitAgentVotes,
  invokeAI,
  invokeAIStream,
  advanceGamePhase,
  applyGameCast,
  revealGame,
  generateSpoiler,
  getMyScript,
  getEvidencePool,
  getGameSnapshot,
  getScript,
  listAgents,
  initPersonas,
  listPersonas,
  postGameReflection,
  recordChatCount,
  type InvocationRequest,
} from "../api/invoke";
import type { Actor, SafeActor, LLMMessage } from "../types";
import {
  buildCastPayload,
  buildCompanionCastingOptions,
  buildRosterFromCast,
  HUMAN_PLAYER,
  scriptCharacterToCastingRole,
  type CastAssignment,
  type CastingAgentOption,
  type CastingRoleOption,
  type ScriptCharacterSource,
} from "../utils/gameCasting";
import { AgentCastingPanel } from "../components/AgentCastingPanel";
import { buildReviewPath } from "../utils/gameNavigation";

// ============================
// 角色立绘
// ============================

const characterPortraits: Record<string, string> = {
  "周野": new URL("../Character/周野.png", import.meta.url).href,
  "顾沉": new URL("../Character/顾沉.png", import.meta.url).href,
  "沈禾": new URL("../Character/沈禾.png", import.meta.url).href,
  "周岚": new URL("../Character/周岚.png", import.meta.url).href,
  "秦野": new URL("../Character/秦野.png", import.meta.url).href,
  "林远": new URL("../Character/林远.png", import.meta.url).href,
};

const agentPortraits: Record<string, string> = {
  "白鸦": new URL("../video_picture/白鸽.png", import.meta.url).href,
  "回声": new URL("../video_picture/回声.png", import.meta.url).href,
  "纸鸮": new URL("../video_picture/纸鸮.png", import.meta.url).href,
  "燧石": new URL("../video_picture/燧石.png", import.meta.url).href,
  "月蛾": new URL("../video_picture/月蛾.png", import.meta.url).href,
  "影织者": new URL("../video_picture/影织者.png", import.meta.url).href,
  "夜蝉": new URL("../video_picture/夜蝉.png", import.meta.url).href,
  "雾港主理人": new URL("../video_picture/雾港主理人.png", import.meta.url).href,
  "暮烛引导员": new URL("../video_picture/暮烛引导员.png", import.meta.url).href,
  "铁幕裁判": new URL("../video_picture/铁幕裁判.png", import.meta.url).href,
};

const dmPortrait = new URL("../video_picture/雾港主理人.png", import.meta.url).href;

const scriptMap: Record<string, string> = {
  "xiutie-avenue-missing-three-minutes": "锈铁大道",
  "black-archive": "黑箱档案馆",
  "mirror-parade": "镜面游行",
  "salt-ward": "盐雾病房",
  "wolf-assembly": "狼群集会",
  "paper-cathedral": "纸穹教堂",
};

// ============================
// 角色名映射系统
// 后端可能返回各种格式的角色名（英文key、拼音、中文名等），
// 需要统一映射到前端显示用的中文名
// ============================

const ROLE_NAME_ALIASES: Record<string, string> = {
  user: "周野",
  chen: "顾沉",
  crow: "沈禾",
  su: "周岚",
  echo: "秦野",
  lin: "林远",
  zhouye: "周野",
  guchen: "顾沉",
  shenhe: "沈禾",
  zhoulan: "周岚",
  qinye: "秦野",
  linyuan: "林远",
  "zhou-ye": "周野",
  "gu-chen": "顾沉",
  "shen-he": "沈禾",
  "zhou-lan": "周岚",
  "qin-ye": "秦野",
  "lin-yuan": "林远",
  "周野": "周野",
  "顾沉": "顾沉",
  "沈禾": "沈禾",
  "周岚": "周岚",
  "秦野": "秦野",
  "林远": "林远",
};

const PLAYER_NAME_ALIASES: Record<string, string> = {
  user: "林晓青",
  chen: "陈墨",
  crow: "白鸦",
  su: "苏颜",
  echo: "回声",
  lin: "林远",
  "white-crow": "白鸦",
  "paper-owl": "纸鸮",
  flint: "燧石",
  "luna-moth": "月蛾",
  "night-cicada": "夜蝉",
  "mist-harbor": "雾港主理人",
  "candle-core": "暮烛引导员",
  "iron-judge": "铁幕裁判",
  "shadow-weaver": "影织者",
  "moon-moth": "月蛾",
  compass: "罗盘",
};

const ROLE_TO_INTRO_KEY: Record<string, string> = {
  "周野": "user",
  "顾沉": "chen",
  "沈禾": "crow",
  "周岚": "su",
  "秦野": "echo",
  "林远": "lin",
};

function normalizeRoleToken(value: unknown) {
  return String(value || "")
    .toLowerCase()
    .replace(/agent/g, "")
    .replace(/[^a-z0-9\u4e00-\u9fa5]/g, "");
}

function resolveRoleName(value: unknown, fallback = "") {
  const raw = String(value || "").trim();
  const normalized = normalizeRoleToken(raw);
  return ROLE_NAME_ALIASES[raw] || ROLE_NAME_ALIASES[normalized] || fallback || raw || "未知角色";
}

function getRolePortrait(role: unknown, fallback = "") {
  const resolved = resolveRoleName(role, fallback);
  const fallbackResolved = resolveRoleName(fallback);
  return characterPortraits[resolved] || characterPortraits[fallbackResolved] || agentPortraits[resolved] || agentPortraits[fallbackResolved];
}

function getAgentPortrait(name: string) {
  return agentPortraits[name] || agentPortraits[resolvePlayerName(name)];
}

function resolvePlayerName(value: unknown, fallback = "") {
  const raw = String(value || "").trim();
  const normalized = normalizeRoleToken(raw);
  return PLAYER_NAME_ALIASES[raw] || PLAYER_NAME_ALIASES[normalized] || fallback || raw || "玩家";
}

type PublicEvent =
  | { id: number; type: "speech"; speaker: string; text: string; tone: string; suspectId?: string; evidenceId?: string }
  | { id: number; type: "system"; title: string; text: string }
  | { id: number; type: "evidence"; speaker: string; evidence: Evidence; reason?: string; suspectId?: string; aiResponse?: string; targetName?: string }
  | { id: number; type: "forced"; asker: string; agent: string; question: string }
  | { id: number; type: "private"; agent: string; text: string }
  | { id: number; type: "accusation"; actor: string; target: string; sourceTitle: string; reason?: string }
  | { id: number; type: "inquiry"; asker: string; target: string; sourceTitle: string; question: string; answer: string };

type PublicEventInput =
  | { type: "speech"; speaker: string; text: string; tone: string; suspectId?: string; evidenceId?: string }
  | { type: "system"; title: string; text: string }
  | { type: "evidence"; speaker: string; evidence: Evidence; reason?: string; suspectId?: string; aiResponse?: string; targetName?: string }
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

type StreamingState = {
  active: boolean;
  agentKey: string;
  agentName: string;
  partial: string;
  phase: "intro" | "speech" | "forced" | "inquiry";
  resolveId?: number; // event id to append text to
};

type ScriptHighlight = {
  id: string;
  chapter: number;
  text: string;
};

const defaultInitialEvents: PublicEvent[] = [
  { id: 1, type: "system", title: "阶段开始", text: "公共讨论已开启，所有发言按照队列顺序进行。" },
];

function formatTime(totalSeconds: number) {
  return `${String(Math.floor(totalSeconds / 60)).padStart(2, "0")}:${String(totalSeconds % 60).padStart(2, "0")}`;
}

function isDetectiveObserver(characterName: string) {
  const name = characterName.trim();
  return !name || name === "侦探" || name.startsWith("林晓青");
}

async function loadReadingMaterial(
  scriptId: string,
  sessionId: string,
  characterName: string,
): Promise<{ chapters: Array<{ title: string; content: string }>; characterLabel: string }> {
  if (isDetectiveObserver(characterName)) {
    const scriptResult = await getScript(scriptId);
    const story = scriptResult.globalStory || "";
    return {
      chapters: story
        ? [{ title: "案件背景", content: story }]
        : [{ title: "案件背景", content: "（暂无背景故事）" }],
      characterLabel: "林晓青 · 侦探",
    };
  }
  const scriptResult = await getMyScript(sessionId, characterName);
  return {
    chapters: scriptResult.chapters || [],
    characterLabel: scriptResult.character_name || characterName,
  };
}

function GamePage() {
  const navigate = useNavigate();
  const { id = "xiutie-avenue-missing-three-minutes" } = useParams();
  const scriptTitle = scriptMap[id] || "未知剧本";
  const gameMode = id === "black-archive" ? "单人游戏" : "真人组队";
  const { ref: fullscreenRef, toggle: toggleFullscreen, fullscreen } = useFullscreen();

  const [phaseIndex, setPhaseIndex] = React.useState(0);
  const [sessionId, setSessionId] = React.useState(
    () => window.localStorage.getItem(`game-session:${id}`) || "",
  );
  const phase = GAME_PHASES[phaseIndex];
  const [selectedRole, setSelectedRole] = React.useState(
    () => window.localStorage.getItem(`selected-role:${id}`) || "",
  );
  const [allSeatsFilled, setAllSeatsFilled] = React.useState(false);
  const [roleConfirmed, setRoleConfirmed] = React.useState(false);
  const [scriptCharacters, setScriptCharacters] = React.useState<ScriptCharacterSource[]>([]);
  const [availableAgents, setAvailableAgents] = React.useState<CastingAgentOption[]>([]);
  const [castAssignments, setCastAssignments] = React.useState<CastAssignment[]>(() => {
    try {
      const saved = window.localStorage.getItem(`game-cast:${id}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        return parsed.castAssignments || [];
      }
    } catch {
      // ignore
    }
    return [];
  });

  const castingRoles = React.useMemo<CastingRoleOption[]>(() => {
    const playable = scriptCharacters.filter((character) => !character.isVictim);
    if (playable.length > 0) {
      return playable.map((character, index) => scriptCharacterToCastingRole(character, index));
    }
    return GAME_PLAYERS.filter((player) => player.id !== "dm" && player.role !== "顾沉")
      .map((player, index) => ({
        id: player.id,
        role: player.role,
        publicIdentity: player.publicIdentity,
        background: player.background,
        tags: player.tags,
        color: player.color,
      }));
  }, [scriptCharacters]);

  const rosterPlayers = React.useMemo(
    () => buildRosterFromCast(castingRoles, castAssignments, availableAgents),
    [castingRoles, castAssignments, availableAgents],
  );

  /** 讨论阶段 Agent 发言顺序：与选角/自我介绍顺序一致 */
  const discussionAgentIds = React.useMemo(
    () => rosterPlayers.filter((player) => player.agent).map((player) => player.id),
    [rosterPlayers],
  );

  const dynamicPlayers = React.useMemo(() => {
    const dm = GAME_PLAYERS.find((player) => player.id === "dm");
    const detective: typeof rosterPlayers = rosterPlayers.some((player) => player.id === "user")
      ? []
      : [{
          id: "user",
          name: "林晓青",
          role: "侦探",
          publicIdentity: "案件调查者",
          agent: false,
          color: "orange",
          status: "空闲",
          tags: ["调查", "质询"],
          background: "以第三方侦探身份参与搜证与质询，不扮演嫌疑人。",
        }];
    if (rosterPlayers.length > 0) {
      return dm ? [dm, ...detective, ...rosterPlayers] : [...detective, ...rosterPlayers];
    }
    return dm ? [dm, ...detective] : detective;
  }, [rosterPlayers]);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [scriptResult, agentResult, personaResult] = await Promise.all([
          getScript(id),
          listAgents(),
          listPersonas("companion"),
        ]);
        if (cancelled) return;
        let personas = personaResult || [];
        if (personas.length === 0) {
          try {
            await initPersonas();
            personas = await listPersonas("companion");
          } catch {
            // 人设库未初始化时不阻塞选角
          }
        }
        setScriptCharacters((scriptResult.characters || []) as ScriptCharacterSource[]);
        setAvailableAgents(
          buildCompanionCastingOptions(agentResult.agents || [], personas),
        );
      } catch (error) {
        console.warn("剧本角色或 Agent 人设加载失败:", error);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);
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
  const [queue, setQueue] = React.useState<string[]>([]);
  const [currentSpeaker, setCurrentSpeaker] = React.useState<string | null>(null);
  const [discussionRoundIdle, setDiscussionRoundIdle] = React.useState(false);
  const [forcedAnswer, setForcedAnswer] = React.useState<{ asker: string; agentId: string; question: string } | null>(null);
  const [events, setEvents] = React.useState<PublicEvent[]>(defaultInitialEvents);
  const [rightTab, setRightTab] = React.useState<string | null>("script");
  const [dialog, setDialog] = React.useState<DialogType>(null);
  const [selectedPlayerId, setSelectedPlayerId] = React.useState<string | null>(null);
  const [targetId, setTargetId] = React.useState("");
  const [question, setQuestion] = React.useState("");
  const [selectedEvidenceId, setSelectedEvidenceId] = React.useState("");
  const [evidenceVisibility, setEvidenceVisibility] = React.useState("所有人");
  const [evidenceReason, setEvidenceReason] = React.useState("");
  const [privateThreads, setPrivateThreads] = React.useState<typeof PRIVATE_THREADS>([]);
  const [activeThreadId, setActiveThreadId] = React.useState("");
  const [privateMessage, setPrivateMessage] = React.useState("");
  const [publicMessage, setPublicMessage] = React.useState("");
  const [feedback, setFeedback] = React.useState("欢迎进入游戏，请点击圆桌席位选择你喜欢的角色");
  const [settingsOpen, setSettingsOpen] = React.useState(false);
  const [speakerSeconds, setSpeakerSeconds] = React.useState(90);
  const [voteSuspect, setVoteSuspect] = React.useState("");
  const [voteReason, setVoteReason] = React.useState("");
  const [voteEvidence, setVoteEvidence] = React.useState<string[]>([]);
  const [voteSubmitted, setVoteSubmitted] = React.useState(false);
  const [agentVoteResults, setAgentVoteResults] = React.useState<Array<{
    role: string;
    killer: string;
    motive?: string;
  }>>([]);
  const [voteTallies, setVoteTallies] = React.useState<Record<string, number>>({});
  const [introSpotlight, setIntroSpotlight] = React.useState<(typeof dynamicPlayers)[number] | null>(null);
  const snapshotRestoredRef = React.useRef<string | null>(null);
  const agentSpeechStartedRef = React.useRef<string | null>(null);
  const AGENT_SPEECH_HANDOFF_MS = 700;

  const clearGameProgress = () => {
    window.localStorage.removeItem(`game-session:${id}`);
    window.localStorage.removeItem(highlightStorageKey);
    window.localStorage.removeItem(`selected-role:${id}`);
    if (sessionId) {
      window.localStorage.removeItem(`game-phase-index:${id}:${sessionId}`);
      window.localStorage.removeItem(`game-introduced:${id}:${sessionId}`);
      window.localStorage.removeItem(`game-cast:${id}:${sessionId}`);
    }
    window.location.reload();
  };

  const [selectedDiscussionEventId, setSelectedDiscussionEventId] = React.useState<number | null>(null);
  const [selectedDetailEvidence, setSelectedDetailEvidence] = React.useState<Evidence | null>(null);
  const [pointTargetId, setPointTargetId] = React.useState("");
  const [pointReason, setPointReason] = React.useState("");
  const [inquiryTargetId, setInquiryTargetId] = React.useState("");
  const [inquiryQuestion, setInquiryQuestion] = React.useState("");
  const [inquiryRecords, setInquiryRecords] = React.useState<InquiryRecord[]>([]);
  const [privateInviteStatus, setPrivateInviteStatus] = React.useState<"未处理" | "稍后处理" | "已接受" | "已拒绝">("未处理");
  const [chatHistoryOpen, setChatHistoryOpen] = React.useState(false);
  const [streaming, setStreaming] = React.useState<StreamingState | null>(null);
  const [scriptChapters, setScriptChapters] = React.useState<Array<{ title: string; content: string }>>([]);
  const [scriptCharacterName, setScriptCharacterName] = React.useState("");
  const [searchEvidencePool, setSearchEvidencePool] = React.useState<Evidence[]>([]);
  const [revealData, setRevealData] = React.useState<{
    killer_confession?: string;
    truth?: string;
    vote_correct?: boolean;
    accused_killer?: string;
  } | null>(null);
  const [spoilerStory, setSpoilerStory] = React.useState("");
  const reflectionSentRef = React.useRef(false);

  // Session 恢复效果（页面刷新后重建 UI 状态，且不降级已推进的前端阶段）
  React.useEffect(() => {
    if (!sessionId) return;
    if (snapshotRestoredRef.current === sessionId) return;
    snapshotRestoredRef.current = sessionId;

    const storageKey = `game-phase-index:${id}:${sessionId}`;
    const savedRaw = window.localStorage.getItem(storageKey);
    const savedIndex = savedRaw !== null ? parseInt(savedRaw, 10) : null;
    if (savedIndex !== null && !Number.isNaN(savedIndex)) {
      setPhaseIndex((prev) => Math.max(prev, savedIndex));
    }

    (async () => {
      try {
        const snapshot = await getGameSnapshot(sessionId);
        if (!snapshot.success) return;

        const restoredIndex = snapshot.frontend_phase_index ?? 0;
        setPhaseIndex((prev) => Math.max(prev, restoredIndex));

        // 恢复剧本内容
        if (restoredIndex >= 1) {
          const charName = snapshot.player_character_name
            || playerById("user")?.role
            || selectedRole;
          loadReadingMaterial(id, sessionId, charName)
            .then(({ chapters, characterLabel }) => {
              if (chapters.length > 0) setScriptChapters(chapters);
              setScriptCharacterName(characterLabel);
            })
            .catch((error) => {
              console.warn("Session 剧本恢复失败:", error);
            });
        }

        // 恢复证物列表
        if (snapshot.evidences && snapshot.evidences.length > 0) {
          const restoredEvidence = snapshot.evidences.map(backendEvidenceToGameEvidence);
          setEvidence(restoredEvidence);
          if (restoredEvidence.length > 0) {
            setSelectedEvidenceId(restoredEvidence[0].id);
          }
        }

        // 恢复角色确认状态
        if (Math.max(restoredIndex, savedIndex ?? 0) >= 2) {
          setRoleConfirmed(true);
        }

        // 恢复投票结果
        if (snapshot.vote_result) {
          setVoteSubmitted(true);
        }

        try {
          const savedIntro = window.localStorage.getItem(`game-introduced:${id}:${sessionId}`);
          if (savedIntro) setIntroduced(JSON.parse(savedIntro));
        } catch {
          // ignore
        }

        if (snapshot.player_character_name && !selectedRole) {
          setSelectedRole(snapshot.player_character_name);
        }

        // 恢复揭示数据
        if (snapshot.reveal_data) {
          setRevealData(snapshot.reveal_data);
        }

        showFeedback("游戏状态已恢复。");
      } catch (error) {
        console.warn("Session 恢复失败:", error);
      }
    })();
  }, [sessionId, id]);

  React.useEffect(() => {
    if (!sessionId) return;
    window.localStorage.setItem(`game-phase-index:${id}:${sessionId}`, String(phaseIndex));
  }, [phaseIndex, sessionId, id]);

  React.useEffect(() => {
    const timer = window.setInterval(() => {
      setSpeakerSeconds((value) => (value > 0 ? value - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [currentSpeaker]);

  React.useEffect(() => {
    if (phase.id !== "discussion" || speakerSeconds > 0 || streaming?.active) return;
    if (currentSpeaker === "user") {
      showFeedback("发言时间到，请尽快结束发言或继续说完。");
    }
  }, [speakerSeconds, phase.id, currentSpeaker, streaming?.active]);

  React.useEffect(() => {
    if (!sessionId) return;
    // 加载已发现的运行时证物
    getEvidences(id, sessionId)
      .then((result) => {
        const records = result.evidences.map(backendEvidenceToGameEvidence);
        setEvidence(records);
        setSelectedEvidenceId((current) => current || records[0]?.id || "");
      })
      .catch((error) => {
        showFeedback(`后端证物加载失败：${error instanceof Error ? error.message : String(error)}`);
      });
    // 加载剧本证物池（初始证物 + 搜证池）
    const dbScriptId = id;
    getEvidencePool(dbScriptId)
      .then((result) => {
        const initialEv: Evidence[] = (result.initial_evidences || []).map((item: Record<string, any>) => ({
          id: item.id,
          name: item.name,
          description: item.description,
          location: item.category || "未知",
          time: "游戏开始",
          source: "初始证物",
          visibility: "仅自己" as const,
          icon: item.category || "card",
        }));
        const searchEv = (result.search_evidences || []).map((item: Record<string, any>) => ({
          id: item.id,
          name: item.name,
          description: item.description,
          location: item.category || "未知",
          time: "搜证阶段",
          source: "随机搜证",
          visibility: "仅自己" as const,
          icon: item.category || "physical",
        }));
        setSearchEvidencePool(searchEv);
        if (initialEv.length > 0 && sessionId) {
          Promise.all(initialEv.map((item) => registerEvidenceInBackend(item).catch(() => undefined)))
            .catch(() => undefined);
        }
        // 初始证物加入玩家证物列表
        if (initialEv.length > 0) {
          setEvidence((prev) => [...initialEv, ...prev]);
          setSelectedEvidenceId((current) => current || initialEv[0]?.id || "");
        }
      })
      .catch((error) => {
        showFeedback(`证物池加载失败：${error instanceof Error ? error.message : String(error)}`);
      });
  }, [id, sessionId]);

  const playerById = (playerId: string | null) => dynamicPlayers.find((item) => item.id === playerId);
  const scriptCharByRole = (role: string) => scriptCharacters.find((character) => character.name === role);
  const resolveAgentKey = (playerId: string | null | undefined) => {
    const player = playerById(playerId || null);
    return player?.agentKey || playerId || "";
  };
  const agents = dynamicPlayers.filter((player) => player.agent && player.id !== "dm");
  const voteableSuspects = dynamicPlayers.filter((player) => {
    if (player.id === "user" || player.id === "dm" || player.role === "侦探") return false;
    const ch = scriptCharByRole(player.role);
    return player.role !== "顾沉" && !ch?.isVictim;
  });
  const firstAgentPlayerId = agents[0]?.id || "";
  const current = playerById(currentSpeaker);
  const isUserSpeaking = currentSpeaker === "user";
  const userQueued = queue.includes("user");
  const nextSpeakerId = queue[0] ?? null;
  const nextSpeaker = playerById(nextSpeakerId);
  const nonDmPlayerIds = dynamicPlayers.filter((p) => p.id !== "dm").map((p) => p.id);
  const introPlayerIds = dynamicPlayers
    .filter((player) => player.id !== "dm" && player.role !== "侦探")
    .map((player) => player.id);
  const currentIntroId = introPlayerIds.find((playerId) => !introduced.includes(playerId));
  const selectedPlayer = playerById(selectedPlayerId);
  const activeThread = privateThreads.find((item) => item.id === activeThreadId);
  const dm = playerById("dm");

  React.useEffect(() => {
    if (!targetId && firstAgentPlayerId) setTargetId(firstAgentPlayerId);
    if (!pointTargetId && firstAgentPlayerId) setPointTargetId(firstAgentPlayerId);
    if (!inquiryTargetId && firstAgentPlayerId) setInquiryTargetId(firstAgentPlayerId);
  }, [firstAgentPlayerId, targetId, pointTargetId, inquiryTargetId]);

  React.useEffect(() => {
    if (phase.id !== "review" || !sessionId || reflectionSentRef.current) return;
    reflectionSentRef.current = true;
    postGameReflection(sessionId, {
      vote_correct: revealData?.vote_correct,
      accused_killer: revealData?.accused_killer || voteSuspect,
      killer_confession: revealData?.killer_confession,
      truth: revealData?.truth,
    }).catch(() => undefined);
  }, [phase.id, sessionId, revealData, voteSuspect]);

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

  const getPublicSpeakerLabel = () => {
    const self = playerById("user");
    if (!self || self.role === "侦探") return "林晓青";
    return self.role;
  };

  const registerEvidenceInBackend = async (item: Evidence) => {
    if (!sessionId) return;
    await createEvidence({
      id: item.id,
      scriptId: id,
      sessionId,
      name: item.name,
      basicDescription: item.description,
      category: item.location || "physical",
      discoveredBy: "player",
    });
  };

  // ============================
  // AI 流式调用辅助
  // ============================

  const agentPlayerByRole = (role: string) => dynamicPlayers.find((p) => p.role === role);

  const buildActorFromPlayer = (player: typeof dynamicPlayers[number]): Actor => {
    const ch = scriptCharByRole(player.role);
    return {
      id: player.id,
      name: player.role,
      bio: ch?.bio || player.background,
      personality: ch?.personality || "",
      context: ch?.context || "",
      secret: ch?.secret || "",
      violation: ch?.violation || "",
      isVictim: Boolean(ch?.isVictim),
      isKiller: false,
      isAssistant: false,
      isPlayer: !player.agent,
      isPartner: false,
      roleType: player.agent ? "companion" : "suspect",
    };
  };

  const buildSafeActors = (): SafeActor[] =>
    dynamicPlayers.filter((p) => p.id !== "dm" && p.id !== "user").map((p) => {
      const ch = scriptCharByRole(p.role);
      return {
        id: p.id,
        name: p.role,
        bio: ch?.bio || p.background,
        personality: ch?.personality || "",
        context: ch?.context || "",
        isVictim: Boolean(ch?.isVictim),
        isKiller: false,
        isAssistant: false,
        isPlayer: !p.agent,
        isPartner: false,
        roleType: p.agent ? "companion" : "suspect",
      };
    });

  const streamAgentSpeech = (
    targetPlayerId: string,
    userMessage: string,
    onToken: (token: string) => void,
    onDone: (final: string) => void,
    onError?: (error: Error) => void,
  ) => {
    const player = playerById(targetPlayerId);
    if (!player || !sessionId) return;

    const chatMessages = [{ role: "user" as const, content: userMessage }];
    if (queue.includes("user") || currentSpeaker === "user") {
      // 如果玩家在发言队列中，注入讨论上下文
    }

    const req: InvocationRequest = {
      globalStory: `剧名：${scriptTitle}。当前游戏阶段：${phase.label}(${phase.shortLabel})。`,
      actor: buildActorFromPlayer(player),
      sessionId,
      detectiveName: "林晓青",
      victimName: "未知",
      allActors: buildSafeActors(),
      chatMessages,
      temperature: 0.8,
    };

    invokeAIStream(req, onToken, (final) => {
      onDone(final);
      if (sessionId) recordChatCount(sessionId).catch(() => undefined);
    }, (error) => {
      showFeedback(`AI 回复失败：${error.message}`);
      onError?.(error);
    });
  };

  const updateEventText = (eventId: number, newText: string) => {
    setEvents((items) =>
      items.map((item) =>
        item.id === eventId && item.type === "speech"
          ? { ...item, text: newText }
          : item,
      ),
    );
  };

  const hasHumanSuspectSeat = castAssignments.some((item) => item.assignee === HUMAN_PLAYER);

  const confirmRoleSelection = async () => {
    if (!allSeatsFilled) {
      showFeedback("请为所有席位分配 Agent 或真人玩家后再确认阵容。");
      return;
    }
    if (hasHumanSuspectSeat && !selectedRole) {
      showFeedback("请先在圆桌中选择你要扮演的嫌疑人角色。");
      return;
    }
    const playerCharName = hasHumanSuspectSeat
      ? (castingRoles.find((role) => role.id === selectedRole)?.role || playerById("user")?.role || "")
      : "";
    try {
      let activeSessionId = sessionId;
      if (activeSessionId) {
        await getGamePhase(activeSessionId);
      } else {
        const session = await createGameSession(id, `剧本游戏：${scriptTitle}`, playerCharName);
        activeSessionId = session.sessionId;
        setSessionId(activeSessionId);
        window.localStorage.setItem(`game-session:${id}`, activeSessionId);
        window.localStorage.setItem(`selected-role:${id}`, selectedRole);
      }
      setRoleConfirmed(true);
      setPhaseIndex(1);
      window.localStorage.setItem(`game-cast:${id}`, JSON.stringify({
        selectedRole,
        castAssignments,
      }));
      const castPayload = buildCastPayload(castingRoles, castAssignments);
      let confirmMessage = `角色已确认，后端游戏会话 ${activeSessionId} 可用。`;
      try {
        await applyGameCast(activeSessionId, castPayload, playerCharName);
      } catch (castError) {
        console.warn("选角同步失败:", castError);
        confirmMessage = `角色已确认，但选角同步失败：${castError instanceof Error ? castError.message : String(castError)}`;
      }
      showFeedback(confirmMessage);
      // 加载阅读材料（嫌疑人私人本 / 侦探 globalStory）
      try {
        const { chapters, characterLabel } = await loadReadingMaterial(
          id,
          activeSessionId,
          playerCharName || (hasHumanSuspectSeat ? "" : "侦探"),
        );
        if (chapters.length > 0) {
          setScriptChapters(chapters);
          setChapter(0);
        } else {
          showFeedback("后端未返回章节数据，请检查数据库配置。");
        }
        setScriptCharacterName(characterLabel);
      } catch (scriptErr) {
        console.error("Script load error:", scriptErr);
        showFeedback("剧本加载失败，将使用默认剧本。");
      }
    } catch (error) {
      showFeedback(`无法确认角色：后端游戏会话创建或恢复失败：${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const backendPhaseForIndex = (index: number) => {
    if (index <= 2) return "intro";
    if (index <= 4) return "investigation";
    if (index === 5) return "voting";
    if (index === 6) return "reveal";
    return "review";
  };

  const goToPhase = async (index: number) => {
    if (streaming?.active) {
      showFeedback("AI 正在发言，请稍候再切换阶段。");
      return;
    }
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
    if (sessionId) {
      window.localStorage.setItem(`game-phase-index:${id}:${sessionId}`, String(index));
    }
    try {
      await forceGamePhase(sessionId, backendPhaseForIndex(index), index);
    } catch (error) {
      showFeedback(`后端阶段切换失败：${error instanceof Error ? error.message : String(error)}`);
      return;
    }
    setPhaseIndex(index);
    setSpeakerSeconds(90);
    agentSpeechStartedRef.current = null;
    if (GAME_PHASES[index].id === "discussion") {
      initDiscussionQueue();
    }
  };

  const initDiscussionQueue = (preserveUserQueue = false) => {
    const agentIds = discussionAgentIds;
    const userWaiting = preserveUserQueue ? queue.filter((item) => item === "user") : [];
    setDiscussionRoundIdle(agentIds.length === 0 && userWaiting.length === 0);
    setCurrentSpeaker(agentIds[0] ?? null);
    setQueue([...agentIds.slice(1), ...userWaiting]);
    agentSpeechStartedRef.current = null;
  };

  const startNextDiscussionRound = () => {
    if (streaming?.active) {
      showFeedback("AI 正在发言，请稍候。");
      return;
    }
    if (discussionAgentIds.length === 0) {
      showFeedback("当前没有可发言的 Agent。");
      return;
    }
    initDiscussionQueue(true);
    showFeedback("新一轮讨论开始，Agent 将按角色顺序依次发言。");
  };

  const advancePhase = () => {
    if (phase.id === "role-selection" && !roleConfirmed) return showFeedback("请先确认角色。");
    if (phase.id === "script-reading" && !readingDone) return showFeedback("请阅读全部章节并确认完成。");
    if (phase.id === "intro" && introduced.length < introPlayerIds.length) return showFeedback("仍有角色尚未完成自我介绍。");
    if (phase.id === "search" && searchesLeft > 0) return showFeedback("请使用完本阶段的搜证次数。");
    if (phaseIndex < GAME_PHASES.length - 1) goToPhase(phaseIndex + 1);
  };

  const joinQueue = () => {
    if (phase.id === "vote") return showFeedback("投票阶段已经停止新的发言申请。");
    if (forcedAnswer) return showFeedback("当前为强制回答，其他角色暂时不可插队。");
    if (userQueued || isUserSpeaking) return;
    setDiscussionRoundIdle(false);
    if (!currentSpeaker && !streaming?.active) {
      setCurrentSpeaker("user");
      setSpeakerSeconds(90);
      showFeedback("轮到你发言了，请在下方输入内容。");
      return;
    }
    setQueue((items) => {
      const next = [...items, "user"];
      const position = (currentSpeaker ? 1 : 0) + next.length;
      showFeedback(`已进入发言队列，当前排队第 ${position} 位。`);
      return next;
    });
  };

  const cancelQueue = () => {
    setQueue((items) => items.filter((item) => item !== "user"));
    showFeedback("已取消发言申请。");
  };

  const advanceSpeakerQueue = (finishedSpeakerId: string) => {
    agentSpeechStartedRef.current = null;
    setQueue((items) => {
      const waiting = items.filter((item) => item !== finishedSpeakerId);
      const nextSpeaker = waiting[0] ?? null;
      setCurrentSpeaker(nextSpeaker);
      if (!nextSpeaker) {
        setDiscussionRoundIdle(true);
        showFeedback("本轮发言顺序已结束，你可以申请发言或开启下一轮讨论。");
      } else if (nextSpeaker === "user") {
        showFeedback("轮到你发言了，请在下方输入内容或结束发言。");
      }
      return nextSpeaker ? waiting.slice(1) : waiting;
    });
    setSpeakerSeconds(90);
  };

  const startAgentDiscussionSpeech = (
    speakerId: string,
    onComplete?: () => void,
    promptOverride?: string,
  ) => {
    const agentPlayer = playerById(speakerId);
    if (!agentPlayer || !sessionId) {
      onComplete?.();
      return;
    }

    const eventId = Date.now();
    const recentDiscussion = events
      .filter((e): e is Extract<PublicEvent, { type: "speech" | "evidence" }> =>
        e.type === "speech" || e.type === "evidence",
      )
      .slice(-5)
      .map((e) =>
        e.type === "speech"
          ? `${e.speaker}：${e.text}`
          : `${e.speaker} 出示了证物【${e.evidence.name}】`,
      )
      .join("\n");

    setEvents((items) => [
      ...items,
      {
        id: eventId,
        type: "speech",
        speaker: `${agentPlayer.name} Agent`,
        text: "（正在思考…）",
        tone: agentPlayer.color || "blue",
      } as PublicEvent,
    ]);
    setStreaming({
      active: true,
      agentKey: speakerId,
      agentName: agentPlayer.name,
      partial: "",
      phase: "speech",
      resolveId: eventId,
    });

    streamAgentSpeech(
      speakerId,
      promptOverride
        || `最近讨论内容：\n${recentDiscussion || "（讨论刚开始）"}\n\n请根据当前讨论，以你的角色身份和已有信息发表看法。你可以：(1)回应其他人的话题 (2)提出新线索方向 (3)对其他角色的发言表示质疑。不要泄露你的角色秘密。`,
      (token) => {
        setStreaming((prev) => {
          if (!prev) return null;
          const updated = prev.partial + token;
          updateEventText(eventId, updated);
          return { ...prev, partial: updated };
        });
      },
      (final) => {
        setStreaming(null);
        updateEventText(eventId, final);
        onComplete?.();
      },
      () => {
        setStreaming(null);
        updateEventText(eventId, "（AI 发言失败，已跳过）");
        onComplete?.();
      },
    );
  };

  const finishSpeaker = () => {
    if (streaming?.active) {
      showFeedback("AI 正在发言，请稍候。");
      return;
    }
    if (!currentSpeaker) return;

    if (currentSpeaker !== "user") {
      const agentPlayer = playerById(currentSpeaker);
      if (agentPlayer?.agent) {
        advanceSpeakerQueue(currentSpeaker);
        return;
      }
    }

    advanceSpeakerQueue(currentSpeaker);
  };

  React.useEffect(() => {
    if (phase.id !== "discussion") return;
    if (!currentSpeaker || streaming?.active) return;

    const speakerPlayer = playerById(currentSpeaker);
    if (!speakerPlayer?.agent) return;
    if (agentSpeechStartedRef.current === currentSpeaker) return;

    const speakerId = currentSpeaker;
    const pendingForced = forcedAnswer?.agentId === speakerId ? forcedAnswer : null;
    if (forcedAnswer && !pendingForced) return;

    agentSpeechStartedRef.current = speakerId;
    const forcedQuestion = pendingForced?.question;
    if (pendingForced) {
      setForcedAnswer(null);
    }

    const timer = window.setTimeout(() => {
      startAgentDiscussionSpeech(
        speakerId,
        () => advanceSpeakerQueue(speakerId),
        pendingForced
          ? `你被指定回答以下问题："${forcedQuestion}"\n请根据你的角色身份和已知信息回答。注意：不能泄露角色秘密，但可以根据已有线索进行推理。`
          : undefined,
      );
    }, AGENT_SPEECH_HANDOFF_MS);

    return () => window.clearTimeout(timer);
  }, [phase.id, currentSpeaker, streaming?.active, forcedAnswer]);

  const completeIntro = () => {
    if (!currentIntroId) return;
    const introPlayer = playerById(currentIntroId);
    if (!introPlayer) return;
    setIntroduced((items) => {
      const next = [...items, currentIntroId];
      if (sessionId) {
        window.localStorage.setItem(`game-introduced:${id}:${sessionId}`, JSON.stringify(next));
      }
      return next;
    });

    if (introPlayer.agent && sessionId) {
      // Agent → 使用 AI 流式生成介绍
      const eventId = Date.now();
      setEvents((items) => [
        ...items,
        {
          id: eventId,
          type: "speech",
          speaker: introPlayer.name,
          text: "（思考中…）",
          tone: introPlayer.color || "gray",
        } as PublicEvent,
      ]);
      setIntroSpotlight(introPlayer);
      setStreaming({
        active: true,
        agentKey: introPlayer.id,
        agentName: introPlayer.name,
        partial: "",
        phase: "intro",
        resolveId: eventId,
      });
      streamAgentSpeech(
        introPlayer.id,
        `请以角色身份做自我介绍。你的角色是"${introPlayer.role}"，${introPlayer.publicIdentity}。背景：${introPlayer.background}。`,
        (token) => {
          setStreaming((prev) => {
            if (!prev) return null;
            const updated = prev.partial + token;
            updateEventText(eventId, updated);
            return { ...prev, partial: updated };
          });
        },
        (final) => {
          setStreaming(null);
          updateEventText(eventId, final);
          showFeedback(`${introPlayer.name} 已完成自我介绍。`);
        },
      );
    } else {
      // 真人玩家 → 使用硬编码台词（优先按角色名查找，兼容动态角色选择）
      const resolvedRoleKey = ROLE_TO_INTRO_KEY[resolveRoleName(introPlayer.role)] || introPlayer.role;
      const introText = INTRO_LINES[resolvedRoleKey] || INTRO_LINES[introPlayer.role] || INTRO_LINES[currentIntroId] || `我是${introPlayer.role}，${introPlayer.publicIdentity}。`;
      addEvent({
        type: "speech",
        speaker: introPlayer.name,
        text: introText,
        tone: introPlayer.color || "gray",
      });
      setIntroSpotlight(introPlayer);
      showFeedback(`${introPlayer.name} 已完成自我介绍。`);
    }
  };

  const randomSearch = async () => {
    if (searchesLeft <= 0) return;
    if (!sessionId) return showFeedback("搜证失败：尚未创建后端游戏会话。");
    if (searchEvidencePool.length === 0) {
      return showFeedback("搜证池为空，请确认后端证物池已加载（需重启 API）。");
    }

    const available = searchEvidencePool.filter((item) => !evidence.some((owned) => owned.id === item.id));
    if (available.length === 0) {
      showFeedback("本区域所有线索已搜寻完毕。");
      return;
    }

    const found = available[Math.floor(Math.random() * available.length)];

    try {
      const result = await discoverEvidence({
        scriptId: id || "xiutie-avenue-missing-three-minutes",
        sessionId,
        scriptEvidenceId: found.id,
        discoveredBy: "player",
      });

      const saved = result.evidence ? backendEvidenceToGameEvidence(result.evidence) : found;
      setEvidence((items) => (items.some((item) => item.id === saved.id) ? items : [...items, saved]));
      setSelectedEvidenceId(saved.id);
      setNewEvidence(saved);
      setSearchesLeft((value) => value - 1);
      showFeedback(`搜证成功！你发现了：${saved.name}`);
    } catch (error) {
      console.error("Search API Error:", error);
      showFeedback(`搜证失败：${error instanceof Error ? error.message : "无法同步到后端记录"}`);
    }
  };

  const confirmForcedAnswer = () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能指定 Agent 回答。");
    const agent = playerById(targetId);
    if (!question.trim() || !agent) return showFeedback("请选择 Agent 并填写问题。");
    setForcedAnswer({ asker: "林晓青", agentId: targetId, question });
    setDiscussionRoundIdle(false);
    setQueue((items) => [targetId, ...items.filter((item) => item !== targetId && item !== currentSpeaker)]);
    addEvent({ type: "forced", asker: "林晓青", agent: agent.name, question });
    setDialog(null);
    setQuestion("");
    showFeedback(`${agent.name} 已被指定为下一位发言者，其他角色不可插队。`);
  };

  const showEvidence = async () => {
    if (!isUserSpeaking) return showFeedback("只有在自己发言时才能出示证物。");
    if (!sessionId) return showFeedback("出示证物失败：尚未创建后端游戏会话。");
    if (evidence.length === 0) return showFeedback("当前没有可出示的证物，请先完成搜证。");
    const item = evidence.find((entry) => entry.id === selectedEvidenceId);
    if (!item) return showFeedback("请选择要出示的证物。");
    const reason = evidenceReason.trim();
    const targetPlayer = evidenceVisibility === "指定角色" ? playerById(targetId) : undefined;
    if (evidenceVisibility === "指定角色" && !targetPlayer) {
      return showFeedback("请选择要出示证物的目标角色。");
    }
    const presentedTo = targetPlayer ? targetPlayer.role : "所有人";
    const speakerLabel = getPublicSpeakerLabel();
    const targetName = targetPlayer
      ? `${targetPlayer.role} · ${targetPlayer.name}`
      : "所有人";
    try {
      await registerEvidenceInBackend(item);
      const result = await presentEvidence(
        item.id,
        presentedTo,
        "player",
        reason,
        evidenceVisibility,
      );
      setEvidence((items) => items.map((entry) => entry.id === item.id ? { ...entry, visibility: evidenceVisibility as Evidence["visibility"] } : entry));
      addEvent({
        type: "evidence",
        speaker: speakerLabel,
        evidence: { ...item, visibility: evidenceVisibility as Evidence["visibility"] },
        reason: reason || undefined,
        aiResponse: result.aiResponse || undefined,
        targetName,
      });
      setDialog(null);
      setEvidenceReason("");
      showFeedback(
        result.aiResponse
          ? `已向${targetName}出示「${item.name}」，对方已做出反应。`
          : `已向${targetName}出示「${item.name}」。`,
      );
    } catch (error) {
      showFeedback(`后端出示证物失败：${error instanceof Error ? error.message : String(error)}`);
    }
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
    const speakerLabel = getPublicSpeakerLabel();
    try {
      await saveConversation({
        sessionId,
        actorName: speakerLabel,
        chatMessages: [{ role: "user", content }],
        finalResponse: content,
      });
      addEvent({ type: "speech", speaker: speakerLabel, text: content, tone: "orange" });
      setPublicMessage("");
      showFeedback("公开发言已记录。");
    } catch (error) {
      showFeedback(`发言发送失败：${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const appendPrivateThreadMessage = (threadId: string, line: string) => {
    setPrivateThreads((threads) => threads.map((thread) =>
      thread.id === threadId ? { ...thread, messages: [...thread.messages, line] } : thread,
    ));
  };

  const updatePrivateThreadLastMessage = (threadId: string, updater: (prev: string) => string) => {
    setPrivateThreads((threads) => threads.map((thread) => {
      if (thread.id !== threadId || thread.messages.length === 0) return thread;
      const messages = [...thread.messages];
      messages[messages.length - 1] = updater(messages[messages.length - 1]);
      return { ...thread, messages };
    }));
  };

  const sendPrivateMessage = async () => {
    if (!privateMessage.trim() || !activeThread) return;
    if (!sessionId) return showFeedback("发送失败：尚未创建后端游戏会话。");
    const content = privateMessage.trim();
    const threadId = activeThread.id;
    const targetPlayer = playerById(activeThread.playerId);
    if (!targetPlayer) return;

    setPrivateMessage("");
    appendPrivateThreadMessage(threadId, `我：${content}`);

    try {
      await sendPrivateChatMessage(sessionId, "player", resolveAgentKey(activeThread.playerId), content);
    } catch (error) {
      showFeedback(`私聊同步失败：${error instanceof Error ? error.message : String(error)}`);
    }

    if (!targetPlayer.agent) {
      await saveConversation({
        sessionId,
        actorName: "林晓青",
        chatMessages: [{ role: "user", content: `[私聊→${targetPlayer.name}] ${content}` }],
        finalResponse: content,
      }).catch(() => undefined);
      return;
    }

    const replyPrefix = `${targetPlayer.name}：`;
    appendPrivateThreadMessage(threadId, `${replyPrefix}（正在思考…）`);

    const chatMessages: LLMMessage[] = [{
      role: "user",
      content: `玩家私聊对你说："${content}"\n（这是私聊，公共讨论听不到。请以角色身份自然回复，不要泄露角色秘密，可以回避或转移话题。）`,
    }];

    const req: InvocationRequest = {
      globalStory: `剧名：${scriptTitle}。当前阶段：${phase.label}。`,
      actor: buildActorFromPlayer(targetPlayer),
      sessionId,
      detectiveName: "林晓青",
      victimName: "未知",
      allActors: buildSafeActors(),
      chatMessages,
      temperature: 0.8,
    };

    let accumulated = "";
    invokeAIStream(
      req,
      (token) => {
        accumulated += token;
        updatePrivateThreadLastMessage(threadId, () => `${replyPrefix}${accumulated}`);
      },
      async (final) => {
        updatePrivateThreadLastMessage(threadId, () => `${replyPrefix}${final}`);
        try {
          await sendPrivateChatMessage(sessionId, resolveAgentKey(activeThread.playerId), "player", final);
        } catch {
          // 回复已展示，同步失败不阻塞
        }
        await saveConversation({
          sessionId,
          actorName: targetPlayer.role,
          chatMessages,
          finalResponse: final,
        }).catch(() => undefined);
      },
      (error) => {
        showFeedback(`AI 私聊回复失败：${error.message}`);
        updatePrivateThreadLastMessage(threadId, () => `${replyPrefix}（暂时无法回复，请稍后再试。）`);
      },
    );
  };

  const submitVote = async () => {
    if (!voteSuspect || !voteReason.trim() || voteEvidence.length === 0) {
      return showFeedback("请选择嫌疑人、填写推理理由并勾选至少一件关键证物。");
    }
    if (!sessionId) return showFeedback("投票失败：尚未创建后端游戏会话。");
    try {
      await forceGamePhase(sessionId, "voting", 5);
      const result = await submitGameVote(sessionId, voteSuspect, voteReason);
      setVoteSubmitted(true);
      showFeedback(result.message || "你的投票已提交。");

      try {
        const agentResult = await submitAgentVotes(sessionId);
        if (agentResult.agent_votes) {
          setAgentVoteResults(
            agentResult.agent_votes.map((item: Record<string, string>) => ({
              role: item.role,
              killer: item.killer,
              motive: item.motive,
            })),
          );
        }
        if (agentResult.tallies) {
          setVoteTallies(agentResult.tallies as Record<string, number>);
        }
      } catch (agentError) {
        showFeedback(`Agent 投票失败：${agentError instanceof Error ? agentError.message : String(agentError)}`);
      }

      try {
        const advanceResult = await advanceGamePhase(sessionId);
        if (advanceResult.reveal) {
          setRevealData(advanceResult.reveal);
        }
        setPhaseIndex(GAME_PHASES.findIndex((p) => p.id === "reveal"));
        showFeedback("真相即将揭晓...");
      } catch {
        try {
          const revealResult = await revealGame(sessionId, {
            killer: voteSuspect,
            motive: voteReason,
            voter: "player",
            correct: result.is_correct,
            script_type: id,
          });
          setRevealData(revealResult);
          setPhaseIndex(GAME_PHASES.findIndex((p) => p.id === "reveal"));
        } catch (revealError) {
          showFeedback(`真相揭示失败：${revealError instanceof Error ? revealError.message : String(revealError)}`);
        }
      }
      try {
        const spoilerResult = await generateSpoiler(sessionId, {
          killer: voteSuspect,
          motive: voteReason,
          voter: "player",
          correct: result.is_correct,
        });
        if (spoilerResult.story) {
          setSpoilerStory(spoilerResult.story);
        }
      } catch {
        // optional
      }
    } catch (error) {
      showFeedback(`后端投票失败：${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const playerStatus = (playerId: string) => {
    if (currentSpeaker === playerId) return "正在发言";
    const queueIndex = queue.indexOf(playerId);
    if (queueIndex >= 0) {
      const position = (currentSpeaker ? 1 : 0) + queueIndex + 1;
      return `排队第 ${position} 位`;
    }
    if (phase.id === "discussion" && discussionRoundIdle) return "可发言";
    return "旁观中";
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
    setPointTargetId(firstAgentPlayerId);
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
    setInquiryTargetId(firstAgentPlayerId);
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
    const recordId = Date.now();

    if (target.agent && sessionId) {
      // Agent 质询 → AI 流式生成回答
      const eventId = Date.now();
      setEvents((items) => [
        ...items,
        {
          id: eventId,
          type: "inquiry",
          asker: "林晓青",
          target: `${target.role} · ${target.name}`,
          sourceTitle,
          question: inquiryQuestion.trim(),
          answer: "（正在思考…）",
        } as PublicEvent,
      ]);

      const chatMessages: LLMMessage[] = [
        { role: "user", content: `玩家对你说："${inquiryQuestion.trim()}"（背景：对方正在质询你关于「${sourceTitle}」的内容。请以角色身份回答，不要泄露秘密，可以回避或转移话题。）` },
      ];

      const req: InvocationRequest = {
        globalStory: `剧名：${scriptTitle}。当前阶段：线索交流。`,
        actor: buildActorFromPlayer(target),
        sessionId,
        detectiveName: "林晓青",
        victimName: "未知",
        allActors: buildSafeActors(),
        chatMessages,
        temperature: 0.7,
      };

      invokeAIStream(
        req,
        (token) => {
          setEvents((items) =>
            items.map((item) =>
              item.id === eventId && item.type === "inquiry"
                ? { ...item, answer: item.answer === "（正在思考…）" ? token : item.answer + token }
                : item,
            ),
          );
        },
        (final) => {
          const record: InquiryRecord = {
            id: recordId,
            sourceEventId: source.id,
            sourceType: source.type === "evidence" ? "证据" : "关键发言",
            sourceTitle,
            evidence: source.type === "evidence" ? source.evidence : undefined,
            targetId: target.id,
            targetName: `${target.role} · ${target.name}`,
            question: inquiryQuestion.trim(),
            answer: final,
          };
          setInquiryRecords((items) => [...items, record]);
          setEvents((items) =>
            items.map((item) =>
              item.id === eventId && item.type === "inquiry"
                ? { ...item, answer: final }
                : item,
            ),
          );
        },
        (error) => {
          showFeedback(`AI 质询回复失败：${error.message}`);
          const fallbackAnswer = source.type === "evidence"
            ? `我检查过“${source.evidence.name}”的来源。它能证明时间和地点存在关联，但还不能单独证明持有人身份。`
            : `关于这段发言，我的判断是其中有一处时间顺序需要复核。我愿意把相关行动记录公开出来接受比对。`;
          setEvents((items) =>
            items.map((item) =>
              item.id === eventId && item.type === "inquiry"
                ? { ...item, answer: fallbackAnswer }
                : item,
            ),
          );
        },
      );
    } else {
      // 真人质询 → 硬编码回答
      const answer = source.type === "evidence"
        ? `我检查过“${source.evidence.name}”的来源。它能证明时间和地点存在关联，但还不能单独证明持有人身份。`
        : `关于这段发言，我的判断是其中有一处时间顺序需要复核。我愿意把相关行动记录公开出来接受比对。`;
      const record: InquiryRecord = {
        id: recordId,
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
    }

    setRightTab("chat");
    setDialog(null);
    setInquiryQuestion("");
    showFeedback(`已完成对 ${target.role} 的质询，记录已保存到证物栏。`);
  };

  const selectedDiscussionSource = discussionSource(selectedDiscussionEventId);
  const selectedDiscussionSpeaker = selectedDiscussionSource
    ? dynamicPlayers.find((player) =>
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
              const speakerPlayer = dynamicPlayers.find((p) =>
                p.name === event.speaker ||
                `${p.name} Agent` === event.speaker ||
                p.role === event.speaker ||
                event.speaker.includes(p.name)
              );
              const speakerPortrait = speakerPlayer ? getRolePortrait(speakerPlayer.role) : getRolePortrait(event.speaker);
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
          {event.targetName && <Text size="xs" c="dimmed" mt={6}>出示对象：{event.targetName}</Text>}
          {event.aiResponse && (
            <Paper p="sm" radius="md" mt="sm" className="game-evidence-reaction">
              <Text size="xs" c="blue.3" fw={700}>角色反应</Text>
              <Text size="sm" mt={4} lh={1.65}>{event.aiResponse}</Text>
            </Paper>
          )}
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
            roles={castingRoles}
            availableAgents={availableAgents}
            selectedPlayerRoleId={selectedRole}
            onPlayerRoleChange={(id) => setSelectedRole(id)}
            onEnsembleChange={setAllSeatsFilled}
            onCastChange={setCastAssignments}
          />
          <Button
            radius="xl"
            disabled={!allSeatsFilled || (hasHumanSuspectSeat && !selectedRole)}
            onClick={confirmRoleSelection}
          >
            {!allSeatsFilled
              ? "请为所有席位分配 Agent"
              : hasHumanSuspectSeat && !selectedRole
                ? "请先在圆桌中选择自己扮演的角色"
                : "确认阵容并进入剧本"}
          </Button>
        </Stack>
      );
    }
    if (phase.id === "script-reading") {
      const item = scriptChapters[chapter];
      if (!item) {
        return (
          <Stack gap="md" align="center">
            <Text c="dimmed">剧本数据加载中...</Text>
          </Stack>
        );
      }
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
            <Text size="sm" c="dimmed">{chapter + 1} / {scriptChapters.length}</Text>
            {chapter < scriptChapters.length - 1
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
            <Group justify="space-between"><Box><Text size="xs" c="dimmed">当前自我介绍</Text><Title order={3}>{introPlayer?.name || "全部完成"} · {introPlayer?.role}</Title></Box><Badge color="orange">{introduced.length} / {introPlayerIds.length} 已完成</Badge></Group>
            {introPlayer && <Text mt="md" c="dimmed">本阶段仅允许自我介绍和指定 Agent 自我介绍，不可出示证物、搜证或深入私聊。</Text>}
          </Paper>
          <Stack gap="xs">{events.filter((event) => event.type === "speech").map(renderEvent)}</Stack>
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
            <Paper radius="xl" p="xl" className="game-vote-success">
              <IconCheck size={44} />
              <Title order={2} mt="md">投票已提交</Title>
              <Text c="dimmed" mt="sm">你的判断：{voteSuspect} · {voteReason}</Text>
              {Object.keys(voteTallies).length > 0 && (
                <Stack gap="xs" mt="md">
                  <Text fw={700}>投票统计</Text>
                  {Object.entries(voteTallies).map(([name, count]) => (
                    <Text key={name} size="sm">{name}：{count} 票</Text>
                  ))}
                </Stack>
              )}
              {agentVoteResults.length > 0 && (
                <Stack gap="xs" mt="md">
                  <Text fw={700}>Agent 投票</Text>
                  {agentVoteResults.map((item) => (
                    <Text key={item.role} size="sm">
                      {item.role} → {item.killer}
                      {item.motive ? `（${item.motive}）` : ""}
                    </Text>
                  ))}
                </Stack>
              )}
            </Paper>
          ) : (
            <Paper radius="xl" p="lg" className="game-vote-form">
              <Text fw={700}>选择嫌疑人</Text>
              <Radio.Group value={voteSuspect} onChange={setVoteSuspect}>
                <Box className="game-suspect-grid" mt="xs">
                  {voteableSuspects.map((player) => (
                    <Paper
                      key={player.id}
                      component="label"
                      radius="lg"
                      p="sm"
                      className={voteSuspect === player.role ? "game-suspect-option is-selected" : "game-suspect-option"}
                    >
                      <Group wrap="nowrap">
                        {(() => { const portrait = player.agent ? getAgentPortrait(player.name) : getRolePortrait(player.role); return portrait ? <Avatar src={portrait} size={40} radius="xl" imageProps={{ style: { objectPosition: "top" } }} /> : <Avatar color={player.color}>{player.role.slice(0, 1)}</Avatar>; })()}
                        <Box style={{ flex: 1 }}>
                          <Text fw={900}>{player.role}</Text>
                          <Text size="xs" c="dimmed">{player.name}</Text>
                        </Box>
                        <Radio value={player.role} aria-label={`选择 ${player.role}`} />
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
    if (phase.id === "reveal") {
      return (
        <Stack gap="md" align="center">
          <Paper radius="xl" p="xl" className="game-reveal-stage">
            <Title order={2}>真相揭示</Title>
            {revealData ? (
              <>
                <Badge color={revealData.vote_correct ? "teal" : "red"} mt="md" size="lg">
                  {revealData.vote_correct ? "推理正确！" : "推理有误"}
                </Badge>
                {revealData.accused_killer && (
                  <Text size="sm" c="dimmed" mt="sm">
                    你指认的凶手：{revealData.accused_killer}
                  </Text>
                )}
                {revealData.killer_confession && (
                  <>
                    <Divider mt="lg" />
                    <Title order={3} mt="lg">凶手交代</Title>
                    <Text lh={1.8} mt="sm">{revealData.killer_confession}</Text>
                  </>
                )}
                {revealData.truth && (
                  <>
                    <Divider mt="lg" />
                    <Title order={3} mt="lg">DM 真相揭晓</Title>
                    <Text lh={1.8} mt="sm">{revealData.truth}</Text>
                  </>
                )}
                {spoilerStory && (
                  <>
                    <Divider mt="lg" />
                    <Title order={3} mt="lg">完整剧情回顾</Title>
                    <Text lh={1.8} mt="sm" style={{ whiteSpace: "pre-wrap" }}>{spoilerStory}</Text>
                  </>
                )}
              </>
            ) : (
              <Text c="dimmed" mt="md">真相数据加载中...</Text>
            )}
          </Paper>
          <Group mt="md">
            <Button
              radius="xl"
              onClick={() => goToPhase(GAME_PHASES.findIndex((p) => p.id === "review"))}
            >
              进入复盘反思
            </Button>
            <Button
              radius="xl"
              variant="light"
              onClick={() => navigate(buildReviewPath(id, sessionId))}
            >
              打开复盘看板
            </Button>
          </Group>
        </Stack>
      );
    }
    if (phase.id === "review") {
      return (
        <Stack gap="md" align="center">
          <Paper radius="xl" p="xl" className="game-review-stage">
            <Title order={2}>复盘反思</Title>
            <Text c="dimmed" mt="sm">游戏已结束，感谢参与。</Text>
            {revealData && (
              <Text lh={1.8} mt="md">
                {revealData.vote_correct
                  ? "恭喜你成功推理出了真凶！"
                  : `真凶并非你指认的${revealData.accused_killer || "嫌疑人"}。下次再加油吧！`}
              </Text>
            )}
          </Paper>
          <Group>
            <Button
              radius="xl"
              onClick={() => navigate(buildReviewPath(id, sessionId))}
            >
              查看完整复盘看板
            </Button>
            <Button
              radius="xl"
              variant="light"
              onClick={() => navigate("/games")}
            >
              返回游戏列表
            </Button>
          </Group>
        </Stack>
      );
    }
    return (
      <Stack gap="md">
        <Paper radius="xl" p="md" className={forcedAnswer ? "game-speaker-control is-forced" : "game-speaker-control"}>
          <Group justify="space-between" align="flex-start">
            <Box><Text size="xs" c="dimmed">{forcedAnswer ? "强制回答中" : current ? "当前发言人" : discussionRoundIdle ? "等待下一轮" : "当前暂无角色发言"}</Text><Title order={3}>{current ? `${current.name} · ${current.role}` : discussionRoundIdle ? "本轮顺序已结束" : `下一位：${nextSpeaker?.name || "等待申请"}`}</Title>{forcedAnswer && <Text size="sm" mt={5}>问题：{forcedAnswer.question}</Text>}</Box>
            <Stack gap={4} align="flex-end"><Badge color={forcedAnswer ? "red" : "orange"} leftSection={<IconClock size={13} />}>{formatTime(speakerSeconds)}</Badge><Text size="xs" c="dimmed">{queue.length > 0 ? `待发：${[nextSpeaker?.name, ...queue.slice(1).map((item) => playerById(item)?.name)].filter(Boolean).join(" → ")}` : discussionRoundIdle ? "可申请发言或开启下一轮" : "队列已空"}</Text></Stack>
          </Group>
          <Group mt="md">{currentSpeaker && <Button size="xs" variant="light" disabled={Boolean(streaming?.active)} onClick={finishSpeaker}>{current?.agent ? streaming?.active ? "AI 发言中…" : "跳过 Agent" : "结束发言"}</Button>}{current?.agent && !streaming?.active && <Button size="xs" variant="subtle" disabled>暂停 Agent</Button>}</Group>
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
              <Title order={3}>{scriptCharacterName || (selectedRole ? (playerById(selectedRole)?.role || selectedRole) : "角色")}的剧本</Title>
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
                        <Text size="xs" c="dimmed">{scriptChapters[highlight.chapter]?.title}</Text>
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
        <Tabs.Panel value="tasks" pt="md"><Stack gap="sm">{[{ label: "主线任务", text: "找到原始门禁记录", done: evidence.some((item) => item.name.includes("门禁") || item.name.includes("值班")) }, { label: "隐藏任务", text: "避免过早暴露数据删除交易", done: false }, { label: "阶段任务", text: phase.id === "search" ? "完成两次搜证" : "推进当前游戏阶段", done: phase.id === "search" && searchesLeft === 0 }].map((task) => <Paper key={task.label} p="sm" radius="lg" className="game-clue-item"><Group justify="space-between"><Text fw={800}>{task.label}</Text><Badge color={task.done ? "teal" : "gray"}>{task.done ? "已完成" : "进行中"}</Badge></Group><Text size="sm" c="dimmed" mt={5}>{task.text}</Text></Paper>)}</Stack></Tabs.Panel>
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
                  <Button size="compact-xs" onClick={() => { setPrivateInviteStatus("已接受"); acceptPrivateInvite(firstAgentPlayerId); }}>允许</Button>
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
                      {event.type === "evidence" && <><Text fw={800}>{event.speaker} 出示证据：{event.evidence.name}</Text><Text size="sm" c="dimmed">{event.reason || event.evidence.description}</Text>{event.aiResponse && <Text size="sm" mt={4}>反应：{event.aiResponse}</Text>}</>}
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
    if (phase.id === "reveal" || phase.id === "review") return <Text c="dimmed">游戏结束阶段。</Text>;
    if (phase.id !== "discussion") return <Group><Button radius="xl" onClick={advancePhase} disabled={(phase.id === "role-selection" && !roleConfirmed) || (phase.id === "script-reading" && !readingDone) || (phase.id === "intro" && introduced.length < introPlayerIds.length) || (phase.id === "search" && searchesLeft > 0)}>进入下一阶段</Button><Text size="sm" c="dimmed">完成当前阶段要求后继续</Text></Group>;
    if (streaming?.active) {
      return (
        <Group gap="xs" wrap="nowrap" style={{ width: "100%" }}>
          <Badge size="lg" color="blue" variant="dot">{streaming.agentName} AI 正在发言…</Badge>
          <Text size="sm" c="dimmed">等待 AI 生成回复后自动结束发言</Text>
        </Group>
      );
    }
    return (
      <Group gap="xs" wrap="nowrap" style={{ width: "100%" }}>
        {discussionRoundIdle && !isUserSpeaking && (
          <Button radius="xl" variant="light" onClick={startNextDiscussionRound} disabled={Boolean(streaming?.active)}>
            开启下一轮讨论
          </Button>
        )}
        {!isUserSpeaking && !userQueued && <Button radius="xl" onClick={joinQueue} disabled={Boolean(forcedAnswer)}>选择发言</Button>}
        {userQueued && !isUserSpeaking && <Button radius="xl" variant="light" onClick={cancelQueue}>取消申请 · 排队第 {(currentSpeaker ? 1 : 0) + queue.indexOf("user") + 1} 位</Button>}
        {isUserSpeaking && <Button radius="xl" color="orange" onClick={finishSpeaker}>结束发言</Button>}
        <Button radius="xl" variant="light" onClick={() => setDialog("private")}>发起私聊</Button>
        <Button radius="xl" variant="light" disabled={!isUserSpeaking} onClick={() => setDialog("force")}>指定 Agent 回答</Button>
        <Button radius="xl" variant="light" disabled={!isUserSpeaking} onClick={() => setDialog("evidence")}>出示证物</Button>
        <Button radius="xl" variant="subtle" color="orange" disabled={Boolean(forcedAnswer)} onClick={() => goToPhase(5)}>进入推理投票</Button>
        <TextInput
          value={publicMessage}
          onChange={(event) => setPublicMessage(event.currentTarget.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void sendPublicMessage();
            }
          }}
          placeholder={isUserSpeaking ? "输入当前公共发言，Enter 发送…" : "轮到你发言后可输入内容"}
          disabled={!isUserSpeaking}
          className="game-message-input"
          radius="xl"
        />
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
                  <Text fw={800}>{current?.role || "暂无"} → {nextSpeaker?.role || (discussionRoundIdle ? "可开启下一轮" : "等待申请")}</Text>
                </Box>
              </Group>
              <Group gap="xs"><Badge size="lg" color="orange" leftSection={<IconClock size={13} />}>{formatTime(speakerSeconds)}</Badge><Button size="xs" variant="light" onClick={() => setDialog("rules")}>游戏规则</Button><Button size="xs" variant="light" color="red" onClick={clearGameProgress}>重置进度</Button><Tooltip label={fullscreen ? "退出全屏" : "全屏"}><ActionIcon size="lg" onClick={toggleFullscreen}>{fullscreen ? <IconX size={18} /> : <IconMaximize size={18} />}</ActionIcon></Tooltip><ActionIcon size="lg" variant={settingsOpen ? "filled" : "light"} onClick={() => setSettingsOpen((value) => !value)}><IconSettings size={18} /></ActionIcon><Button size="xs" color="red" variant="subtle" onClick={() => navigate("/games")}>退出</Button></Group>
            </Group>
            <Box className="game-phase-track">{GAME_PHASES.map((item, index) => <button key={item.id} disabled={(index === 0 && roleConfirmed) || Boolean(streaming?.active)} className={`${index < phaseIndex ? "game-phase-step is-complete" : index === phaseIndex ? "game-phase-step is-active" : "game-phase-step"}${index === 0 && roleConfirmed ? " is-locked" : ""}`} onClick={() => goToPhase(index)}><span>{index < phaseIndex ? "✓" : index + 1}</span><Text size="xs">{item.shortLabel}</Text></button>)}</Box>
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
              <Group justify="space-between" mb="md"><Group gap="xs"><IconUsers size={18} /><Text fw={900}>玩家与 Agent</Text></Group><Badge color="teal">{nonDmPlayerIds.length} 在线</Badge></Group>
              <ScrollArea className="game-panel-scroll" offsetScrollbars>
                <Stack gap="xs">
                  {dynamicPlayers.filter((player) => player.id !== "dm").map((player) => {
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
                          <Box className="game-avatar-wrap">{(() => { const portrait = player.agent ? getAgentPortrait(player.name) : getRolePortrait(player.role); return portrait ? <Avatar src={portrait} size={40} radius="xl" imageProps={{ style: { objectPosition: "top" } }} /> : <Avatar color={player.color}>{player.role.slice(0, 1)}</Avatar>; })()}<Box className="game-online-dot" /></Box>
                          <Box style={{ flex: 1, minWidth: 0 }}>
                            <Group gap={5}>
                              <Text fw={900} truncate>{player.role}</Text>
                              {isSelf && <Badge size="xs" color="orange" variant="filled">我</Badge>}
                            </Group>
                            <Text size="xs" c="dimmed" truncate>玩家：{player.name}</Text>
                          </Box>
                          <Badge size="xs" color={status === "正在发言" ? "orange" : status.startsWith("排队") ? "gray" : status === "可发言" ? "teal" : "blue"} variant="dot">{status}</Badge>
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

      <Modal opened={dialog === "force"} onClose={() => setDialog(null)} title="指定 Agent 回答" centered><Stack><Select label="选择 Agent" value={targetId} onChange={(value) => setTargetId(value || firstAgentPlayerId)} data={agents.map((agent) => ({ value: agent.id, label: `${agent.name} · ${agent.role}` }))} /><Textarea label="需要回答的问题" value={question} onChange={(event) => setQuestion(event.currentTarget.value)} minRows={4} /><Button onClick={confirmForcedAnswer}>确认指定</Button></Stack></Modal>
      <Modal opened={dialog === "evidence"} onClose={() => setDialog(null)} title="出示证物" centered><Stack>{evidence.length === 0 ? <Text c="dimmed">暂无证物，请先完成搜证或等待初始证物加载。</Text> : <><Select label="选择证物" value={selectedEvidenceId || evidence[0]?.id || ""} onChange={(value) => setSelectedEvidenceId(value || evidence[0]?.id || "")} data={evidence.map((item) => ({ value: item.id, label: item.name }))} /><Textarea label="出示理由" placeholder="说明这项证据支持或反驳了什么观点" value={evidenceReason} onChange={(event) => setEvidenceReason(event.currentTarget.value)} minRows={3} /><Radio.Group label="公开范围" value={evidenceVisibility} onChange={setEvidenceVisibility}><Stack mt="xs"><Radio value="所有人" label="公开给所有人" /><Radio value="指定角色" label="只分享给指定角色" /></Stack></Radio.Group>{evidenceVisibility === "指定角色" && <Select label="指定角色" value={targetId} onChange={(value) => setTargetId(value || firstAgentPlayerId)} data={dynamicPlayers.filter((player) => player.id !== "user" && player.id !== "dm" && player.role !== "顾沉" && player.role !== "侦探").map((player) => ({ value: player.id, label: `${player.role} · ${player.name}` }))} />}<Button onClick={showEvidence} disabled={!selectedEvidenceId && !evidence[0]?.id}>确认出示</Button></>}</Stack></Modal>
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
        title="讨论详情"
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
              {selectedDiscussionSource.type === "evidence" && selectedDiscussionSource.aiResponse && (
                <Paper p="sm" radius="md" mt="md" className="game-evidence-reaction">
                  <Text size="xs" c="blue.3" fw={700}>
                    {selectedDiscussionSource.targetName ? `${selectedDiscussionSource.targetName} 的反应` : "角色反应"}
                  </Text>
                  <Text size="sm" mt={4} lh={1.7}>{selectedDiscussionSource.aiResponse}</Text>
                </Paper>
              )}
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
      <Modal
        opened={dialog === "script"}
        onClose={() => setDialog(null)}
        title="我的剧本"
        size="xl"
        centered
        radius="xl"
      >
        {scriptChapters.length > 0 ? (
          <Stack gap="md">
            <Paper radius="xl" p="xl" className="game-reading-card">
              <Text className="monospace-label" size="xs" c="red.3">private script / chapter {chapter + 1}</Text>
              <Title order={2} mt="sm">{scriptChapters[chapter].title}</Title>
              <Text
                fz="lg"
                lh={1.9}
                mt="lg"
                className="game-script-selectable"
                onMouseUp={() => captureScriptSelection(chapter)}
              >
                {renderHighlightedScript(scriptChapters[chapter].content, chapter)}
              </Text>
            </Paper>
            <Group justify="space-between">
              <Button variant="light" disabled={chapter === 0} onClick={() => setChapter((value) => value - 1)}>上一章节</Button>
              <Text size="sm" c="dimmed">{chapter + 1} / {scriptChapters.length}</Text>
              <Button 
                disabled={chapter === scriptChapters.length - 1} 
                onClick={() => setChapter((value) => value + 1)}
              >
                下一章节
              </Button>
            </Group>
          </Stack>
        ) : (
          <Text c="dimmed" ta="center" py="xl">暂无剧本数据，请确认是否已完成选角。</Text>
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
            onChange={(value) => setPointTargetId(value || dynamicPlayers.find((p) => p.id !== "user" && p.id !== "dm")?.id || "")}
            data={dynamicPlayers.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({
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
            onChange={(value) => setInquiryTargetId(value || dynamicPlayers.find((p) => p.id !== "user" && p.id !== "dm")?.id || "")}
            data={dynamicPlayers.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({
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
      <Modal opened={dialog === "private"} onClose={() => setDialog(null)} title="发起或接受私聊" centered><Stack><Select label="私聊对象" value={targetId} onChange={(value) => setTargetId(value || dynamicPlayers.find((p) => p.id !== "user" && p.id !== "dm")?.id || "")} data={dynamicPlayers.filter((player) => player.id !== "user" && player.id !== "dm").map((player) => ({ value: player.id, label: `${player.role} · 玩家：${player.name}` }))} /><Text size="sm" c="dimmed">私聊建立后即可直接对话，不需要额外设置 Agent 发言权限；私聊内容和证物不会自动公开。</Text><Button onClick={() => acceptPrivateInvite()}>建立私聊</Button></Stack></Modal>
      <Modal opened={dialog === "rules"} onClose={() => setDialog(null)} title="游戏规则" centered size="lg"><Stack><Text>公共讨论采用单一发言权，普通发言按申请顺序进行。</Text><Text>被指定回答的 Agent 必须成为下一位发言者，回答结束后恢复原队列。</Text><Text>私聊与公共讨论独立运行，私聊内容和证物仅参与者可见。</Text><Text>进入投票阶段后停止新的发言、私聊和证物出示。</Text></Stack></Modal>
      <Modal
        opened={dialog === "script"}
        onClose={() => {
          setDialog(null);
          setSelectedScriptText("");
        }}
        title={`我的剧本 · ${scriptCharacterName || selectedRole || "角色"}`}
        centered
        size="xl"
        scrollAreaComponent={ScrollArea.Autosize}
      >
        <Stack gap="lg">
          <Text size="sm" c="dimmed">拖动选中具体语句，再点击“高亮选中文段”。高亮会自动保存在当前浏览器。</Text>
          {scriptChapters.map((item, chapterIndex) => (
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
                        <Text size="xs" c="dimmed">{scriptChapters[highlight.chapter]?.title}</Text>
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
            {getRolePortrait(introSpotlight.role) ? (
              <img
                src={getRolePortrait(introSpotlight.role)}
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
              {getRolePortrait(introSpotlight.role) ? (
                <Avatar src={getRolePortrait(introSpotlight.role)} size={48} radius="xl" imageProps={{ style: { objectPosition: "top" } }} />
              ) : (
                <Avatar color={introSpotlight.color}>{introSpotlight.role.slice(0, 1)}</Avatar>
              )}
              <Box>
                <Title order={3}>{introSpotlight.role}</Title>
                <Text size="sm" c="dimmed">{introSpotlight.name} · {introSpotlight.agent ? "AI 玩家" : "真人玩家"}</Text>
              </Box>
            </Group>
            <Text fz="lg" lh={1.8} mt="md">"{INTRO_LINES[ROLE_TO_INTRO_KEY[resolveRoleName(introSpotlight.role)] || introSpotlight.role] || INTRO_LINES[introSpotlight.id] || `我是${introSpotlight.role}，${introSpotlight.publicIdentity}。`}"</Text>
            <Text size="xs" c="dimmed" ta="center" mt="md">点击任意位置继续</Text>
          </Paper>
        </Box>
      )}
    </StudioShell>
  );
}

export { GamePage };
