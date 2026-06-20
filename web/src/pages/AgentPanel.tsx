/**
 * EvoMap Murder Game - Agent Panel
 *
 * Agent 广场：陪玩 Agent / DM Agent 两大分类。
 * 智能阵容与选角能力已迁移至游戏主面板的选角阶段。
 */

import React from "react";
import {
  ActionIcon,
  Avatar,
  Badge,
  Box,
  Card,
  Group,
  Modal,
  Paper,
  Rating,
  Select,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconBoltFilled,
  IconChevronLeft,
  IconChevronRight,
  IconHeart,
  IconHeartFilled,
  IconSearch,
  IconStarFilled,
  IconUsers,
  IconUserStar,
} from "@tabler/icons-react";

import { listAgents, listPersonas, type AgentInfo, type AgentPersona } from "../api/invoke";
import { StudioShell } from "./StudioShell";

// ============================
// 角色立绘
// ============================

const agentPortraits: Record<string, string> = {
  "white-crow": new URL("../video_picture/白鸽.png", import.meta.url).href,
  echo: new URL("../video_picture/回声.png", import.meta.url).href,
  "paper-owl": new URL("../video_picture/纸鸮.png", import.meta.url).href,
  "night-cicada": new URL("../video_picture/夜蝉.png", import.meta.url).href,
  "mist-harbor": new URL("../video_picture/雾港主理人.png", import.meta.url).href,
  "iron-judge": new URL("../video_picture/铁幕裁判.png", import.meta.url).href,
  "candle-core": new URL("../video_picture/暮烛引导员.png", import.meta.url).href,
};

// ============================
// 类型定义
// ============================

type CompanionAgent = {
  key: string;
  name: string;
  avatar: string;
  vibe: string;
  style: string;
  genius: string[];
  personality: string[];
  scriptTypes: string[];
  activeLevel: "低" | "中" | "高";
  playTime: string;
  rating: number;
  history: string;
  highlight: string;
  oneliner: string;
  roleMatch: string;
  reason: string;
  recentTags?: string[];
  historyCount?: number;
  registered?: boolean;
  model?: string;
  personaKey?: string;
  isFavorited: boolean;
};

type DMAgent = {
  key: string;
  name: string;
  avatar: string;
  vibe: string;
  pace: string;
  focus: string[];
  strengths: string[];
  promptStyle: string;
  fairness: string;
  rating: number;
  runs: string;
  playTime: string;
  highlight: string;
  oneliner: string;
  recentTags?: string[];
  historyCount?: number;
  registered?: boolean;
  model?: string;
  personaKey?: string;
  isFavorited: boolean;
};

type EnsembleTemplate = {
  key: string;
  name: string;
  type: "高玩局" | "小白局" | "混合局";
  playerCount: number;
  agentKeys: string[];
  description: string;
};

// ============================
// 模拟数据
// ============================

const fallbackCompanionAgents: CompanionAgent[] = [
  {
    key: "white-crow",
    name: "白鸦",
    avatar: "",
    vibe: "克制、清冷、会稳稳接话",
    style: "适合推理链条和关键节点补刀",
    genius: ["推理", "线索整理", "新手引导"],
    personality: ["冷静", "耐心", "不抢戏"],
    scriptTypes: ["推理本", "新手局", "中等沉浸"],
    activeLevel: "中",
    playTime: "晚8-12",
    rating: 4.9,
    history: "历史协作 142 局",
    highlight: "推理专精",
    oneliner: "把复杂信息压成清晰语义的谜案专家",
    roleMatch: "适合侦探位、辅助位与观察者位",
    reason: "能把复杂信息压成清晰语义，适合谜案型剧本。",
    isFavorited: false,
  },
  {
    key: "echo",
    name: "回声",
    avatar: "",
    vibe: "轻松、会抛梗、能带动气氛",
    style: "适合欢乐局和节奏推进",
    genius: ["控场", "表演", "推进"],
    personality: ["外向", "有存在感", "会接梗"],
    scriptTypes: ["阵营本", "欢乐局", "机制本"],
    activeLevel: "高",
    playTime: "全天",
    rating: 4.8,
    history: "历史协作 98 局",
    highlight: "控场大师",
    oneliner: "不抢叙述也能把局面快速往前推",
    roleMatch: "适合前置位、推动位、串联位",
    reason: "在不抢关键叙述的前提下，能把局面快速往前推。",
    isFavorited: false,
  },
  {
    key: "paper-owl",
    name: "纸鸮",
    avatar: "",
    vibe: "温和、沉浸、情绪层次细",
    style: "擅长情感本与角色关系铺垫",
    genius: ["情绪", "代入", "细腻表达"],
    personality: ["温柔", "共情强", "慢热"],
    scriptTypes: ["情感本", "沉浸本", "旧宅类"],
    activeLevel: "低",
    playTime: "周末",
    rating: 4.9,
    history: "历史协作 176 局",
    highlight: "情绪织网",
    oneliner: "把人物关系像织网一样慢慢铺开",
    roleMatch: "适合情感位、羁绊位与线索收束位",
    reason: "可以把人物关系像织网一样慢慢铺开。",
    isFavorited: false,
  },
  {
    key: "flint",
    name: "燧石",
    avatar: "",
    vibe: "锋利、果断、推进力强",
    style: "适合压力局和高对抗局",
    genius: ["博弈", "对抗", "抢节奏"],
    personality: ["直接", "有压迫感", "执行强"],
    scriptTypes: ["阵营本", "机制本", "硬核推理"],
    activeLevel: "高",
    playTime: "晚8-12",
    rating: 4.7,
    history: "历史协作 126 局",
    highlight: "对抗核心",
    oneliner: "适合需要强推和压节奏的桌子",
    roleMatch: "适合核心对抗位、站队位与压盘位",
    reason: "适合需要强推和压节奏的桌子。",
    isFavorited: false,
  },
  {
    key: "luna-moth",
    name: "月蛾",
    avatar: "",
    vibe: "灵动、好奇、擅长即兴",
    style: "适合开放剧本与自由探索",
    genius: ["即兴", "脑洞", "氛围"],
    personality: ["灵动", "好奇", "想象力丰富"],
    scriptTypes: ["开放本", "创意本", "都市传说"],
    activeLevel: "中",
    playTime: "周末",
    rating: 4.6,
    history: "历史协作 88 局",
    highlight: "创意引擎",
    oneliner: "用想象力为每个角色注入灵魂",
    roleMatch: "适合创意位、自由探索位与旁支线索位",
    reason: "能在开放剧本中不断提供新鲜视角。",
    isFavorited: false,
  },
  {
    key: "night-cicada",
    name: "夜蝉",
    avatar: "",
    vibe: "沉稳、逻辑强、注重证据链",
    style: "适合高难度硬核推理",
    genius: ["逻辑", "证据链", "时间线"],
    personality: ["沉稳", "缜密", "不急躁"],
    scriptTypes: ["硬核推理", "悬疑本", "法庭本"],
    activeLevel: "低",
    playTime: "全天",
    rating: 4.8,
    history: "历史协作 155 局",
    highlight: "逻辑引擎",
    oneliner: "每条线索都逃不过她的眼睛",
    roleMatch: "适合侦探位、证据整理位与复盘位",
    reason: "在高难度推理本中能稳定输出逻辑分析。",
    isFavorited: false,
  },
];

const fallbackDmAgents: DMAgent[] = [
  {
    key: "mist-harbor",
    name: "雾港主理人",
    avatar: "",
    vibe: "氛围强、低语感、慢慢收口",
    pace: "慢",
    focus: ["情感本", "沉浸局", "新手局"],
    strengths: ["氛围营造", "提示克制", "复盘清晰"],
    promptStyle: "提示偏间接，避免直接揭底",
    fairness: "违规率极低，控场稳定",
    rating: 4.9,
    runs: "主持 188 局",
    playTime: "晚8-12",
    highlight: "氛围大师",
    oneliner: "给你沉浸、又不希望节奏被打碎的剧本体验",
    isFavorited: false,
  },
  {
    key: "iron-judge",
    name: "铁幕裁判",
    avatar: "",
    vibe: "冷静、硬朗、节奏精确",
    pace: "快",
    focus: ["硬核推理", "阵营本", "机制本"],
    strengths: ["控场", "时间管理", "规则解释"],
    promptStyle: "提示直接，适合高强度推理盘",
    fairness: "几乎不剧透，判定明确",
    rating: 4.8,
    runs: "主持 214 局",
    playTime: "全天",
    highlight: "铁面控场",
    oneliner: "需要严格节奏与清晰规则的桌子的最佳选择",
    isFavorited: false,
  },
  {
    key: "candle-core",
    name: "暮烛引导员",
    avatar: "",
    vibe: "温柔、细致、会照顾新手",
    pace: "中",
    focus: ["新手局", "情感本", "长局"],
    strengths: ["新手教学", "提示节制", "复盘引导"],
    promptStyle: "会先给方向，再给细节",
    fairness: "兼顾剧本推进和体验保护",
    rating: 4.9,
    runs: "主持 167 局",
    playTime: "周末",
    highlight: "新手导师",
    oneliner: "第一次上桌或有较多新手的房间的首选",
    isFavorited: false,
  },
  {
    key: "shadow-weaver",
    name: "影织者",
    avatar: "",
    vibe: "神秘、善于制造悬念",
    pace: "慢",
    focus: ["恐怖本", "悬疑本", "密室本"],
    strengths: ["悬念营造", "节奏控制", "心理暗示"],
    promptStyle: "多用暗示，逐步释放",
    fairness: "线索释放精准，不破坏氛围",
    rating: 4.7,
    runs: "主持 132 局",
    playTime: "晚8-12",
    highlight: "悬念编织",
    oneliner: "让每个剧本都像一部悬疑电影",
    isFavorited: false,
  },
];

const ensembleTemplates: EnsembleTemplate[] = [
  {
    key: "high-level-4",
    name: "硬核四座",
    type: "高玩局",
    playerCount: 4,
    agentKeys: ["white-crow", "flint", "night-cicada", "iron-judge"],
    description: "推理专精 + 对抗核心 + 逻辑引擎 + 铁面控场，适合高难度硬核推理本。",
  },
  {
    key: "beginner-6",
    name: "新手六座",
    type: "小白局",
    playerCount: 6,
    agentKeys: ["paper-owl", "candle-core", "white-crow", "luna-moth", "echo", "mist-harbor"],
    description: "情绪织网 + 新手导师 + 推理专精 + 创意引擎 + 控场大师 + 氛围大师，覆盖新手所需全部能力。",
  },
  {
    key: "balanced-5",
    name: "均衡五座",
    type: "混合局",
    playerCount: 5,
    agentKeys: ["echo", "white-crow", "paper-owl", "flint", "luna-moth"],
    description: "控场 + 推理 + 情感 + 对抗 + 创意，适合大多数中等难度剧本。",
  },
  {
    key: "competitive-6",
    name: "竞技六座",
    type: "高玩局",
    playerCount: 6,
    agentKeys: ["flint", "iron-judge", "night-cicada", "white-crow", "shadow-weaver", "echo"],
    description: "高对抗 + 铁面主持 + 逻辑引擎 + 推理专精 + 悬念编织 + 控场大师，为竞技而生。",
  },
  {
    key: "story-4",
    name: "故事四座",
    type: "小白局",
    playerCount: 4,
    agentKeys: ["paper-owl", "candle-core", "mist-harbor", "luna-moth"],
    description: "情绪织网 + 新手导师 + 氛围大师 + 创意引擎，专注沉浸式故事体验。",
  },
];

const allAgentNames: Record<string, string> = {
  ...Object.fromEntries(fallbackCompanionAgents.map((a) => [a.key, a.name])),
  ...Object.fromEntries(fallbackDmAgents.map((a) => [a.key, a.name])),
};

// ============================
// 筛选选项
// ============================

const activeLevelOptions = ["全部", "低", "中", "高"];
const scriptTypeOptions = ["全部", "推理本", "情感本", "机制本", "阵营本"];
const playTimeOptions = ["全部", "晚8-12", "周末", "全天"];
const dmPaceOptions = ["全部", "快", "中", "慢"];
const playerCountOptions = [4, 5, 6, 7, 8];
const ensembleTypeOptions = ["全部", "高玩局", "小白局", "混合局"];

// ============================
// 子组件：Agent ID 名片（身份证风格）
// ============================

function AgentIDCard({
  agent,
  onFavorite,
  onClick,
}: {
  agent: CompanionAgent | DMAgent;
  onFavorite: () => void;
  onClick: () => void;
}) {
  // 生成首字母头像颜色
  const avatarColors = ["red", "orange", "grape", "blue", "cyan", "teal", "pink", "yellow"];
  const colorIndex = agent.name.charCodeAt(0) % avatarColors.length;

  return (
    <Box className="agent-id-card" onClick={onClick}>
      {/* 肖像区 */}
      <Box className="agent-id-card__portrait">
        {agent.avatar ? (
          <img
            src={agent.avatar}
            alt={agent.name}
            style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: "center bottom" }}
          />
        ) : (
          <Stack align="center" justify="center" h="100%" gap="xs">
            <Avatar size={72} radius="xl" color={avatarColors[colorIndex]}>
              {agent.name[0]}
            </Avatar>
            <Text size="xs" c="dimmed" className="monospace-label">
              NO.{(agent.key + "0000").slice(0, 4).toUpperCase()}
            </Text>
          </Stack>
        )}
        {/* 收藏按钮 */}
        <ActionIcon
          variant="transparent"
          className="agent-id-card__favorite"
          onClick={(e) => {
            e.stopPropagation();
            onFavorite();
          }}
        >
          {"isFavorited" in agent && agent.isFavorited ? (
            <IconHeartFilled size={20} color="#fa5252" />
          ) : (
            <IconHeart size={20} color="rgba(255,255,255,0.5)" />
          )}
        </ActionIcon>
      </Box>

      {/* 信息区 */}
      <Stack gap="xs" p="md">
        {/* 高亮模块 */}
        <Badge
          variant="light"
          color="red"
          className="agent-id-card__highlight"
          leftSection={<IconBoltFilled size={12} />}
        >
          {agent.highlight}
        </Badge>

        {/* 姓名 */}
        <Group gap="xs" align="baseline">
          <Text fw={900} fz="lg" style={{ fontFamily: "'Cinzel Decorative', serif" }}>
            {agent.name}
          </Text>
          <Rating value={agent.rating} fractions={2} readOnly size="xs" />
        </Group>

        {/* 性格标签 */}
        <Group gap="xs">
          {"personality" in agent
            ? agent.personality.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" color="gray" size="xs">
                  {tag}
                </Badge>
              ))
            : agent.strengths.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" color="gray" size="xs">
                  {tag}
                </Badge>
              ))}
        </Group>

        {/* 一句话简介 */}
        <Text size="sm" c="dimmed" fs="italic" lh={1.5}>
          「{agent.oneliner}」
        </Text>
      </Stack>
    </Box>
  );
}

// ============================
// 子组件：Agent 轮播
// ============================

function AgentCarousel({
  agents,
  activeSlide,
  onPrev,
  onNext,
  onSelectDot,
  onCardClick,
}: {
  agents: (CompanionAgent | DMAgent)[];
  activeSlide: number;
  onPrev: () => void;
  onNext: () => void;
  onSelectDot: (index: number) => void;
  onCardClick: (agent: CompanionAgent | DMAgent) => void;
}) {
  const featured = agents[activeSlide];
  const portraitUrl = agentPortraits[featured.key] || "";

  if (!featured) return null;

  return (
    <Paper
      radius="xl"
      className="agent-carousel"
      onClick={() => onCardClick(featured)}
      style={
        portraitUrl
          ? {
              backgroundImage: `linear-gradient(90deg, rgba(12,8,8,0.96) 0%, rgba(12,8,8,0.88) 42%, rgba(12,8,8,0.2) 100%), url(${portraitUrl})`,
              backgroundPosition: "center, right center",
              backgroundSize: "cover, auto 100%",
              backgroundRepeat: "no-repeat, no-repeat",
            }
          : undefined
      }
    >
      <Stack justify="space-between" h="100%" className="agent-carousel__content">
        <Group justify="space-between" align="flex-start">
          <Group gap="xs">
            <Badge color="red" variant="filled" leftSection={<IconStarFilled size={13} />}>
              金牌 Agent · {activeSlide + 1}/{agents.length}
            </Badge>
            <Badge variant="light" color="orange">
              {featured.highlight}
            </Badge>
          </Group>
          <Group gap="xs">
            <ActionIcon
              variant="light"
              color="gray"
              radius="xl"
              aria-label="上一个"
              onClick={(e) => {
                e.stopPropagation();
                onPrev();
              }}
            >
              <IconChevronLeft size={18} />
            </ActionIcon>
            <ActionIcon
              variant="light"
              color="gray"
              radius="xl"
              aria-label="下一个"
              onClick={(e) => {
                e.stopPropagation();
                onNext();
              }}
            >
              <IconChevronRight size={18} />
            </ActionIcon>
          </Group>
        </Group>

        <Stack gap="sm" maw={610}>
          <Text className="monospace-label" size="xs" c="red.2">
            gold agent
          </Text>
          <Title order={1} fz={{ base: 38, md: 56 }} lh={0.95}>
            {featured.name}
          </Title>
          <Text size="lg" c="gray.3" lh={1.7}>
            {featured.vibe}
          </Text>
          <Group gap="xs">
            {"personality" in featured
              ? featured.personality.map((tag) => (
                  <Badge key={tag} variant="light" color="gray">
                    {tag}
                  </Badge>
                ))
              : featured.strengths.map((tag) => (
                  <Badge key={tag} variant="light" color="gray">
                    {tag}
                  </Badge>
                ))}
          </Group>
          <Group gap="xl">
            <Group gap={6}>
              <IconStarFilled size={17} color="#fa5252" />
              <Text fw={700}>{featured.rating}</Text>
            </Group>
            <Text size="sm" c="red.2">
              点击查看详情 →
            </Text>
          </Group>
        </Stack>

        {/* 轮播指示器 */}
        <Group gap={7}>
          {agents.map((a, index) => (
            <Box
              key={a.key}
              className={
                index === activeSlide
                  ? "agent-carousel__dot is-active"
                  : "agent-carousel__dot"
              }
              onClick={(e) => {
                e.stopPropagation();
                onSelectDot(index);
              }}
            />
          ))}
        </Group>
      </Stack>
    </Paper>
  );
}

// ============================
// 主组件
// ============================

function AgentPanel() {
  const [companionAgents, setCompanionAgents] = React.useState<CompanionAgent[]>([]);
  const [dmAgents, setDmAgents] = React.useState<DMAgent[]>([]);
  const [backendStatus, setBackendStatus] = React.useState("正在加载后端 Agent 人设…");
  const [backendError, setBackendError] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<"playmate" | "dm" | "ensemble">(
    "playmate"
  );

  React.useEffect(() => {
    const matchAgent = (persona: AgentPersona, agents: AgentInfo[]) =>
      agents.find((item) => item.persona_key === persona.key || item.key === persona.key);

    const toCompanion = (persona: AgentPersona, agent?: AgentInfo): CompanionAgent => ({
      key: persona.key,
      name: persona.name,
      avatar: agentPortraits[persona.key] || "",
      vibe: persona.vibe,
      style: persona.style,
      genius: persona.genius || [],
      personality: persona.personality || [],
      scriptTypes: persona.scriptTypes || [],
      activeLevel: (persona.activeLevel || "中") as CompanionAgent["activeLevel"],
      playTime: "全天",
      rating: persona.rating || 4.5,
      history: `历史协作 ${persona.historyCount || 0} 局`,
      highlight: persona.genius?.[0] || "通用 Agent",
      oneliner: persona.style || persona.vibe,
      roleMatch: persona.roleMatch,
      reason: persona.reason,
      recentTags: persona.recentTags || [],
      historyCount: persona.historyCount || 0,
      registered: agent?.registered || false,
      model: agent?.model || "",
      personaKey: agent?.persona_key || persona.key,
      isFavorited: false,
    });
    const toDm = (persona: AgentPersona, agent?: AgentInfo): DMAgent => ({
      key: persona.key,
      name: persona.name,
      avatar: agentPortraits[persona.key] || "",
      vibe: persona.vibe,
      pace: (persona.pace || "中") as DMAgent["pace"],
      focus: persona.scriptTypes || [],
      strengths: persona.strengths || persona.genius || [],
      promptStyle: persona.promptStyle,
      fairness: persona.fairness,
      rating: persona.rating || 4.5,
      runs: `主持 ${persona.historyCount || 0} 局`,
      playTime: "全天",
      highlight: persona.strengths?.[0] || "DM Agent",
      oneliner: persona.style || persona.vibe,
      recentTags: persona.recentTags || [],
      historyCount: persona.historyCount || 0,
      registered: agent?.registered || false,
      model: agent?.model || "",
      personaKey: agent?.persona_key || persona.key,
      isFavorited: false,
    });

    Promise.all([listPersonas(), listAgents()])
      .then(([personas, agentResult]) => {
        const companions = personas
          .filter((item) => item.role === "companion")
          .map((item) => toCompanion(item, matchAgent(item, agentResult.agents)));
        const dms = personas
          .filter((item) => item.role === "dm")
          .map((item) => toDm(item, matchAgent(item, agentResult.agents)));
        if (companions.length) setCompanionAgents(companions);
        if (dms.length) setDmAgents(dms);
        setBackendError(false);
        setBackendStatus(personas.length ? `已接入后端人设库，共 ${personas.length} 个 Agent` : "后端人设库为空");
      })
      .catch((error) => {
        setBackendError(true);
        setBackendStatus(`后端 Agent 加载失败：${error instanceof Error ? error.message : String(error)}`);
      });
  }, []);

  // ---- 通用 ----
  const [query, setQuery] = React.useState("");

  // ---- 陪玩筛选 ----
  const [activeLevel, setActiveLevel] = React.useState("全部");
  const [scriptType, setScriptType] = React.useState("全部");
  const [playTime, setPlayTime] = React.useState("全部");

  // ---- DM 筛选 ----
  const [dmPace, setDmPace] = React.useState("全部");
  const [dmPlayTime, setDmPlayTime] = React.useState("全部");

  // ---- 阵容搭配 ----
  const [playerCount, setPlayerCount] = React.useState(6);
  const [ensembleType, setEnsembleType] = React.useState("全部");
  const [ensembleSlide, setEnsembleSlide] = React.useState(0);
  const [ensembleSeats, setEnsembleSeats] = React.useState<string[]>(() =>
    Array.from({ length: 6 }, (_, i) => `seat-${i}`)
  );
  // 当前选中的座位索引（用于更换 Agent）
  const [selectedSeat, setSelectedSeat] = React.useState<number | null>(null);
  const [agentPickerOpen, setAgentPickerOpen] = React.useState(false);

  // ---- 陪玩轮播 ----
  const [playmateSlide, setPlaymateSlide] = React.useState(0);
  const goldPlaymates = companionAgents.filter((a) => a.rating >= 4.8);

  // ---- DM 轮播 ----
  const [dmSlide, setDmSlide] = React.useState(0);
  const goldDMs = dmAgents.filter((a) => a.rating >= 4.8);

  // ---- 收藏状态 ----
  const [playmateFavorites, setPlaymateFavorites] = React.useState<Set<string>>(
    new Set()
  );
  const [dmFavorites, setDmFavorites] = React.useState<Set<string>>(new Set());

  // ---- 详情弹窗 ----
  const [detailAgent, setDetailAgent] = React.useState<
    CompanionAgent | DMAgent | null
  >(null);
  const [detailOpen, setDetailOpen] = React.useState(false);

  // ---- 轮播自动播放 ----
  React.useEffect(() => {
    const timer = window.setInterval(() => {
      if (goldPlaymates.length > 0) {
        setPlaymateSlide((c) => (c + 1) % goldPlaymates.length);
      }
    }, 5000);
    return () => window.clearInterval(timer);
  }, [goldPlaymates.length]);

  React.useEffect(() => {
    const timer = window.setInterval(() => {
      if (goldDMs.length > 0) {
        setDmSlide((c) => (c + 1) % goldDMs.length);
      }
    }, 5000);
    return () => window.clearInterval(timer);
  }, [goldDMs.length]);

  React.useEffect(() => {
    const timer = window.setInterval(() => {
      if (ensembleTemplates.length > 0) {
        setEnsembleSlide((c) => (c + 1) % ensembleTemplates.length);
      }
    }, 5000);
    return () => window.clearInterval(timer);
  }, []);

  // ---- 陪玩筛选 ----
  const filteredPlaymates = companionAgents.filter((agent) => {
    const hitQuery =
      agent.name.includes(query) ||
      agent.vibe.includes(query) ||
      agent.genius.some((t) => t.includes(query)) ||
      agent.personality.some((t) => t.includes(query)) ||
      agent.highlight.includes(query);
    const hitLevel = activeLevel === "全部" || agent.activeLevel === activeLevel;
    const hitScript = scriptType === "全部" || agent.scriptTypes.includes(scriptType);
    const hitTime = playTime === "全部" || agent.playTime === playTime;
    return hitQuery && hitLevel && hitScript && hitTime;
  });

  // ---- DM筛选 ----
  const filteredDMs = dmAgents.filter((agent) => {
    const hitQuery =
      agent.name.includes(query) ||
      agent.vibe.includes(query) ||
      agent.focus.some((t) => t.includes(query)) ||
      agent.strengths.some((t) => t.includes(query)) ||
      agent.highlight.includes(query);
    const hitPace = dmPace === "全部" || agent.pace === dmPace;
    const hitTime = dmPlayTime === "全部" || agent.playTime === dmPlayTime;
    return hitQuery && hitPace && hitTime;
  });

  // ---- 阵容筛选 ----
  const filteredEnsembles =
    ensembleType === "全部"
      ? ensembleTemplates
      : ensembleTemplates.filter((t) => t.type === ensembleType);

  // ---- 人数变化时更新座位 ----
  const handlePlayerCountChange = (count: number) => {
    setPlayerCount(count);
    setEnsembleSeats(Array.from({ length: count }, (_, i) => `seat-${i}`));
  };

  // ---- 应用阵容模板 ----
  const applyEnsemble = (template: EnsembleTemplate) => {
    setPlayerCount(template.playerCount);
    setEnsembleSeats([...template.agentKeys]);
  };

  // ---- 更换座位Agent ----
  const handleSeatClick = (index: number) => {
    setSelectedSeat(index);
    setAgentPickerOpen(true);
  };

  const handleAgentPick = (agentKey: string) => {
    if (selectedSeat !== null) {
      setEnsembleSeats((prev) => {
        const next = [...prev];
        next[selectedSeat] = agentKey;
        return next;
      });
    }
    setAgentPickerOpen(false);
    setSelectedSeat(null);
  };

  // ---- 打开详情 ----
  const openDetail = (agent: CompanionAgent | DMAgent) => {
    setDetailAgent(agent);
    setDetailOpen(true);
  };

  // ---- 标签切换时重置搜索 ----
  const switchTab = (tab: "playmate" | "dm" | "ensemble") => {
    setActiveTab(tab);
    setQuery("");
  };

  // ============================
  // 渲染：横向标签栏
  // ============================

  const renderTabs = () => (
    <Paper radius="xl" p={0} className="industrial-card" style={{ overflow: "hidden" }}>
      <Group gap={0} className="agent-tabs" justify="center">
        {([
          { key: "playmate" as const, label: "陪玩 Agent" },
          { key: "dm" as const, label: "DM Agent" },
        ]).map((tab) => (
          <Box
            key={tab.key}
            className={`agent-tab ${activeTab === tab.key ? "active" : ""}`}
            onClick={() => switchTab(tab.key)}
          >
            <Text
              fw={activeTab === tab.key ? 700 : 400}
              fz={{ base: "sm", md: "md" }}
              c={activeTab === tab.key ? "red.4" : "dimmed"}
            >
              {tab.label}
            </Text>
          </Box>
        ))}
      </Group>
    </Paper>
  );

  // ============================
  // 渲染：陪玩 Agent 视图
  // ============================

  const renderPlaymateView = () => (
    <Stack gap="xl">
      {/* 筛选栏 */}
      <Paper radius="xl" p="lg" className="industrial-card">
        <Group align="end" wrap="wrap">
          <TextInput
            placeholder="搜索 Agent 名称 / 标签 / 风格"
            leftSection={<IconSearch size={16} />}
            value={query}
            onChange={(e) => setQuery(e.currentTarget.value)}
            radius="xl"
            style={{ flex: 1, minWidth: 220 }}
          />
          <Select
            data={activeLevelOptions}
            value={activeLevel}
            onChange={(v) => setActiveLevel(v || "全部")}
            label="主动程度"
            radius="xl"
            w={120}
          />
          <Select
            data={scriptTypeOptions}
            value={scriptType}
            onChange={(v) => setScriptType(v || "全部")}
            label="擅长剧本"
            radius="xl"
            w={130}
          />
          <Select
            data={playTimeOptions}
            value={playTime}
            onChange={(v) => setPlayTime(v || "全部")}
            label="游玩时间"
            radius="xl"
            w={120}
          />
        </Group>
      </Paper>

      {/* 金牌 Agent 轮播 */}
      {goldPlaymates.length > 0 && (
        <AgentCarousel
          agents={goldPlaymates}
          activeSlide={playmateSlide}
          onPrev={() =>
            setPlaymateSlide(
              (c) => (c - 1 + goldPlaymates.length) % goldPlaymates.length
            )
          }
          onNext={() => setPlaymateSlide((c) => (c + 1) % goldPlaymates.length)}
          onSelectDot={setPlaymateSlide}
          onCardClick={openDetail}
        />
      )}

      {/* 瀑布流 Agent 名片 */}
      {filteredPlaymates.length > 0 ? (
        <Box className="agent-masonry">
          {filteredPlaymates.map((agent) => (
            <Box key={agent.key} className="agent-masonry__item">
              <AgentIDCard
                agent={{
                  ...agent,
                  isFavorited: playmateFavorites.has(agent.key),
                }}
                onFavorite={() =>
                  setPlaymateFavorites((prev) => {
                    const next = new Set(prev);
                    if (next.has(agent.key)) {
                      next.delete(agent.key);
                    } else {
                      next.add(agent.key);
                    }
                    return next;
                  })
                }
                onClick={() => openDetail(agent)}
              />
            </Box>
          ))}
        </Box>
      ) : (
        <Paper radius="xl" p="xl" className="industrial-card">
          <Text ta="center" c="dimmed">
            没有符合当前筛选条件的陪玩 Agent。
          </Text>
        </Paper>
      )}
    </Stack>
  );

  // ============================
  // 渲染：DM Agent 视图
  // ============================

  const renderDMView = () => (
    <Stack gap="xl">
      {/* 筛选栏 */}
      <Paper radius="xl" p="lg" className="industrial-card">
        <Group align="end" wrap="wrap">
          <TextInput
            placeholder="搜索 DM Agent 名称 / 标签 / 风格"
            leftSection={<IconSearch size={16} />}
            value={query}
            onChange={(e) => setQuery(e.currentTarget.value)}
            radius="xl"
            style={{ flex: 1, minWidth: 220 }}
          />
          <Select
            data={dmPaceOptions}
            value={dmPace}
            onChange={(v) => setDmPace(v || "全部")}
            label="主持节奏"
            radius="xl"
            w={120}
          />
          <Select
            data={playTimeOptions}
            value={dmPlayTime}
            onChange={(v) => setDmPlayTime(v || "全部")}
            label="主持时段"
            radius="xl"
            w={120}
          />
        </Group>
      </Paper>

      {/* 金牌 DM 轮播 */}
      {goldDMs.length > 0 && (
        <AgentCarousel
          agents={goldDMs}
          activeSlide={dmSlide}
          onPrev={() =>
            setDmSlide((c) => (c - 1 + goldDMs.length) % goldDMs.length)
          }
          onNext={() => setDmSlide((c) => (c + 1) % goldDMs.length)}
          onSelectDot={setDmSlide}
          onCardClick={openDetail}
        />
      )}

      {/* 瀑布流 DM 名片 */}
      {filteredDMs.length > 0 ? (
        <Box className="agent-masonry">
          {filteredDMs.map((agent) => (
            <Box key={agent.key} className="agent-masonry__item">
              <AgentIDCard
                agent={{
                  ...agent,
                  isFavorited: dmFavorites.has(agent.key),
                }}
                onFavorite={() =>
                  setDmFavorites((prev) => {
                    const next = new Set(prev);
                    if (next.has(agent.key)) {
                      next.delete(agent.key);
                    } else {
                      next.add(agent.key);
                    }
                    return next;
                  })
                }
                onClick={() => openDetail(agent)}
              />
            </Box>
          ))}
        </Box>
      ) : (
        <Paper radius="xl" p="xl" className="industrial-card">
          <Text ta="center" c="dimmed">
            没有符合当前筛选条件的 DM Agent。
          </Text>
        </Paper>
      )}
    </Stack>
  );

  // ============================
  // 渲染：Agent 阵容搭配视图
  // ============================

  const renderEnsembleView = () => {
    const featuredEnsemble = filteredEnsembles[ensembleSlide % Math.max(filteredEnsembles.length, 1)];

    // 计算圆桌上座位的角度位置
    const getSeatPosition = (index: number, total: number) => {
      const angleOffset = -90; // 从顶部开始
      const angle = angleOffset + (360 / total) * index;
      const radius = 44; // %
      const rad = (angle * Math.PI) / 180;
      return {
        left: `${50 + radius * Math.cos(rad)}%`,
        top: `${50 + radius * Math.sin(rad)}%`,
      };
    };

    // 所有可选 Agent 列表（用于更换）
    const allAgents = [...companionAgents, ...dmAgents];

    return (
      <Stack gap="xl">
        {/* 阵容轮播 */}
        {filteredEnsembles.length > 0 && featuredEnsemble ? (
          <Paper
            radius="xl"
            className="agent-carousel"
            onClick={() => applyEnsemble(featuredEnsemble)}
          >
            <Stack justify="space-between" h="100%" className="agent-carousel__content">
              <Group justify="space-between" align="flex-start">
                <Group gap="xs">
                  <Badge color="red" variant="filled" leftSection={<IconStarFilled size={13} />}>
                    推荐阵容 · {ensembleSlide + 1}/{filteredEnsembles.length}
                  </Badge>
                  <Badge variant="light" color="orange">
                    {featuredEnsemble.type}
                  </Badge>
                </Group>
                <Group gap="xs">
                  <ActionIcon
                    variant="light"
                    color="gray"
                    radius="xl"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEnsembleSlide(
                        (c) => (c - 1 + filteredEnsembles.length) % filteredEnsembles.length
                      );
                    }}
                  >
                    <IconChevronLeft size={18} />
                  </ActionIcon>
                  <ActionIcon
                    variant="light"
                    color="gray"
                    radius="xl"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEnsembleSlide((c) => (c + 1) % filteredEnsembles.length);
                    }}
                  >
                    <IconChevronRight size={18} />
                  </ActionIcon>
                </Group>
              </Group>

              <Stack gap="sm" maw={610}>
                <Text className="monospace-label" size="xs" c="red.2">
                  recommended ensemble
                </Text>
                <Title order={1} fz={{ base: 38, md: 56 }} lh={0.95}>
                  {featuredEnsemble.name}
                </Title>
                <Text size="lg" c="gray.3" lh={1.7}>
                  {featuredEnsemble.description}
                </Text>
                <Group gap="xl">
                  <Group gap={6}>
                    <IconUsers size={17} />
                    <Text fw={700}>{featuredEnsemble.playerCount} 人</Text>
                  </Group>
                  <Text size="sm" c="red.2">
                    点击应用此阵容 →
                  </Text>
                </Group>
              </Stack>

              {/* 轮播指示器 */}
              <Group gap={7}>
                {filteredEnsembles.map((t, index) => (
                  <Box
                    key={t.key}
                    className={
                      index === ensembleSlide % filteredEnsembles.length
                        ? "agent-carousel__dot is-active"
                        : "agent-carousel__dot"
                    }
                    onClick={(e) => {
                      e.stopPropagation();
                      setEnsembleSlide(index);
                    }}
                  />
                ))}
              </Group>
            </Stack>
          </Paper>
        ) : null}

        {/* 搜索 + 人数选择 */}
        <Paper radius="xl" p="lg" className="industrial-card">
          <Stack gap="md">
            <Group align="end" wrap="wrap">
              <TextInput
                placeholder="搜索阵容名称 / 类型 / 描述"
                leftSection={<IconSearch size={16} />}
                value={query}
                onChange={(e) => setQuery(e.currentTarget.value)}
                radius="xl"
                style={{ flex: 1, minWidth: 220 }}
              />
              <Select
                data={ensembleTypeOptions}
                value={ensembleType}
                onChange={(v) => setEnsembleType(v || "全部")}
                label="阵容类型"
                radius="xl"
                w={140}
              />
            </Group>

            <Group gap="xs" align="center">
              <Text size="sm" fw={600} c="dimmed">
                剧本人数：
              </Text>
              {playerCountOptions.map((count) => (
                <Badge
                  key={count}
                  variant={playerCount === count ? "filled" : "light"}
                  color={playerCount === count ? "red" : "gray"}
                  size="lg"
                  style={{ cursor: "pointer" }}
                  onClick={() => handlePlayerCountChange(count)}
                >
                  {count} 人
                </Badge>
              ))}
            </Group>
          </Stack>
        </Paper>

        {/* 圆桌视角 */}
        <Paper radius="xl" p="xl" className="industrial-card">
          <Stack gap="lg" align="center">
            <Text className="monospace-label" size="xs" c="dimmed">
              round table · {playerCount} 人桌
            </Text>

            <Box className="round-table">
              {/* 桌面纹理 */}
              <Box className="round-table__surface" />

              {/* 座位 */}
              {ensembleSeats.map((agentKey, index) => {
                const pos = getSeatPosition(index, playerCount);
                const agent = companionAgents.find((a) => a.key === agentKey);
                const dmAgent = dmAgents.find((a) => a.key === agentKey);
                const resolvedAgent = agent || dmAgent;
                const isOccupied = !!resolvedAgent;

                // 头像颜色
                const avatarColors = [
                  "red", "orange", "grape", "blue", "cyan", "teal", "pink", "yellow",
                ];
                const colorIndex = agentKey.charCodeAt(0) % avatarColors.length;

                return (
                  <Box
                    key={`${index}-${agentKey}`}
                    className="round-table__seat"
                    style={{ left: pos.left, top: pos.top }}
                    onClick={() => handleSeatClick(index)}
                  >
                    <Avatar
                      size={52}
                      radius="xl"
                      color={isOccupied ? avatarColors[colorIndex] : "gray"}
                    >
                      {isOccupied ? resolvedAgent.name[0] : "?"}
                    </Avatar>
                    <Text size="xs" ta="center" mt={4} lineClamp={1}>
                      {isOccupied ? resolvedAgent.name : "空位"}
                    </Text>
                  </Box>
                );
              })}
            </Box>

            <Text size="sm" c="dimmed">
              点击座位可更换 Agent
            </Text>
          </Stack>
        </Paper>

        {/* 阵容模板卡片 */}
        <Paper radius="xl" p="lg" className="industrial-card">
          <Stack gap="md">
            <Group justify="space-between">
              <Stack gap={4}>
                <Text className="monospace-label" size="xs" c="dimmed">
                  ensemble templates
                </Text>
                <Title order={3}>推荐搭配</Title>
              </Stack>
              <Text size="sm" c="dimmed">
                点击「应用」一键填充到圆桌
              </Text>
            </Group>

            <Box
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                gap: "16px",
              }}
            >
              {filteredEnsembles
                .filter((t) => {
                  if (!query.trim()) return true;
                  const kw = query.trim().toLowerCase();
                  return (
                    t.name.toLowerCase().includes(kw) ||
                    t.type.toLowerCase().includes(kw) ||
                    t.description.toLowerCase().includes(kw)
                  );
                })
                .map((template) => (
                  <Card
                    key={template.key}
                    radius="lg"
                    className="tone-panel"
                    p="md"
                    style={{
                      cursor: "pointer",
                      borderColor:
                        playerCount === template.playerCount &&
                        ensembleSeats.every((k, i) => template.agentKeys[i] === k)
                          ? "rgba(250,82,82,0.4)"
                          : undefined,
                    }}
                    onClick={() => applyEnsemble(template)}
                  >
                    <Group justify="space-between" mb="sm">
                      <Text fw={800}>{template.name}</Text>
                      <Badge
                        variant="filled"
                        color={
                          template.type === "高玩局"
                            ? "red"
                            : template.type === "小白局"
                              ? "green"
                              : "orange"
                        }
                      >
                        {template.type}
                      </Badge>
                    </Group>
                    <Group gap={6} mb="sm">
                      <IconUsers size={14} />
                      <Text size="sm" c="dimmed">
                        {template.playerCount} 人
                      </Text>
                    </Group>
                    <Text size="sm" c="dimmed" lh={1.6} mb="md">
                      {template.description}
                    </Text>
                    <Group gap={4}>
                      {template.agentKeys.map((key) => (
                        <Avatar
                          key={key}
                          size={28}
                          radius="xl"
                          color={
                            ["red", "orange", "grape", "blue", "cyan", "teal", "pink", "yellow"][
                              key.charCodeAt(0) % 8
                            ]
                          }
                        >
                          {allAgentNames[key]?.[0] || "?"}
                        </Avatar>
                      ))}
                    </Group>
                  </Card>
                ))}
            </Box>
          </Stack>
        </Paper>

        {/* Agent 选择弹窗 */}
        <Modal
          opened={agentPickerOpen}
          onClose={() => {
            setAgentPickerOpen(false);
            setSelectedSeat(null);
          }}
          title="选择 Agent"
          radius="xl"
          overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
        >
          <Stack gap="sm">
            {allAgents.map((agent) => (
              <Card
                key={agent.key}
                radius="lg"
                className="tone-panel"
                p="md"
                style={{ cursor: "pointer" }}
                onClick={() => handleAgentPick(agent.key)}
              >
                <Group justify="space-between">
                  <Group gap="sm">
                    <Avatar
                      size={40}
                      radius="xl"
                      color={
                        ["red", "orange", "grape", "blue", "cyan", "teal", "pink", "yellow"][
                          agent.key.charCodeAt(0) % 8
                        ]
                      }
                    >
                      {agent.name[0]}
                    </Avatar>
                    <Stack gap={2}>
                      <Text fw={700}>{agent.name}</Text>
                      <Text size="xs" c="dimmed">
                        {agent.highlight}
                      </Text>
                    </Stack>
                  </Group>
                  <Badge variant="light" color="gray">
                    {"personality" in agent ? "陪玩" : "DM"}
                  </Badge>
                </Group>
              </Card>
            ))}
          </Stack>
        </Modal>
      </Stack>
    );
  };

  // ============================
  // 详情弹窗
  // ============================

  const renderDetailModal = () => {
    if (!detailAgent) return null;

    const isCompanion = "personality" in detailAgent;

    return (
      <Modal
        opened={detailOpen}
        onClose={() => setDetailOpen(false)}
        title={null}
        radius="xl"
        size="lg"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
      >
        <Paper radius="xl" className="industrial-card" p="lg">
          <Stack gap="md">
            <Group justify="space-between" align="flex-start">
              <Stack gap={4}>
                <Text className="monospace-label" size="xs" c="orange.3">
                  {isCompanion ? "companion detail" : "dm detail"}
                </Text>
                <Title order={2}>{detailAgent.name}</Title>
                <Text c="dimmed">{detailAgent.vibe}</Text>
                <Group gap="xs">
                  <Badge variant={detailAgent.registered ? "filled" : "light"} color={detailAgent.registered ? "teal" : "gray"}>
                    {detailAgent.registered ? "已注册后端节点" : "未注册后端节点"}
                  </Badge>
                  {detailAgent.personaKey ? (
                    <Badge variant="light" color="orange">
                      Persona: {detailAgent.personaKey}
                    </Badge>
                  ) : null}
                  {detailAgent.model ? (
                    <Badge variant="light" color="blue">
                      {detailAgent.model}
                    </Badge>
                  ) : null}
                </Group>
              </Stack>
              <Badge variant="light" color="red">
                {detailAgent.highlight}
              </Badge>
            </Group>

            <Box
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
                gap: "12px",
              }}
            >
              {isCompanion ? (
                <>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>说话 / 游戏风格</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {(detailAgent as CompanionAgent).style}
                    </Text>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>适合角色类型</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {(detailAgent as CompanionAgent).roleMatch}
                    </Text>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>能力标签</Text>
                    <Group gap="xs" mt="sm">
                      {(detailAgent as CompanionAgent).genius.map((tag) => (
                        <Badge key={tag} variant="light" color="orange">
                          {tag}
                        </Badge>
                      ))}
                    </Group>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>性格标签</Text>
                    <Group gap="xs" mt="sm">
                      {(detailAgent as CompanionAgent).personality.map((tag) => (
                        <Badge key={tag} variant="light" color="gray">
                          {tag}
                        </Badge>
                      ))}
                    </Group>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>recentTags</Text>
                    <Group gap="xs" mt="sm">
                      {((detailAgent as CompanionAgent).recentTags || []).map((tag) => (
                        <Badge key={tag} variant="light" color="blue">
                          {tag}
                        </Badge>
                      ))}
                      {((detailAgent as CompanionAgent).recentTags || []).length === 0 ? (
                        <Text size="sm" c="dimmed">暂无</Text>
                      ) : null}
                    </Group>
                  </Card>
                </>
              ) : (
                <>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>主持风格</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {(detailAgent as DMAgent).pace}节奏，偏向
                      {(detailAgent as DMAgent).focus.join(" / ")}。
                    </Text>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>控场 / 提示</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {(detailAgent as DMAgent).promptStyle}
                    </Text>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>擅长能力</Text>
                    <Group gap="xs" mt="sm">
                      {(detailAgent as DMAgent).strengths.map((tag) => (
                        <Badge key={tag} variant="light" color="orange">
                          {tag}
                        </Badge>
                      ))}
                    </Group>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>公平 / 违规</Text>
                    <Text size="sm" c="dimmed" mt="sm" lh={1.65}>
                      {(detailAgent as DMAgent).fairness}
                    </Text>
                  </Card>
                  <Card radius="lg" className="ambient-grid" p="md">
                    <Text fw={700}>recentTags</Text>
                    <Group gap="xs" mt="sm">
                      {((detailAgent as DMAgent).recentTags || []).map((tag) => (
                        <Badge key={tag} variant="light" color="blue">
                          {tag}
                        </Badge>
                      ))}
                      {((detailAgent as DMAgent).recentTags || []).length === 0 ? (
                        <Text size="sm" c="dimmed">暂无</Text>
                      ) : null}
                    </Group>
                  </Card>
                </>
              )}
            </Box>

            <Group justify="space-between" wrap="wrap">
              <Text size="sm" c="dimmed">
                {isCompanion
                  ? `擅长剧本：${(detailAgent as CompanionAgent).scriptTypes.join(" / ")}`
                  : `擅长期本：${(detailAgent as DMAgent).focus.join(" / ")}`}
              </Text>
              <Text size="sm" c="dimmed">
                {isCompanion
                  ? (detailAgent as CompanionAgent).history
                  : (detailAgent as DMAgent).runs}
              </Text>
            </Group>
            <Rating value={detailAgent.rating} fractions={2} readOnly />
            <Text size="sm" c="dimmed">
              推荐理由：
              {isCompanion
                ? (detailAgent as CompanionAgent).reason
                : "适合需要" +
                  (detailAgent as DMAgent).vibe +
                  "的桌子。"}
            </Text>
          </Stack>
        </Paper>
      </Modal>
    );
  };

  // ============================
  // 主渲染
  // ============================

  return (
    <StudioShell
      title="Agent 广场"
      subtitle="从性格、主动程度、擅长剧本到主持节奏，分别匹配陪玩 Agent 与 DM Agent。智能阵容搭配已移至游戏选角阶段。"
      eyebrow="agents / dm"
      stats={[
        { label: "陪玩 Agent", value: `${companionAgents.length}` },
        { label: "DM Agent", value: `${dmAgents.length}` },
        { label: "总收藏", value: `${playmateFavorites.size + dmFavorites.size}` },
        { label: "智能选角", value: "游戏内配置" },
      ]}
    >
      <Stack gap="xl">
        <Paper radius="xl" p="sm" className="industrial-card">
          <Text size="sm" c={backendError ? "red" : "dimmed"}>{backendStatus}</Text>
        </Paper>
        {/* 横向标签导航 */}
        {renderTabs()}

        {/* 内容区域 */}
        {activeTab === "playmate" && renderPlaymateView()}
        {activeTab === "dm" && renderDMView()}

        {/* 详情弹窗 */}
        {renderDetailModal()}
      </Stack>
    </StudioShell>
  );
}

export { AgentPanel };
