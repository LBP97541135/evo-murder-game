export type GamePhaseId =
  | "role-selection"
  | "script-reading"
  | "intro"
  | "search"
  | "discussion"
  | "vote";

export type PlayerStatus =
  | "空闲"
  | "正在发言"
  | "等待发言"
  | "必须回答"
  | "正在思考"
  | "申请私聊"
  | "私聊中"
  | "已完成";

export type GamePlayer = {
  id: string;
  name: string;
  role: string;
  publicIdentity: string;
  agent: boolean;
  color: string;
  status: PlayerStatus;
  tags: string[];
  background: string;
};

export type Evidence = {
  id: string;
  name: string;
  description: string;
  location: string;
  time: string;
  source: string;
  visibility: "仅自己" | "所有人" | "指定角色";
  icon: string;
};

export const GAME_PHASES: Array<{ id: GamePhaseId; label: string; shortLabel: string }> = [
  { id: "role-selection", label: "选角", shortLabel: "选角" },
  { id: "script-reading", label: "阅读剧本", shortLabel: "阅读" },
  { id: "intro", label: "公共讨论 1：自我介绍", shortLabel: "自我介绍" },
  { id: "search", label: "随机搜证", shortLabel: "搜证" },
  { id: "discussion", label: "公共讨论 2：线索交流", shortLabel: "线索交流" },
  { id: "vote", label: "推理投票", shortLabel: "投票" },
];

export const GAME_PLAYERS: GamePlayer[] = [
  {
    id: "dm",
    name: "雾港主理人",
    role: "DM",
    publicIdentity: "案件主持与规则裁定者",
    agent: true,
    color: "red",
    status: "空闲",
    tags: ["主持", "规则", "旁白"],
    background: "负责推进阶段、发布场景和裁定玩家行动。",
  },
  {
    id: "user",
    name: "林晓青",
    role: "周野",
    publicIdentity: "废弃厂区维修员",
    agent: false,
    color: "orange",
    status: "空闲",
    tags: ["熟悉门禁", "沉默寡言", "旧厂员工"],
    background: "十二年前曾负责厂区门禁维护，事故后离开锈铁大道。",
  },
  {
    id: "chen",
    name: "陈墨",
    role: "顾沉",
    publicIdentity: "事故档案管理员",
    agent: false,
    color: "teal",
    status: "等待发言",
    tags: ["档案", "谨慎", "时间线"],
    background: "保管事故档案，对缺失的值班记录格外敏感。",
  },
  {
    id: "crow",
    name: "白鸦",
    role: "沈禾",
    publicIdentity: "调查记者",
    agent: true,
    color: "blue",
    status: "正在思考",
    tags: ["推理", "追问", "线索整理"],
    background: "追踪锈铁大道旧案多年，擅长发现证词之间的矛盾。",
  },
  {
    id: "su",
    name: "苏颜",
    role: "周岚",
    publicIdentity: "夜班护士",
    agent: false,
    color: "grape",
    status: "空闲",
    tags: ["医疗", "目击者", "情绪敏锐"],
    background: "事故当晚在附近诊所值夜班，曾接诊过一位匿名伤者。",
  },
  {
    id: "echo",
    name: "回声",
    role: "秦野",
    publicIdentity: "厂区前工头",
    agent: true,
    color: "gray",
    status: "空闲",
    tags: ["现场", "工人关系", "行动派"],
    background: "熟悉厂区结构和旧员工关系，但对事故当晚闭口不谈。",
  },
];

export const ROLE_OPTIONS = GAME_PLAYERS.filter((player) => player.id !== "dm").map((player) => ({
  ...player,
  selectedBy: player.id === "chen" ? "陈墨" : player.agent ? player.name : undefined,
}));

export const SCRIPT_CHAPTERS = [
  {
    title: "第一章 · 重返锈铁大道",
    content:
      "十二年前，你负责维修厂区门禁。事故发生后，有人付钱让你删除一段记录。今晚，一张折断的访客卡重新出现，证明那次删除并不完整。",
  },
  {
    title: "第二章 · 被删除的三分钟",
    content:
      "事故当晚 22:41 至 22:44 的记录被人为覆盖。你知道只有维修终端能够执行覆盖，而终端钥匙当时并不在你手上。",
  },
  {
    title: "第三章 · 不能公开的交易",
    content:
      "失踪者曾承诺替你保守秘密。你的隐藏任务是找到原始记录，同时避免过早暴露自己参与删除数据的事实。",
  },
];

export const INITIAL_EVIDENCE: Evidence[] = [
  {
    id: "visitor-card",
    name: "折断的访客卡",
    description: "编号与失踪名单第三行一致，背面残留储物柜形状的锈迹。",
    location: "废弃宿舍门禁机",
    time: "22:47",
    source: "DM 场景事件",
    visibility: "仅自己",
    icon: "card",
  },
];

export const SEARCH_EVIDENCE: Evidence[] = [
  {
    id: "footprint",
    name: "103 室鞋印照片",
    description: "鞋底纹路来自停产多年的厂区安全靴，边缘沾有新鲜机油。",
    location: "103 室门口",
    time: "22:51",
    source: "随机搜证",
    visibility: "仅自己",
    icon: "footprint",
  },
  {
    id: "duty-sheet",
    name: "被涂改的值班表",
    description: "顾沉的签名被覆盖，纸张背面留下维修终端的压痕编号。",
    location: "旧值班室",
    time: "23:02",
    source: "随机搜证",
    visibility: "仅自己",
    icon: "file",
  },
  {
    id: "oil-key",
    name: "沾有机油的钥匙",
    description: "钥匙对应地下储物柜，齿槽里夹着一小段红色纤维。",
    location: "排水沟",
    time: "23:06",
    source: "随机搜证",
    visibility: "仅自己",
    icon: "key",
  },
];

export const INTRO_LINES: Record<string, string> = {
  user: "我是周野，十二年前负责这里的门禁维修。我回来只想弄清楚那段缺失记录是谁改的。",
  chen: "我是顾沉，事故档案由我保管。档案确实缺页，但缺失并不是最近才发生。",
  crow: "我是沈禾，调查记者。过去三年，我收到了七封署名不同、笔迹相同的匿名信。",
  su: "我是周岚，事故当晚在诊所值班。我见过一个不愿留下姓名的伤者。",
  echo: "我是秦野，前工头。厂区结构我最熟，但别指望我替任何人掩盖事实。",
};

export const PRIVATE_THREADS = [
  {
    id: "crow-thread",
    playerId: "crow",
    name: "白鸦",
    unread: 2,
    permission: "主动发言" as const,
    messages: [
      "访客卡编号与值班表压痕可能来自同一台机器。",
      "我建议暂时不要公开你参与过门禁维护。",
    ],
  },
  {
    id: "chen-thread",
    playerId: "chen",
    name: "陈墨",
    unread: 0,
    permission: "仅回答" as const,
    messages: ["如果你愿意交换门禁记录，我可以公开档案缺页时间。"],
  },
];
