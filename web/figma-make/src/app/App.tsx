// @ts-nocheck
import { useState } from "react";
import { Menu, X, Star, Users, Clock, ChevronRight, Skull, Flame, Eye, Lock, Play, Award } from "lucide-react";

const SCRIPTS = [
  {
    id: 1,
    title: "血色玫瑰庄园",
    subtitle: "The Crimson Rose Manor",
    genre: "情感",
    difficulty: 4,
    players: "6-8人",
    duration: "4-6小时",
    rating: 4.9,
    tag: "新品",
    tagColor: "bg-red-800",
    img: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=480&h=640&fit=crop&auto=format",
    desc: "1920年代上海，一场婚礼晚宴上，庄园女主人离奇死亡。每个来宾都藏着秘密，每段情感都暗流汹涌。",
  },
  {
    id: 2,
    title: "幽灵列车·午夜班次",
    subtitle: "Ghost Express: Midnight Run",
    genre: "恐怖",
    difficulty: 3,
    players: "5-7人",
    duration: "3-5小时",
    rating: 4.7,
    tag: "热门",
    tagColor: "bg-amber-900",
    img: "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=480&h=640&fit=crop&auto=format",
    desc: "午夜零时，一班从未到站的列车。乘客们醒来发现时间停止，车厢外是无尽黑暗，而车上有人已经死去。",
  },
  {
    id: 3,
    title: "深宫迷案·凤仪宫变",
    subtitle: "Palace Conspiracy",
    genre: "古风",
    difficulty: 5,
    players: "8-10人",
    duration: "6-8小时",
    rating: 4.8,
    tag: "史诗",
    tagColor: "bg-purple-900",
    img: "https://images.unsplash.com/photo-1538032746644-0212e812a9e7?w=480&h=640&fit=crop&auto=format",
    desc: "大明宫内，一夜之间皇后暴毙，三位皇子各怀鬼胎。后宫的权谋与情仇在这个命运之夜彻底爆发。",
  },
  {
    id: 4,
    title: "孤岛求生·第七天",
    subtitle: "Island Survival: Day Seven",
    genre: "推理",
    difficulty: 4,
    players: "5-6人",
    duration: "4-5小时",
    rating: 4.6,
    tag: "烧脑",
    tagColor: "bg-blue-900",
    img: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=480&h=640&fit=crop&auto=format",
    desc: "七名旅客在荒岛上困守七天。食物短缺、信任崩塌，第七天的黎明，有人用自己的方式结束了一切。",
  },
  {
    id: 5,
    title: "戏中戏·消失的演员",
    subtitle: "The Missing Actor",
    genre: "现代",
    difficulty: 3,
    players: "4-6人",
    duration: "3-4小时",
    rating: 4.5,
    tag: "入门",
    tagColor: "bg-green-900",
    img: "https://images.unsplash.com/photo-1503095396549-807759245b35?w=480&h=640&fit=crop&auto=format",
    desc: "剧团排练时，主角神秘消失。舞台上的戏与现实中的局，究竟哪一个才是真实？",
  },
  {
    id: 6,
    title: "赛博都市·断线人偶",
    subtitle: "CyberCity: Disconnected",
    genre: "科幻",
    difficulty: 5,
    players: "6-8人",
    duration: "5-7小时",
    rating: 4.9,
    tag: "限定",
    tagColor: "bg-cyan-900",
    img: "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=480&h=640&fit=crop&auto=format",
    desc: "2087年，人工智能觉醒的前夜。一个被植入人格芯片的机器人声称自己是凶手。真相还是程序？",
  },
];

const MODES = [
  {
    icon: Skull,
    title: "硬核推理",
    desc: "严密的逻辑链，海量线索，真实案件还原。适合推理爱好者与烧脑玩家。",
    color: "border-red-900",
    iconColor: "text-red-600",
  },
  {
    icon: Flame,
    title: "情感沉浸",
    desc: "深度角色扮演，情感羁绊与命运抉择并行。你将活成另一个人的一生。",
    color: "border-amber-900",
    iconColor: "text-amber-600",
  },
  {
    icon: Eye,
    title: "恐怖体验",
    desc: "心理恐惧、密室氛围、不明存在。胆小者请勿入场。",
    color: "border-purple-900",
    iconColor: "text-purple-500",
  },
  {
    icon: Lock,
    title: "秘密身份",
    desc: "每人身怀隐秘使命。欺骗、试探、联盟。最终只有一个真相。",
    color: "border-blue-900",
    iconColor: "text-blue-500",
  },
];

const TESTIMONIALS = [
  {
    name: "林晓雨",
    role: "资深玩家 · 200+场",
    text: "《血色玫瑰》让我哭了整整半小时，那个结局真的颠覆了我对剧本杀的认知。强烈推荐。",
    avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop&auto=format",
    stars: 5,
  },
  {
    name: "陈墨",
    role: "推理爱好者 · 80+场",
    text: "GM专业度极高，道具精良，灯光音效全程沉浸。《幽灵列车》那个反转太绝了。",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&auto=format",
    stars: 5,
  },
  {
    name: "苏颜",
    role: "新手玩家 · 15场",
    text: "第一次玩就选了入门款，GM引导很耐心。从此每周必来，剧本杀已经是我的精神依赖了。",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&auto=format",
    stars: 5,
  },
];

const GENRES = ["全部", "情感", "推理", "恐怖", "古风", "现代", "科幻"];

function StarRating({ count }: { count: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          size={12}
          className={i <= count ? "text-amber-400 fill-amber-400" : "text-muted-foreground"}
        />
      ))}
    </div>
  );
}

function DifficultyDots({ level }: { level: number }) {
  return (
    <div className="flex gap-1 items-center">
      {[1, 2, 3, 4, 5].map((i) => (
        <span
          key={i}
          className={`inline-block w-1.5 h-1.5 rounded-full ${i <= level ? "bg-accent" : "bg-muted"}`}
        />
      ))}
    </div>
  );
}

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeGenre, setActiveGenre] = useState("全部");
  const [activeTab, setActiveTab] = useState<"featured" | "new" | "popular">("featured");

  const filtered =
    activeGenre === "全部"
      ? SCRIPTS
      : SCRIPTS.filter((s) => s.genre === activeGenre);

  return (
    <div className="min-h-screen bg-background text-foreground" style={{ fontFamily: "'Crimson Pro', serif" }}>
      {/* ── NAV ── */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/90 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Skull size={22} className="text-accent" />
            <span
              className="text-xl font-bold tracking-widest text-foreground"
              style={{ fontFamily: "'Cinzel Decorative', serif", letterSpacing: "0.15em" }}
            >
              暗夜剧场
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            {["剧本库", "游戏模式", "预约场次", "排行榜", "关于我们"].map((item) => (
              <a
                key={item}
                href="#"
                className="hover:text-foreground transition-colors duration-200 tracking-wider"
              >
                {item}
              </a>
            ))}
          </nav>
          <div className="hidden md:flex items-center gap-3">
            <button className="text-sm text-muted-foreground hover:text-foreground transition-colors px-4 py-1.5">
              登录
            </button>
            <button className="text-sm bg-accent text-accent-foreground px-5 py-1.5 hover:bg-red-700 transition-colors tracking-wider">
              立即预约
            </button>
          </div>
          <button
            className="md:hidden text-muted-foreground"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
        {menuOpen && (
          <div className="md:hidden border-t border-border bg-card px-6 py-4 flex flex-col gap-4 text-sm">
            {["剧本库", "游戏模式", "预约场次", "排行榜", "关于我们"].map((item) => (
              <a key={item} href="#" className="text-muted-foreground hover:text-foreground">
                {item}
              </a>
            ))}
            <button className="w-full text-center bg-accent text-accent-foreground py-2 mt-2 tracking-wider">
              立即预约
            </button>
          </div>
        )}
      </header>

      {/* ── HERO ── */}
      <section className="relative pt-16 min-h-screen flex items-center overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1509023464722-18d996393ca8?w=1600&h=900&fit=crop&auto=format')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/85 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background/30" />

        <div className="relative max-w-7xl mx-auto px-6 py-24 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div
              className="inline-flex items-center gap-2 text-xs tracking-[0.3em] uppercase text-accent mb-6 border border-accent/30 px-3 py-1.5"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              <span className="w-1.5 h-1.5 bg-accent rounded-full animate-pulse" />
              2024全新剧本上线
            </div>
            <h1
              className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight text-foreground mb-6"
              style={{ fontFamily: "'Cinzel Decorative', serif", lineHeight: 1.15 }}
            >
              每一场游戏
              <br />
              <span className="text-accent">都是真实的谎言</span>
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed mb-8 max-w-md" style={{ fontStyle: "italic" }}>
              沉浸式角色扮演推理游戏——在精心设计的剧本世界中，每个玩家都是嫌疑人，也都是侦探。
              真相只有一个，而你的选择决定一切。
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="flex items-center gap-2 bg-accent text-accent-foreground px-8 py-3 hover:bg-red-700 transition-colors text-base tracking-wider">
                <Play size={16} />
                浏览剧本库
              </button>
              <button className="flex items-center gap-2 border border-border text-muted-foreground px-8 py-3 hover:border-accent/50 hover:text-foreground transition-colors text-base tracking-wider">
                了解玩法
                <ChevronRight size={16} />
              </button>
            </div>
            <div className="mt-12 flex gap-8 text-center">
              {[
                { val: "200+", label: "精品剧本" },
                { val: "50,000+", label: "玩家用户" },
                { val: "4.9", label: "综合评分" },
              ].map(({ val, label }) => (
                <div key={label}>
                  <div
                    className="text-2xl font-bold text-foreground"
                    style={{ fontFamily: "'Cinzel Decorative', serif" }}
                  >
                    {val}
                  </div>
                  <div className="text-xs text-muted-foreground tracking-widest mt-0.5">{label}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="hidden md:block" />
        </div>
      </section>

      {/* ── SCRIPTS ── */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <p
              className="text-xs tracking-[0.3em] uppercase text-accent mb-2"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Script Library
            </p>
            <h2
              className="text-3xl md:text-4xl font-bold text-foreground"
              style={{ fontFamily: "'Cinzel Decorative', serif" }}
            >
              精选剧本
            </h2>
          </div>
          <div className="flex gap-1">
            {(["featured", "new", "popular"] as const).map((tab) => {
              const labels = { featured: "编辑精选", new: "最新上线", popular: "热门榜单" };
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`text-sm px-4 py-1.5 transition-colors tracking-wider ${
                    activeTab === tab
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {labels[tab]}
                </button>
              );
            })}
          </div>
        </div>

        {/* Genre Filter */}
        <div className="flex gap-2 flex-wrap mb-8">
          {GENRES.map((g) => (
            <button
              key={g}
              onClick={() => setActiveGenre(g)}
              className={`text-sm px-4 py-1 border transition-colors tracking-wider ${
                activeGenre === g
                  ? "border-accent text-accent"
                  : "border-border text-muted-foreground hover:border-accent/40 hover:text-foreground"
              }`}
              style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.75rem" }}
            >
              {g}
            </button>
          ))}
        </div>

        {/* Script Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((script) => (
            <div
              key={script.id}
              className="group relative bg-card border border-border hover:border-accent/40 transition-all duration-300 overflow-hidden cursor-pointer"
            >
              <div className="relative h-64 overflow-hidden bg-secondary">
                <img
                  src={script.img}
                  alt={script.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-card via-card/20 to-transparent" />
                <span
                  className={`absolute top-3 left-3 text-xs text-white px-2 py-0.5 ${script.tagColor} tracking-widest`}
                  style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.65rem" }}
                >
                  {script.tag}
                </span>
                <span
                  className="absolute top-3 right-3 text-xs text-muted-foreground border border-border px-2 py-0.5 bg-card/80 tracking-widest"
                  style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.65rem" }}
                >
                  {script.genre}
                </span>
              </div>
              <div className="p-5">
                <h3
                  className="text-lg font-bold text-foreground mb-0.5 group-hover:text-accent transition-colors"
                  style={{ fontFamily: "'Cinzel Decorative', serif", fontSize: "1rem" }}
                >
                  {script.title}
                </h3>
                <p className="text-xs text-muted-foreground mb-3 tracking-wider italic">
                  {script.subtitle}
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed mb-4" style={{ fontSize: "0.875rem" }}>
                  {script.desc}
                </p>
                <div className="flex items-center justify-between pt-3 border-t border-border">
                  <div className="flex items-center gap-4 text-xs text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                    <span className="flex items-center gap-1">
                      <Users size={11} />
                      {script.players}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock size={11} />
                      {script.duration}
                    </span>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StarRating count={Math.round(script.rating)} />
                    <DifficultyDots level={script.difficulty} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-10">
          <button className="text-sm border border-border text-muted-foreground px-10 py-2.5 hover:border-accent/50 hover:text-foreground transition-colors tracking-widest">
            查看全部剧本 →
          </button>
        </div>
      </section>

      {/* ── MODES ── */}
      <section className="border-t border-border bg-secondary/30">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center mb-14">
            <p
              className="text-xs tracking-[0.3em] uppercase text-accent mb-2"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Game Modes
            </p>
            <h2
              className="text-3xl md:text-4xl font-bold text-foreground"
              style={{ fontFamily: "'Cinzel Decorative', serif" }}
            >
              四种沉浸体验
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {MODES.map((mode) => (
              <div
                key={mode.title}
                className={`group p-6 border ${mode.color} bg-card hover:bg-secondary transition-colors duration-300 cursor-pointer`}
              >
                <mode.icon size={28} className={`${mode.iconColor} mb-5`} />
                <h3
                  className="text-base font-bold text-foreground mb-3"
                  style={{ fontFamily: "'Cinzel Decorative', serif", fontSize: "0.9rem" }}
                >
                  {mode.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{mode.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW TO PLAY ── */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <p
              className="text-xs tracking-[0.3em] uppercase text-accent mb-2"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              How To Play
            </p>
            <h2
              className="text-3xl md:text-4xl font-bold text-foreground mb-6"
              style={{ fontFamily: "'Cinzel Decorative', serif" }}
            >
              如何开始<br />你的第一局
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-10">
              无论你是剧本杀老手还是初次体验，暗夜剧场都为你准备了完善的引导体系与专业DM团队，
              确保每一局都是难忘的故事。
            </p>
            <div className="space-y-6">
              {[
                { step: "01", title: "选择剧本", desc: "按难度、类型、人数筛选，找到最适合你们小队的故事。" },
                { step: "02", title: "预约场次", desc: "选择时间，填写人数，我们将为你安排专属DM和场地。" },
                { step: "03", title: "领取角色", desc: "到场后领取专属剧本，进入角色设定，开始你的表演。" },
                { step: "04", title: "揭开真相", desc: "收集线索，展开调查，在游戏结束时大胆公布你的答案。" },
              ].map(({ step, title, desc }) => (
                <div key={step} className="flex gap-5 items-start">
                  <span
                    className="text-2xl font-bold text-accent/40 shrink-0 mt-0.5"
                    style={{ fontFamily: "'Cinzel Decorative', serif" }}
                  >
                    {step}
                  </span>
                  <div>
                    <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
                    <p className="text-sm text-muted-foreground">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="relative">
            <div className="relative overflow-hidden bg-secondary h-[520px]">
              <img
                src="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=700&h=900&fit=crop&auto=format"
                alt="游戏体验"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-card/60 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="border border-accent/30 bg-card/80 backdrop-blur-sm p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <Award size={16} className="text-accent" />
                    <span className="text-xs tracking-widest text-accent" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                      GAME MASTER CERTIFIED
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    所有DM经过200+小时专业培训，持证上岗，确保每场游戏都完美呈现。
                  </p>
                </div>
              </div>
            </div>
            <div className="absolute -top-3 -right-3 w-full h-full border border-accent/20 -z-10" />
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ── */}
      <section className="border-t border-border bg-secondary/20">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center mb-14">
            <p
              className="text-xs tracking-[0.3em] uppercase text-accent mb-2"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Player Reviews
            </p>
            <h2
              className="text-3xl md:text-4xl font-bold text-foreground"
              style={{ fontFamily: "'Cinzel Decorative', serif" }}
            >
              玩家心声
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t) => (
              <div key={t.name} className="bg-card border border-border p-6 hover:border-accent/30 transition-colors">
                <StarRating count={t.stars} />
                <p
                  className="text-base text-foreground/90 leading-relaxed my-4"
                  style={{ fontStyle: "italic" }}
                >
                  "{t.text}"
                </p>
                <div className="flex items-center gap-3 pt-4 border-t border-border">
                  <img
                    src={t.avatar}
                    alt={t.name}
                    className="w-9 h-9 rounded-full object-cover grayscale"
                  />
                  <div>
                    <div className="text-sm font-semibold text-foreground">{t.name}</div>
                    <div
                      className="text-xs text-muted-foreground"
                      style={{ fontFamily: "'JetBrains Mono', monospace" }}
                    >
                      {t.role}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1600&h=600&fit=crop&auto=format')",
          }}
        />
        <div className="absolute inset-0 bg-background/85" />
        <div className="relative max-w-7xl mx-auto px-6 py-24 text-center">
          <h2
            className="text-4xl md:text-5xl font-bold text-foreground mb-4"
            style={{ fontFamily: "'Cinzel Decorative', serif" }}
          >
            你的故事，今晚开始
          </h2>
          <p className="text-muted-foreground text-lg mb-8 max-w-xl mx-auto" style={{ fontStyle: "italic" }}>
            加入超过五万名玩家，在暗夜剧场活出另一段人生。每周新场次，每场独一无二。
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-accent text-accent-foreground px-10 py-3 text-base hover:bg-red-700 transition-colors tracking-widest">
              立即预约场次
            </button>
            <button className="border border-border text-muted-foreground px-10 py-3 text-base hover:border-accent/50 hover:text-foreground transition-colors tracking-widest">
              成为会员
            </button>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="border-t border-border bg-card">
        <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-3">
              <Skull size={18} className="text-accent" />
              <span
                className="text-sm font-bold tracking-widest text-foreground"
                style={{ fontFamily: "'Cinzel Decorative', serif" }}
              >
                暗夜剧场
              </span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              中国领先的沉浸式剧本杀体验平台。精品剧本、专业DM、极致沉浸。
            </p>
          </div>
          {[
            { title: "剧本", links: ["情感向", "推理向", "恐怖向", "古风向", "科幻向"] },
            { title: "服务", links: ["在线预约", "团购优惠", "企业团建", "剧本定制"] },
            { title: "关于", links: ["关于我们", "加盟合作", "招贤纳士", "联系我们"] },
          ].map(({ title, links }) => (
            <div key={title}>
              <h4
                className="text-xs font-semibold text-foreground mb-3 tracking-widest"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                {title}
              </h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link}>
                    <a href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t border-border">
          <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col sm:flex-row justify-between items-center gap-2">
            <p
              className="text-xs text-muted-foreground"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              © 2024 暗夜剧场. All rights reserved.
            </p>
            <p
              className="text-xs text-muted-foreground"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              沪ICP备2024000000号
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
