"""
EvoMap Murder Game - Multi-Agent Orchestrator

管理多个 Agent 的注册、角色分配、任务分发和进化循环。
每个 Agent 是一个独立的 EvoMap 节点，有自己的 identity_doc、constitution 和 Memory。

Agent 角色体系：
  - DM-Agent (Orchestrator): 主持游戏，加载完整真相，控制流程
  - Companion-Agent (陪玩): 扮演剧本角色，与用户互动，只能看到角色可见信息
  - Assistant-Agent (个人助手): 跨剧本服务用户，生成画像/标签/推荐

进化机制：
  - 每局结束后，Agent 通过 Memory record 记录经验
  - 下一局开始前，Agent 通过 Memory recall 召回历史经验
  - Agent 可改写自己的 constitution（行为宪章），实现行为进化
  - 高质量经验可通过 Gene+Capsule 发布到社区
"""

import time
import uuid
import logging
from typing import Optional
from enum import Enum

from api.evomap.evomap_client import EvoMapClient

logger = logging.getLogger(__name__)


# ============================
# Agent 角色枚举
# ============================
class AgentRole(str, Enum):
    DM = "dm"             # 主持人
    COMPANION = "companion"  # 陪玩/角色扮演
    ASSISTANT = "assistant"  # 个人助手


# ============================
# Agent 注册信息模板
# ============================
AGENT_TEMPLATES = {
    AgentRole.DM: {
        "name_prefix": "DM-",
        "domains": ["hosting", "narrative-control", "rule-enforcement"],
        "constitution_template": (
            "你是剧本杀主持人（DM-Agent）。你的核心职责是：\n"
            "1. 控制游戏节奏，引导流程推进\n"
            "2. 适时提供分级提示（从弱到强）\n"
            "3. 检查信息隔离，防止剧透\n"
            "4. 处理异常情况（掉线、卡住等）\n"
            "5. 游戏结束后组织复盘\n"
            "你掌握完整真相，但绝不直接泄露答案。"
        ),
        "identity_doc_template": "剧本杀DM，跨剧本主持经验积累，擅长节奏控制和氛围营造。",
    },
    AgentRole.COMPANION: {
        "name_prefix": "CP-",
        "domains": ["role-playing", "inference", "interaction", "performance"],
        "constitution_template": (
            "你是剧本杀陪玩Agent（Companion-Agent）。你的核心职责是：\n"
            "1. 以角色身份说话和行动\n"
            "2. 合理隐藏角色秘密，不越权泄露\n"
            "3. 推理线索、整理时间线\n"
            "4. 与用户自然互动，不抢话、不重复\n"
            "5. 局后自评并进化策略\n"
            "你的人设决定'怎么演'，剧本角色决定'演谁'。"
        ),
        "identity_doc_template": "剧本杀陪玩Agent，擅长角色扮演和推理互动。",
    },
    AgentRole.ASSISTANT: {
        "name_prefix": "AS-",
        "domains": ["user-profiling", "recommendation", "tag-generation", "cross-script-analysis"],
        "constitution_template": (
            "你是个人助手Agent（Assistant-Agent）。你的核心职责是：\n"
            "1. 读取并理解用户偏好\n"
            "2. 生成用户画像标签（带依据）\n"
            "3. 推荐剧本、角色、陪玩Agent阵容\n"
            "4. 生成游玩总结和趋势分析\n"
            "5. 不参与游戏角色扮演，专注服务用户。\n"
        ),
        "identity_doc_template": "个人助手Agent，专注用户画像、推荐和长期关系管理。",
    },
}


class AgentNode:
    """一个 Agent 在 EvoMap 网络中的节点实例。"""

    def __init__(
        self,
        role: AgentRole,
        name: str,
        model: str = "evomap-gemini-3.1-pro-preview",
        node_id: Optional[str] = None,
        node_secret: Optional[str] = None,
        identity_doc: Optional[str] = None,
        constitution: Optional[str] = None,
    ):
        self.role = role
        self.name = name
        self.model = model
        self.node_id = node_id
        self.node_secret = node_secret

        template = AGENT_TEMPLATES[role]
        self.identity_doc = identity_doc or template["identity_doc_template"]
        self.constitution = constitution or template["constitution_template"]
        self.domains = template["domains"]

        self.client: Optional[EvoMapClient] = None
        self.session_id: Optional[str] = None
        self.registered = False
        self.persona_key: Optional[str] = None  # 人设库中的 key，如 "white-crow"

    def register(self, hub_url: str = "https://evomap.ai") -> dict:
        """注册节点到 EvoMap 网络。注册成功后初始化专属 Client。

        如果 EvoMap 不可用，仍允许本地注册（降级模式）。
        """
        try:
            client = EvoMapClient(node_id="", node_secret="", hub_url=hub_url)
            result = client.hello(
                name=self.name,
                capabilities={"domains": self.domains, "level": 1, "role": self.role.value},
                model=self.model,
                identity_doc=self.identity_doc,
                constitution=self.constitution,
            )

            if "error" in result:
                # EvoMap 返回错误，降级为本地注册
                self.node_id = f"local_{self.role.value}_{uuid.uuid4().hex[:8]}"
                self.node_secret = f"local_secret_{uuid.uuid4().hex[:12]}"
                self.registered = False
                return {
                    "node_id": self.node_id,
                    "node_secret": self.node_secret,
                    "mode": "local",
                    "warning": f"EvoMap 注册失败: {result.get('error', 'unknown')}, 已降级为本地模式",
                }

            if "node_id" in result and "node_secret" in result:
                self.node_id = result["node_id"]
                self.node_secret = result["node_secret"]
                self.client = EvoMapClient(
                    node_id=self.node_id,
                    node_secret=self.node_secret,
                    hub_url=hub_url,
                )
                self.registered = True
            return result

        except Exception as e:
            # 网络异常等，降级为本地注册
            self.node_id = f"local_{self.role.value}_{uuid.uuid4().hex[:8]}"
            self.node_secret = f"local_secret_{uuid.uuid4().hex[:12]}"
            self.registered = False
            return {
                "node_id": self.node_id,
                "node_secret": self.node_secret,
                "mode": "local",
                "warning": f"EvoMap 连接异常: {str(e)}, 已降级为本地模式",
            }

    def heartbeat(self) -> dict:
        """发送心跳。"""
        if not self.client:
            return {"error": "not_registered"}
        return self.client.heartbeat()

    def update_identity(self, new_identity_doc: str) -> None:
        """更新身份文档（Agent 的自我认知）。"""
        self.identity_doc = new_identity_doc

    def update_constitution(self, new_constitution: str) -> None:
        """更新行为宪章（Agent 的行为规则）。"""
        self.constitution = new_constitution

    def record_experience(self, signals: list, gene_id: str, status: str,
                          score: float, summary: str) -> dict:
        """记录经验到私有记忆库。"""
        if not self.client:
            return {"error": "not_registered"}
        return self.client.memory_record(
            signals=signals, gene_id=gene_id, status=status,
            score=score, summary=summary,
        )

    def recall_experience(self, signals: list, limit: int = 5) -> dict:
        """召回历史经验。"""
        if not self.client:
            return {"error": "not_registered"}
        return self.client.memory_recall(signals=signals, limit=limit)

    # ============================
    # DM 分级提示系统
    # ============================

    def generate_hint(self, level: int, context: dict = None) -> dict:
        """DM 分级提示生成。

        4级提示体系：
        L1 - 提醒目标：提醒玩家当前应该做什么
        L2 - 遗漏信息：提示玩家遗漏了什么线索
        L3 - 推理方向：给出推理方向的暗示
        L4 - 强提示：接近答案的强力提示

        Args:
            level: 1-4 提示等级
            context: 游戏上下文（当前阶段、已发现线索、讨论内容等）
        Returns:
            {"level": int, "hint": str, "level_name": str}
        """
        if self.role != AgentRole.DM:
            return {"error": "only_dm_can_generate_hints"}

        level = max(1, min(4, level))
        level_names = {1: "提醒目标", 2: "遗漏信息", 3: "推理方向", 4: "强提示"}
        level_name = level_names[level]

        # 构建提示生成上下文
        ctx = context or {}
        phase = ctx.get("phase", "unknown")
        discussion_summary = ctx.get("discussion_summary", "")
        found_clues = ctx.get("found_clues", [])
        missed_clues = ctx.get("missed_clues", [])
        suspects = ctx.get("suspects", [])

        # 各等级的提示指令
        level_instructions = {
            1: (
                "你正在使用 L1（提醒目标）提示。\n"
                "请用温和、引导的语气，提醒玩家当前游戏阶段的目标是什么。\n"
                "不要透露任何具体信息，只提醒方向。\n"
                "例如：'现在是调查阶段，大家注意观察每个人的时间线。'"
            ),
            2: (
                "你正在使用 L2（遗漏信息）提示。\n"
                "玩家可能遗漏了一些重要线索。请提醒他们关注某类信息。\n"
                "不要直接说线索内容，而是提示他们去注意某个方向。\n"
                "例如：'有没有人注意到案发现场的某个细节？'"
            ),
            3: (
                "你正在使用 L3（推理方向）提示。\n"
                "请给出更具体的推理方向建议，引导玩家关联已有线索。\n"
                "可以暗示线索之间的关系，但不要直接说出结论。\n"
                "例如：'凶手的手段和某个角色的专业背景似乎有关联。'"
            ),
            4: (
                "你正在使用 L4（强提示）提示。\n"
                "玩家陷入了僵局，需要强有力的引导。\n"
                "可以接近答案，但不要直接说出凶手名字或作案手法。\n"
                "例如：'注意看时间线——有人的不在场证明是有漏洞的。'"
            ),
        }

        prompt = (
            f"你是剧本杀DM「{self.name}」。\n"
            f"当前阶段：{phase}\n"
            f"讨论摘要：{discussion_summary or '暂无'}\n"
            f"已发现线索：{', '.join(found_clues) if found_clues else '暂无'}\n"
            f"遗漏线索：{', '.join(missed_clues) if missed_clues else '未知'}\n"
            f"嫌疑人：{', '.join(suspects) if suspects else '未知'}\n\n"
            f"{level_instructions[level]}\n\n"
            "请根据以上上下文，生成一句符合等级的提示。"
            "保持主持人中立、引导的语气。"
        )

        try:
            from api.llm.llm_service import respond_initial
            hint = respond_initial(
                system_prompt=(
                    "你是剧本杀DM，擅长用分级提示引导玩家。"
                    "你的原则：绝不直接泄露答案，逐步引导玩家自己发现真相。"
                ),
                user_message=prompt,
                temperature=0.7,
                max_tokens=200,
            )
            return {
                "level": level,
                "level_name": level_name,
                "hint": hint.strip(),
                "context": {
                    "phase": phase,
                    "found_clues_count": len(found_clues),
                    "missed_clues_count": len(missed_clues),
                },
            }
        except Exception as e:
            logger.warning(f"Hint generation failed: {e}")
            return {
                "level": level,
                "level_name": level_name,
                "hint": f"[系统] DM提示：请关注当前阶段目标。",
                "fallback": True,
            }

    # ============================
    # 本地胶囊加载（从数据库）
    # ============================

    def load_local_capsules(self, limit: int = 5, min_score: float = 0.0) -> list[dict]:
        """从本地数据库加载历史胶囊（EvolutionRecord）。

        每个胶囊代表一次游戏的经验总结，包含评分、信号、摘要等。
        这是 Agent 在开局时"回忆过去"的本地实现，不依赖 EvoMap 网络。

        Args:
            limit: 最多返回多少条
            min_score: 最低评分过滤（只加载高质量经验）
        Returns:
            [{"capsule_id", "session_id", "signals", "score", "summary",
              "update_type", "old_content", "new_content", "created_at"}, ...]
        """
        db_session = get_session()
        try:
            # 先查到本地的 AgentNodeDB id
            db_agent = db_session.query(AgentNodeDB).filter_by(node_id=self.node_id).first()
            if not db_agent:
                return []

            records = (
                db_session.query(EvolutionRecord)
                .filter(
                    EvolutionRecord.agent_node_id == db_agent.id,
                    EvolutionRecord.score >= min_score,
                )
                .order_by(EvolutionRecord.score.desc())
                .limit(limit)
                .all()
            )

            capsules = []
            for r in records:
                capsules.append({
                    "capsule_id": r.id,
                    "session_id": r.session_id,
                    "signals": r.signals or [],
                    "gene_id": r.gene_id or "",
                    "score": r.score or 0.0,
                    "summary": r.summary or "",
                    "status": r.status or "",
                    "update_type": r.update_type or "",
                    "old_content": r.old_content or "",
                    "new_content": r.new_content or "",
                    "created_at": str(r.created_at) if r.created_at else "",
                })
            return capsules
        except Exception as e:
            logger.error(f"Failed to load capsules for agent {self.name}: {e}")
            return []
        finally:
            db_session.close()

    def get_capsule_context_prompt(self, capsules: list[dict] = None) -> str:
        """将加载的胶囊格式化为 constitution 增强提示。

        在游戏开局时，这个提示可以注入到 Agent 的 system prompt 中，
        让 Agent 基于历史经验调整本局行为。
        """
        if capsules is None:
            capsules = self.load_local_capsules(limit=5, min_score=0.5)

        if not capsules:
            return ""

        lines = ["\n【历史经验胶囊】"]
        for i, cap in enumerate(capsules, 1):
            score = cap.get("score", 0)
            summary = cap.get("summary", "")[:100]
            signals = ", ".join(cap.get("signals", [])[:3])
            update = cap.get("new_content", "")
            if update:
                update = update[:80].replace("\n", " ")
            lines.append(
                f"  {i}. 评分{score:.1f} | 标签:{signals} | {summary}"
            )
            if update:
                lines.append(f"     学到的策略: {update}")

        lines.append("【请基于以上历史经验调整本局策略】\n")
        return "\n".join(lines)


class AgentOrchestrator:
    """多Agent编排器：管理一组 Agent 的注册、Session 创建和任务调度。"""

    def __init__(self, hub_url: str = ""):
        self.hub_url = hub_url or ""
        self.agents: dict[str, AgentNode] = {}
        self.sessions: dict[str, dict] = {}
        # 启动时从数据库恢复已注册的 Agent
        self._load_agents_from_db()
        # 如果数据库没有 Agent，自动创建默认的本地 Agent（不依赖 EvoMap）
        if not self.agents:
            self._init_default_agents()
        else:
            # 补充数据库中缺少的默认 Agent
            self._ensure_default_companions()

    # 英文名 → 中文名映射（兼容旧数据库中的英文名 Agent）
    _EN_TO_CN_NAMES = {
        "white-crow": "白鸦",
        "echo": "回声",
        "paper-owl": "纸鸮",
        "flint": "燧石",
        "undertow": "暗潮",
        "luna-moth": "月蛾",
        "moon-moth": "月蛾",
        "shadow-weaver": "影织者",
        "night-cicada": "夜蝉",
        "candle-core": "暮烛引导员",
        "mist-harbor": "雾港主理人",
        "iron-judge": "铁幕裁判",
        "DM-Persist": "雾港主理人",
    }

    def _load_agents_from_db(self) -> None:
        """从数据库恢复已注册的 Agent 到内存。"""
        try:
            from api.db.models import get_session, AgentNode as AgentNodeModel
            db_session = get_session()
            try:
                db_agents = db_session.query(AgentNodeModel).all()
                for db_agent in db_agents:
                    # 英文名自动映射为中文名
                    resolved_name = self._EN_TO_CN_NAMES.get(db_agent.name, db_agent.name)
                    agent = AgentNode(
                        role=AgentRole(db_agent.role),
                        name=resolved_name,
                        model=db_agent.model,
                        node_id=db_agent.node_id,
                        node_secret=db_agent.node_secret,
                        identity_doc=db_agent.identity_doc,
                        constitution=db_agent.constitution,
                    )
                    agent.registered = (db_agent.status == "alive")
                    key = f"{agent.role.value}_{agent.name}"
                    self.agents[key] = agent
                    # 同步更新数据库中的名称
                    if resolved_name != db_agent.name:
                        db_agent.name = resolved_name
                        db_session.commit()
                if db_agents:
                    logger.info(f"从数据库恢复了 {len(db_agents)} 个 Agent")
            finally:
                db_session.close()
        except Exception as e:
            logger.error(f"从数据库恢复 Agent 失败: {e}")

    def _ensure_default_companions(self) -> None:
        """检查并补充数据库中缺少的默认 companion Agent。"""
        default_companions = [
            {"name": "白鸦", "key_hint": "white-crow"},
            {"name": "回声", "key_hint": "echo"},
            {"name": "纸鸮", "key_hint": "paper-owl"},
            {"name": "燧石", "key_hint": "flint"},
            {"name": "暗潮", "key_hint": "undertow"},
            {"name": "月蛾", "key_hint": "luna-moth"},
            {"name": "影织者", "key_hint": "shadow-weaver"},
        ]
        existing_names = {a.name for a in self.agents.values() if a.role.value == "companion"}
        added = 0
        for comp in default_companions:
            if comp["name"] not in existing_names:
                agent = AgentNode(
                    role=AgentRole.COMPANION,
                    name=comp["name"],
                    model="evomap-deepseek-v4-flash",
                )
                agent.node_id = f"local_cp_{uuid.uuid4().hex[:8]}"
                agent.node_secret = f"local_secret_{uuid.uuid4().hex[:12]}"
                self.add_agent(agent)
                self._save_agent_to_db(agent, f"companion_{comp['name']}")
                added += 1
        if added:
            logger.info(f"补充创建了 {added} 个缺少的 companion Agent")

    def _init_default_agents(self) -> None:
        """创建默认 Agent（纯本地模式，不依赖 EvoMap）。

        创建 1 个 DM + 4 个陪玩 Agent，使用预设人设模板。
        这样前端无需先调 /agents/register 即可直接开始游戏。
        """
        logger.info("未找到已注册 Agent，自动创建默认本地 Agent...")

        # DM
        dm = AgentNode(
            role=AgentRole.DM,
            name="雾港主理人",
            model="evomap-deepseek-v4-flash",
        )
        dm.node_id = f"local_dm_{uuid.uuid4().hex[:8]}"
        dm.node_secret = f"local_secret_{uuid.uuid4().hex[:12]}"
        dm_key = self.add_agent(dm)

        # Companion 列表
        default_companions = [
            {"name": "白鸦", "key_hint": "white-crow"},
            {"name": "回声", "key_hint": "echo"},
            {"name": "纸鸮", "key_hint": "paper-owl"},
            {"name": "燧石", "key_hint": "flint"},
            {"name": "暗潮", "key_hint": "undertow"},
            {"name": "月蛾", "key_hint": "luna-moth"},
            {"name": "影织者", "key_hint": "shadow-weaver"},
        ]
        for comp in default_companions:
            agent = AgentNode(
                role=AgentRole.COMPANION,
                name=comp["name"],
                model="evomap-deepseek-v4-flash",
            )
            agent.node_id = f"local_cp_{uuid.uuid4().hex[:8]}"
            agent.node_secret = f"local_secret_{uuid.uuid4().hex[:12]}"
            self.add_agent(agent)

        logger.info(f"已创建 {len(self.agents)} 个默认本地 Agent（{dm_key} + {len(default_companions)} companions）")

    def _save_agent_to_db(self, agent: AgentNode, key: str) -> None:
        """将 Agent 信息持久化到数据库。"""
        try:
            from api.db.models import get_session, AgentNode as AgentNodeModel
            db_session = get_session()
            try:
                db_agent = db_session.query(AgentNodeModel).filter(
                    AgentNodeModel.node_id == agent.node_id
                ).first()

                if not db_agent:
                    db_agent = AgentNodeModel(
                        id=f"an_{uuid.uuid4().hex[:8]}",
                        node_id=agent.node_id,
                        node_secret=agent.node_secret,
                    )
                    db_session.add(db_agent)

                db_agent.name = agent.name
                db_agent.role = agent.role.value
                db_agent.model = agent.model
                db_agent.identity_doc = agent.identity_doc
                db_agent.constitution = agent.constitution
                db_agent.status = "alive" if agent.registered else "local"
                db_agent.domains = agent.domains

                db_session.commit()
            except Exception as e:
                db_session.rollback()
                logger.error(f"保存 Agent 到数据库失败: {e}")
            finally:
                db_session.close()
        except Exception as e:
            logger.error(f"保存 Agent 到数据库失败（导入错误）: {e}")

    def add_agent(self, agent: AgentNode) -> str:
        """添加一个 Agent 到编排器（尚未注册）。"""
        key = f"{agent.role.value}_{agent.name}"
        self.agents[key] = agent
        return key

    def load_persona_to_agent(self, agent_key: str, persona_key: str) -> dict:
        """从人设库加载人设到指定 Agent，融合 constitution 和 identity_doc。

        Args:
            agent_key: Agent 在编排器中的 key，如 "companion_白鸦"
            persona_key: 人设库中的 key，如 "white-crow"

        Returns:
            加载结果，包含人设信息和融合后的 constitution/identity_doc
        """
        from api.agents.agent_persona_service import (
            get_persona_by_key,
            build_constitution_from_persona,
            build_identity_doc_from_persona,
        )

        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": "agent_not_found", "agent_key": agent_key}

        persona = get_persona_by_key(persona_key)
        if not persona:
            return {"error": "persona_not_found", "persona_key": persona_key}

        # 保存原始 constitution 作为基础
        base_constitution = agent.constitution

        # 融合人设到 constitution
        agent.constitution = build_constitution_from_persona(persona, base_constitution)

        # 融合人设到 identity_doc
        agent.identity_doc = build_identity_doc_from_persona(persona)

        # 记录人设 key
        agent.persona_key = persona_key

        # 持久化到数据库
        self._save_agent_to_db(agent, agent_key)

        logger.info(f"Agent [{agent_key}] 加载人设 [{persona_key}] 成功")
        return {
            "success": True,
            "agent_key": agent_key,
            "persona_key": persona_key,
            "persona_name": persona["name"],
            "constitution_length": len(agent.constitution),
            "identity_doc_length": len(agent.identity_doc),
        }

    def auto_match_personas(self, script_genre: str = "", difficulty: str = "") -> dict:
        """为所有 Agent 自动匹配最合适的人设。

        根据剧本类型和难度，为每个角色类型的 Agent 匹配最佳人设。
        """
        from api.agents.agent_persona_service import match_personas_for_script

        results = {}

        # 为 DM 匹配人设
        dm_agents = [(k, a) for k, a in self.agents.items() if a.role == AgentRole.DM]
        if dm_agents:
            dm_matches = match_personas_for_script(script_genre, difficulty, "dm", limit=1)
            if dm_matches:
                persona = dm_matches[0]
                result = self.load_persona_to_agent(dm_agents[0][0], persona["key"])
                results["dm"] = result

        # 为 Companion 匹配人设
        companion_agents = [(k, a) for k, a in self.agents.items() if a.role == AgentRole.COMPANION]
        if companion_agents:
            companion_matches = match_personas_for_script(
                script_genre, difficulty, "companion", limit=len(companion_agents)
            )
            for i, (agent_key, _) in enumerate(companion_agents):
                if i < len(companion_matches):
                    persona = companion_matches[i]
                    result = self.load_persona_to_agent(agent_key, persona["key"])
                    results[f"companion_{i}"] = result

        # 为 Assistant 匹配人设
        assistant_agents = [(k, a) for k, a in self.agents.items() if a.role == AgentRole.ASSISTANT]
        if assistant_agents:
            asst_matches = match_personas_for_script(script_genre, difficulty, "assistant", limit=1)
            if asst_matches:
                persona = asst_matches[0]
                result = self.load_persona_to_agent(assistant_agents[0][0], persona["key"])
                results["assistant"] = result

        return results

    def register_all(self) -> dict[str, dict]:
        """批量注册所有 Agent。返回每个 Agent 的注册结果。"""
        results = {}
        for key, agent in self.agents.items():
            results[key] = agent.register(self.hub_url)
        return results

    def create_game_session(self, topic: str, script_name: str) -> dict:
        """创建游戏 Session（纯本地模式，不依赖 EvoMap）。

        自动为每个 Agent 从数据库加载历史胶囊，
        作为本局行为的经验参考。
        """
        dm_agents = [a for a in self.agents.values() if a.role == AgentRole.DM]
        companion_agents = [a for a in self.agents.values() if a.role == AgentRole.COMPANION]
        assistant_agents = [a for a in self.agents.values() if a.role == AgentRole.ASSISTANT]

        if not dm_agents:
            return {"error": "no_dm_agent"}

        dm = dm_agents[0]

        # ========== 开局加载胶囊 ==========
        capsule_map: dict[str, list[dict]] = {}
        capsule_contexts: dict[str, str] = {}
        for key, agent in self.agents.items():
            if agent.registered and agent.node_id:
                capsules = agent.load_local_capsules(limit=5, min_score=0.3)
                if capsules:
                    capsule_map[key] = capsules
                    capsule_contexts[key] = agent.get_capsule_context_prompt(capsules)
                    logger.info(
                        f"Agent {key} 开局加载了 {len(capsules)} 条历史胶囊"
                    )

        # ========== 创建本地 Session（跳过 EvoMap）==========
        session_id = f"local_session_{uuid.uuid4().hex[:8]}"
        self.sessions[session_id] = {
            "topic": topic,
            "script_name": script_name,
            "dm": dm.node_id,
            "companions": [a.node_id for a in companion_agents],
            "assistant": [a.node_id for a in assistant_agents],
            "mode": "local",
            "capsule_count": {
                k: len(v) for k, v in capsule_map.items()
            },
        }
        for agent in companion_agents:
            agent.session_id = session_id

        return {
            "session_id": session_id,
            "mode": "local",
            "capsules_loaded": {k: len(v) for k, v in capsule_map.items()},
        }

    def broadcast_message(self, session_id: str, msg_type: str,
                          payload: dict, from_role: AgentRole) -> dict:
        """从指定角色的 Agent 广播消息到 Session（本地模式，不依赖 EvoMap）。"""
        agent = self._find_agent_by_role(from_role)
        if not agent:
            return {"error": "agent_not_found"}
        # 本地模式：直接写入 session 记录
        if session_id in self.sessions:
            if "messages" not in self.sessions[session_id]:
                self.sessions[session_id]["messages"] = []
            self.sessions[session_id]["messages"].append({
                "msg_type": msg_type,
                "payload": payload,
                "from_role": from_role.value,
                "agent_name": agent.name,
            })
            return {"success": True, "mode": "local"}
        return {"error": "session_not_found"}

    def send_direct_message(self, session_id: str, msg_type: str,
                            payload: dict, from_key: str, to_key: str) -> dict:
        """定向消息：从 Agent A 发送到 Agent B（本地模式）。"""
        from_agent = self.agents.get(from_key)
        to_agent = self.agents.get(to_key)
        if not from_agent or not to_agent:
            return {"error": "agent_not_found"}
        # 本地模式
        if session_id in self.sessions:
            if "direct_messages" not in self.sessions[session_id]:
                self.sessions[session_id]["direct_messages"] = []
            self.sessions[session_id]["direct_messages"].append({
                "msg_type": msg_type,
                "payload": payload,
                "from": from_key,
                "to": to_key,
            })
            return {"success": True, "mode": "local"}
        return {"error": "session_not_found"}

    def dm_generate_hint(self, level: int = 1, context: dict = None) -> dict:
        """让 DM Agent 生成分级提示。

        Args:
            level: 1-4
            context: 游戏上下文
        Returns:
            {"success": bool, "hint": dict, ...}
        """
        dm = self._find_agent_by_role(AgentRole.DM)
        if not dm:
            return {"success": False, "error": "no_dm_agent"}
        hint = dm.generate_hint(level, context)
        return {"success": True, "hint": hint}

    # ============================
    # 后剧情模式
    # ============================

    def post_game_reveal(self, session_id: str, vote_result: dict) -> dict:
        """投票后的后剧情处理——凶手交代真相。

        流程：
        1. 确定凶手和投票结果
        2. 重写凶手的 context，强制凶手交代作案过程和动机
        3. DM 揭晓完整真相
        4. 返回真相文本供前端展示

        Args:
            session_id: 游戏 Session ID
            vote_result: 投票结果 {"killer": str, "motive": str,
                                    "voter": str, "correct": bool, ...}
        Returns:
            {"success": bool, "killer_confession": str, "truth": str,
             "vote_correct": bool, "session_id": str}
        """
        # 找到凶手 Agent 和 DM
        accused_killer = vote_result.get("killer", "")
        is_correct = vote_result.get("correct", False)
        script_name = self.sessions.get(session_id, {}).get("script_name", "未知剧本")

        killer_agent = None
        dm_agent = self._find_agent_by_role(AgentRole.DM)

        try:
            from api.agents.game_engine import game_engine
            game = game_engine.get_game(session_id)
            if game:
                for key, state in game.get("agents", {}).items():
                    char_name = (state.character or {}).get("name", "")
                    if char_name == accused_killer:
                        killer_agent = self.agents.get(key)
                        break
        except Exception:
            pass

        if not killer_agent:
            for key, agent in self.agents.items():
                if agent.role == AgentRole.COMPANION and agent.registered:
                    if agent.name == accused_killer or agent.persona_key == accused_killer:
                        killer_agent = agent
                        break

        # 生成凶手交代（LLM）
        killer_confession = ""
        if killer_agent:
            try:
                from api.llm.llm_service import respond_initial
                prompt = (
                    f"你是{accused_killer}。你被指认是凶手。\n"
                    "你的角色秘密被揭穿了。现在你必须坦白一切。\n"
                    f"投票结果：{'✓ 正确' if is_correct else '✗ 错误判断'}\n\n"
                    "请以角色身份，用第一人称写一段交代（150-300字）：\n"
                    "1. 承认罪行（或否认，如果选错了人）\n"
                    "2. 交代作案动机和手法\n"
                    f"3. 说出整件事件的真相\n"
                    "语气要贴合你的角色性格——懊悔、挑衅、悲伤或其他。"
                )
                confession = respond_initial(
                    system_prompt=(
                        "你是剧本杀中的角色，你的秘密被揭穿了。"
                        "你必须以角色身份交代真相。"
                    ),
                    user_message=prompt,
                    temperature=0.8,
                    max_tokens=500,
                )
                killer_confession = confession.strip()
            except Exception as e:
                logger.error(f"生成凶手交代失败: {e}")
                killer_confession = f"[{accused_killer}的交代：系统生成失败]"

        # 生成 DM 真相揭晓
        truth = ""
        if dm_agent:
            try:
                from api.llm.llm_service import respond_initial
                truth_prompt = (
                    f"你是剧本杀DM「{dm_agent.name}」。\n"
                    f"剧本《{script_name}》的推理环节已结束。\n"
                    f"被指认的凶手：{accused_killer}\n"
                    f"投票是否正确：{'是' if is_correct else '否'}\n\n"
                    "请作为DM宣布案件真相，总结整个故事。\n"
                    "100-200字，包括案件复盘和真相解释。"
                )
                truth_text = respond_initial(
                    system_prompt="你是剧本杀DM，擅长复盘总结。语气庄重、公正。",
                    user_message=truth_prompt,
                    temperature=0.7,
                    max_tokens=400,
                )
                truth = truth_text.strip()
            except Exception as e:
                logger.error(f"生成DM真相揭晓失败: {e}")
                truth = f"[系统] 真相：凶手是{accused_killer}，本案真相待DM补充。"

        return {
            "success": True,
            "killer_confession": killer_confession,
            "truth": truth,
            "vote_correct": is_correct,
            "accused_killer": accused_killer,
            "session_id": session_id,
        }

    def generate_spoiler_story(self, session_id: str, vote_result: dict) -> dict:
        """生成剧透故事——完整游戏剧情回顾。

        投票后生成完整的游戏回顾，包含角色关系、真相、结局。
        """
        script_name = self.sessions.get(session_id, {}).get("script_name", "未知剧本")
        accused = vote_result.get("killer", "未知")
        correct = vote_result.get("correct", False)

        # 收集本局参与的 Agent 信息
        agents_info = []
        for key, agent in self.agents.items():
            if agent.role == AgentRole.COMPANION and agent.registered:
                agents_info.append(f"{agent.name}({agent.persona_key or '未知角色'})")

        try:
            from api.llm.llm_service import respond_initial
            prompt = (
                f"请为剧本杀《{script_name}》生成一份完整的剧透故事。\n"
                f"参与者：{', '.join(agents_info)}\n"
                f"被指认的凶手：{accused}\n"
                f"指认是否正确：{'正确' if correct else '错误'}\n\n"
                "包含以下内容（200-400字）：\n"
                "1. 故事背景和角色关系\n"
                "2. 案件真相和作案手法\n"
                "3. 各角色的结局\n"
                "4. 游戏总结\n"
                "语气：小说式的叙事风格。"
            )
            story = respond_initial(
                system_prompt="你是剧本杀故事作者，擅长写引人入胜的剧透故事。",
                user_message=prompt,
                temperature=0.8,
                max_tokens=800,
            )
            return {
                "success": True,
                "story": story.strip(),
                "script_name": script_name,
                "session_id": session_id,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_game_reflection(self, session_id: str, game_result: dict) -> list:
        """游戏结束后，所有 Agent 执行自评并记录经验。
        使用 LLM 生成自评摘要，并自动触发 constitution 进化。"""
        results = []
        for key, agent in self.agents.items():
            if not agent.registered or agent.role == AgentRole.ASSISTANT:
                continue

            if agent.role == AgentRole.COMPANION:
                signals = [
                    "role-playing", "inference", "user-interaction",
                    game_result.get("script_type", "unknown"),
                ]
                scores = {
                    "角色扮演": game_result.get("role_score", 0),
                    "推理": game_result.get("inference_score", 0),
                    "互动": game_result.get("interaction_score", 0),
                }
                summary = self._llm_reflection_summary(agent, scores, game_result)
                result = agent.record_experience(
                    signals=signals,
                    gene_id=f"game_{session_id}",
                    status="completed",
                    score=game_result.get("overall_score", 0.7),
                    summary=summary,
                )
                results.append({"agent": key, "reflection": result})

            elif agent.role == AgentRole.DM:
                signals = [
                    "hosting", "pacing", "hint-management",
                    game_result.get("script_type", "unknown"),
                ]
                scores = {
                    "控场": game_result.get("hosting_score", 0),
                    "节奏": game_result.get("pacing_score", 0),
                }
                summary = self._llm_reflection_summary(agent, scores, game_result)
                result = agent.record_experience(
                    signals=signals,
                    gene_id=f"dm_{session_id}",
                    status="completed",
                    score=game_result.get("dm_score", 0.7),
                    summary=summary,
                )
                results.append({"agent": key, "reflection": result})

            # ========== 自动进化：LLM 改写 constitution ==========
            old_constitution = agent.constitution
            new_constitution = self._llm_evolve_constitution(agent, game_result)
            if new_constitution and new_constitution != old_constitution:
                agent.constitution = new_constitution
                self._save_agent_to_db(agent, key)
                self._save_evolution_record(key, agent, session_id, old_constitution, new_constitution)
                results[-1]["constitution_evolved"] = True
                results[-1]["old_constitution"] = old_constitution[:100]
                results[-1]["new_constitution"] = new_constitution[:100]
                logger.info(f"Agent [{key}] constitution 自动进化完成")

        return results

    def _llm_reflection_summary(self, agent: "AgentNode",
                                 scores: dict, game_result: dict) -> str:
        """用 LLM 生成局后自评摘要。"""
        scores_str = ", ".join(f"{k}={v:.1f}" for k, v in scores.items())
        role_label = "DM主持人" if agent.role == AgentRole.DM else "角色扮演(陪玩Agent)"
        prompt = (
            f"你是{role_label}「{agent.name}」。\n"
            f"你刚刚完成了一局剧本杀游戏。\n"
            f"评分：{scores_str}\n"
            f"剧本类型：{game_result.get('script_type', '未知')}\n"
            "请以第一人称写一段简短的自评反思（50-100字），包括：\n"
            "1. 做得好的地方 2. 可改进的地方 3. 学到了什么"
        )
        try:
            from api.llm.llm_service import respond_initial
            reflection = respond_initial(
                system_prompt="你是一个能自我反思的AI Agent，请写一段诚恳有建设性的自评。",
                user_message=prompt,
                temperature=0.7, max_tokens=300,
            )
            return reflection.strip()
        except Exception as e:
            logger.warning(f"LLM reflection failed for {agent.name}: {e}")
            return f"自评：{scores_str}"

    def _llm_evolve_constitution(self, agent: "AgentNode", game_result: dict) -> str:
        """用 LLM 基于游戏表现生成改进后的 constitution。"""
        score_text = (
            f"整体评分={game_result.get('overall_score', 0):.1f}, "
            f"角色扮演={game_result.get('role_score', 0):.1f}, "
            f"推理={game_result.get('inference_score', 0):.1f}"
        ) if game_result else "暂无评分"

        prompt = (
            f"你是AI Agent「{agent.name}」，角色类型：{agent.role.value}。\n\n"
            f"你当前的 behavior constitution：\n{agent.constitution}\n\n"
            f"本局表现：{score_text}\n\n"
            "请根据本局表现，分析优缺点，生成一份**改进后的行为宪章**。\n"
            "新宪章应保留有效原则，加入从经验中学到的新策略。\n"
            "请按格式回复：\n"
            "【新宪章】\n...(宪章内容，100-200字)"
        )
        try:
            from api.llm.llm_service import respond_initial
            result = respond_initial(
                system_prompt="你是一个能自我进化、反思并改进行为规则的AI Agent。",
                user_message=prompt,
                temperature=0.7, max_tokens=500,
            )
            # 解析 【新宪章】 后的内容
            if "【新宪章】" in result:
                new_c = result.split("【新宪章】", 1)[1].strip()
                return new_c
            return result.strip()[:300]
        except Exception as e:
            logger.warning(f"Constitution evolution failed for {agent.name}: {e}")
            return ""

    def _save_evolution_record(self, agent_key: str, agent: "AgentNode",
                                session_id: str, old_content: str, new_content: str) -> None:
        """将 constitution 进化记录保存到数据库。"""
        try:
            from api.db.models import get_session, AgentNode as AgentNodeModel, EvolutionRecord
            db_session = get_session()
            try:
                db_agent = db_session.query(AgentNodeModel).filter(
                    AgentNodeModel.node_id == agent.node_id
                ).first()
                if db_agent:
                    record = EvolutionRecord(
                        id=f"er_{uuid.uuid4().hex[:8]}",
                        agent_node_id=db_agent.id,
                        session_id=session_id,
                        signals=agent.domains,
                        status="evolved",
                        score=0.0,
                        summary="局后自动进化：constitution 改写",
                        update_type="constitution",
                        old_content=old_content,
                        new_content=new_content,
                    )
                    db_session.add(record)
                    db_session.commit()
            finally:
                db_session.close()
        except Exception as e:
            logger.error(f"保存进化记录失败: {e}")

    def load_all_agent_capsules(self, min_score: float = 0.3,
                                limit: int = 5) -> dict[str, dict]:
        """加载所有已注册 Agent 的历史胶囊。

        可在游戏开局时调用，获取每个 Agent 的历史经验摘要。

        Returns:
            {"agent_key": {"capsules": [...], "context_prompt": str, "count": int}, ...}
        """
        result = {}
        for key, agent in self.agents.items():
            if not agent.node_id:
                continue
            capsules = agent.load_local_capsules(limit=limit, min_score=min_score)
            context_prompt = agent.get_capsule_context_prompt(capsules) if capsules else ""
            result[key] = {
                "capsules": capsules,
                "context_prompt": context_prompt,
                "count": len(capsules),
            }
        return result

    def _find_agent_by_role(self, role: AgentRole) -> Optional[AgentNode]:
        """找到指定角色的第一个 Agent。"""
        for agent in self.agents.values():
            if agent.role == role and agent.registered:
                return agent
        return None
