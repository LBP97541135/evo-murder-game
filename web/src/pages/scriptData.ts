export type ScriptCard = {
  id: string;
  title: string;
  subtitle: string;
  genre: "情感本" | "推理本" | "机制本" | "阵营本";
  difficulty: "入门" | "进阶" | "硬核";
  players: string;
  playerCount: number;
  duration: string;
  rating: number;
  description: string;
  details: string;
  cover: string;
  tags: string[];
  audienceTags: string[];
  hot: boolean;
  newArrival: boolean;
  recommended: boolean;
  friendsPlayed: boolean;
  agentFit: string[];
  roles: string[];
};

export const scripts: ScriptCard[] = [
  {
    id: "xiutie-avenue-missing-three-minutes",
    title: "锈铁大道",
    subtitle: "The Rusted Avenue",
    genre: "推理本",
    difficulty: "进阶",
    players: "4-6人",
    playerCount: 6,
    duration: "4-5小时",
    rating: 4.9,
    description: "停摆工厂、老旧宿舍与失踪名单被压在同一座锈色街区里，真相沿着管道缓慢回流。",
    details: "玩家将进入一座被废弃工业区包围的小镇。六名角色都与十二年前的事故有关，而一份重新出现的值班名单让彼此的证词开始崩塌。剧本强调线索还原、时间线拼接和多轮反转。",
    cover: "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1200&h=1500&fit=crop&auto=format",
    tags: ["工业氛围", "线索链", "反转强", "高复盘"],
    audienceTags: ["推理爱好者", "熟人组队", "喜欢反转", "沉浸玩家"],
    hot: true,
    newArrival: true,
    recommended: true,
    friendsPlayed: true,
    agentFit: ["雾港主理人", "铁幕裁判", "白鸦陪玩"],
    roles: ["林砾", "周岚", "顾沉", "秦野", "沈禾", "陆弦"],
  },
  {
    id: "black-archive",
    title: "黑箱档案馆",
    subtitle: "Black Archive",
    genre: "情感本",
    difficulty: "入门",
    players: "6-7人",
    playerCount: 7,
    duration: "5-6小时",
    rating: 4.8,
    description: "灰尘、烛火与被封存的家族信件，把每个人拽回一段难以解释的旧日往事。",
    details: "一座即将关闭的私人档案馆收到匿名捐赠，七封信分别写给七位从未见过彼此的人。随着馆藏开放，他们发现自己的家庭记忆来自同一个被隐瞒的夜晚。",
    cover: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200&h=1500&fit=crop&auto=format",
    tags: ["高沉浸", "氛围感", "情绪拉扯", "新手友好"],
    audienceTags: ["新手玩家", "情感体验", "朋友聚会", "轻推理"],
    hot: true,
    newArrival: false,
    recommended: true,
    friendsPlayed: false,
    agentFit: ["深井讲述者", "暮烬引导员", "纸鸢陪玩"],
    roles: ["许知白", "程见夏", "闻舟", "苏杳", "江临", "唐穗", "宋遥"],
  },
  {
    id: "mirror-parade",
    title: "镜面游行",
    subtitle: "Mirror Parade",
    genre: "阵营本",
    difficulty: "硬核",
    players: "7-9人",
    playerCount: 8,
    duration: "6小时",
    rating: 4.7,
    description: "面具、反光和舞台灯把每次发言切成碎片，所有阵营都在互相借力与拆台。",
    details: "城市庆典前夜，八位游行委员会成员被困在镜厅。每个人拥有公开身份、秘密立场与一次改变规则的机会，胜负取决于信息交换和阵营判断。",
    cover: "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=1200&h=1500&fit=crop&auto=format",
    tags: ["阵营博弈", "控场强", "表演位", "高对抗"],
    audienceTags: ["桌游老手", "社交玩家", "阵营博弈", "高强度对抗"],
    hot: true,
    newArrival: true,
    recommended: false,
    friendsPlayed: true,
    agentFit: ["铁幕裁判", "节拍室主理", "钩索陪玩"],
    roles: ["白面", "红隼", "司钟人", "玻璃匠", "礼官", "无名客", "领舞者", "守门人"],
  },
  {
    id: "salt-ward",
    title: "盐雾病房",
    subtitle: "Salt Ward",
    genre: "推理本",
    difficulty: "入门",
    players: "5-6人",
    playerCount: 6,
    duration: "3.5小时",
    rating: 4.6,
    description: "潮湿长廊与失效监控构成一场节奏温和、适合新手入门的推理练习。",
    details: "临海疗养院在台风夜失去供电，一名患者离奇消失。玩家需要在有限场景中核对病历、监控和口供，完成清晰但不失悬念的真相还原。",
    cover: "https://images.unsplash.com/photo-1516738901171-8eb4fc13bd20?w=1200&h=1500&fit=crop&auto=format",
    tags: ["新手友好", "节奏清晰", "信息适中"],
    audienceTags: ["第一次玩", "短时体验", "轻度恐怖", "小型聚会"],
    hot: false,
    newArrival: true,
    recommended: true,
    friendsPlayed: false,
    agentFit: ["暮烬引导员", "雾港主理人", "回声陪玩"],
    roles: ["值夜医生", "护士长", "摄影师", "病人家属", "维修工", "档案员"],
  },
  {
    id: "wolf-assembly",
    title: "狼群集会",
    subtitle: "Wolf Assembly",
    genre: "机制本",
    difficulty: "进阶",
    players: "6-8人",
    playerCount: 8,
    duration: "4.5小时",
    rating: 4.5,
    description: "围绕营地资源与夜巡制度展开博弈，角色推进与资源调度都要算得很细。",
    details: "极寒营地即将断粮，成员必须在夜巡、交易和公共建设之间分配行动点。隐藏目标会不断改变合作关系，适合喜欢资源机制与临场谈判的玩家。",
    cover: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1200&h=1500&fit=crop&auto=format",
    tags: ["机制感", "资源调度", "夜谈博弈"],
    audienceTags: ["机制玩家", "策略爱好者", "稳定车队", "谈判型玩家"],
    hot: false,
    newArrival: false,
    recommended: true,
    friendsPlayed: true,
    agentFit: ["节拍室主理", "铁幕裁判", "燧石陪玩"],
    roles: ["哨兵", "猎人", "医师", "书记员", "炊事长", "向导", "商人", "流亡者"],
  },
  {
    id: "paper-cathedral",
    title: "纸穹教堂",
    subtitle: "Paper Cathedral",
    genre: "情感本",
    difficulty: "硬核",
    players: "6-8人",
    playerCount: 7,
    duration: "5.5小时",
    rating: 4.9,
    description: "一座被封死的旧教堂正在吞没记忆，人物关系和信仰冲突同时发酵。",
    details: "七名故人因一场纪念仪式重返纸穹教堂。被删改的唱诗册、空白照片和不同版本的告解，将把他们带向关于牺牲与记忆的最终选择。",
    cover: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1200&h=1500&fit=crop&auto=format",
    tags: ["重氛围", "高情绪", "禁忌感"],
    audienceTags: ["情感本老手", "重沉浸", "长线体验", "关系推演"],
    hot: false,
    newArrival: true,
    recommended: false,
    friendsPlayed: true,
    agentFit: ["深井讲述者", "暮烬引导员", "夜航陪玩"],
    roles: ["司祭", "修复师", "唱诗人", "建筑师", "记者", "守墓人", "归乡者"],
  },
];
