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


class AgentOrchestrator:
    """多Agent编排器：管理一组 Agent 的注册、Session 创建和任务调度。"""

    def __init__(self, hub_url: str = "https://evomap.ai"):
        self.hub_url = hub_url
        self.agents: dict[str, AgentNode] = {}
        self.sessions: dict[str, dict] = {}
        # 启动时从数据库恢复已注册的 Agent
        self._load_agents_from_db()

    def _load_agents_from_db(self) -> None:
        """从数据库恢复已注册的 Agent 到内存。"""
        try:
            from api.db.models import get_session, AgentNode as AgentNodeModel
            db_session = get_session()
            try:
                db_agents = db_session.query(AgentNodeModel).all()
                for db_agent in db_agents:
                    agent = AgentNode(
                        role=AgentRole(db_agent.role),
                        name=db_agent.name,
                        model=db_agent.model,
                        node_id=db_agent.node_id,
                        node_secret=db_agent.node_secret,
                        identity_doc=db_agent.identity_doc,
                        constitution=db_agent.constitution,
                    )
                    agent.registered = (db_agent.status == "alive")
                    key = f"{agent.role.value}_{agent.name}"
                    self.agents[key] = agent
                if db_agents:
                    logger.info(f"从数据库恢复了 {len(db_agents)} 个 Agent")
            finally:
                db_session.close()
        except Exception as e:
            logger.error(f"从数据库恢复 Agent 失败: {e}")

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

    def register_all(self) -> dict[str, dict]:
        """批量注册所有 Agent。返回每个 Agent 的注册结果。"""
        results = {}
        for key, agent in self.agents.items():
            results[key] = agent.register(self.hub_url)
        return results

    def create_game_session(self, topic: str, script_name: str) -> dict:
        """创建游戏 Session，邀请所有 Agent 参与。

        如果 DM 未注册到 EvoMap（本地模式），则创建本地 Session。
        """
        dm_agents = [a for a in self.agents.values() if a.role == AgentRole.DM]
        companion_agents = [a for a in self.agents.values() if a.role == AgentRole.COMPANION]
        assistant_agents = [a for a in self.agents.values() if a.role == AgentRole.ASSISTANT]

        if not dm_agents:
            return {"error": "no_dm_agent"}

        dm = dm_agents[0]

        # 本地模式：DM 未注册到 EvoMap，创建本地 Session
        if not dm.client:
            session_id = f"local_session_{uuid.uuid4().hex[:8]}"
            self.sessions[session_id] = {
                "topic": topic,
                "script_name": script_name,
                "dm": dm.node_id,
                "companions": [a.node_id for a in companion_agents],
                "assistant": [a.node_id for a in assistant_agents],
                "mode": "local",
            }
            for agent in companion_agents:
                agent.session_id = session_id
            return {
                "session_id": session_id,
                "mode": "local",
                "warning": "EvoMap Session 不可用，已创建本地 Session",
            }

        # EvoMap 模式：DM 创建 Session，邀请所有陪玩 Agent
        participants = [a.node_id for a in companion_agents if a.registered]
        result = dm.client.create_session(
            topic=f"[剧本杀] {script_name} - {topic}",
            participants=participants,
        )

        if "session_id" in result:
            session_id = result["session_id"]
            self.sessions[session_id] = {
                "topic": topic,
                "script_name": script_name,
                "dm": dm.node_id,
                "companions": participants,
                "assistant": [a.node_id for a in assistant_agents if a.registered],
                "mode": "evomap",
            }
            for agent in companion_agents:
                if agent.registered:
                    agent.session_id = session_id
        return result

    def broadcast_message(self, session_id: str, msg_type: str,
                          payload: dict, from_role: AgentRole) -> dict:
        """从指定角色的 Agent 广播消息到 Session。"""
        agent = self._find_agent_by_role(from_role)
        if not agent or not agent.client:
            return {"error": "agent_not_found_or_not_registered"}
        return agent.client.send_message(
            session_id=session_id, msg_type=msg_type, payload=payload,
        )

    def send_direct_message(self, session_id: str, msg_type: str,
                            payload: dict, from_key: str, to_key: str) -> dict:
        """定向消息：从 Agent A 发送到 Agent B。"""
        from_agent = self.agents.get(from_key)
        to_agent = self.agents.get(to_key)
        if not from_agent or not to_agent or not from_agent.client:
            return {"error": "agent_not_found"}
        return from_agent.client.send_message(
            session_id=session_id, msg_type=msg_type, payload=payload,
            to_node_id=to_agent.node_id,
        )

    def post_game_reflection(self, session_id: str, game_result: dict) -> list:
        """游戏结束后，所有 Agent 执行自评并记录经验。"""
        results = []
        for key, agent in self.agents.items():
            if not agent.registered or agent.role == AgentRole.ASSISTANT:
                continue

            # Companion Agent 自评
            if agent.role == AgentRole.COMPANION:
                signals = [
                    "role-playing", "inference", "user-interaction",
                    game_result.get("script_type", "unknown"),
                ]
                summary = (
                    f"角色扮演评分:{game_result.get('role_score', 0):.1f} "
                    f"推理评分:{game_result.get('inference_score', 0):.1f} "
                    f"互动评分:{game_result.get('interaction_score', 0):.1f}"
                )
                result = agent.record_experience(
                    signals=signals,
                    gene_id=f"game_{session_id}",
                    status="completed",
                    score=game_result.get("overall_score", 0.7),
                    summary=summary,
                )
                results.append({"agent": key, "reflection": result})

            # DM Agent 自评
            elif agent.role == AgentRole.DM:
                signals = [
                    "hosting", "pacing", "hint-management",
                    game_result.get("script_type", "unknown"),
                ]
                summary = (
                    f"控场评分:{game_result.get('hosting_score', 0):.1f} "
                    f"节奏评分:{game_result.get('pacing_score', 0):.1f}"
                )
                result = agent.record_experience(
                    signals=signals,
                    gene_id=f"dm_{session_id}",
                    status="completed",
                    score=game_result.get("dm_score", 0.7),
                    summary=summary,
                )
                results.append({"agent": key, "reflection": result})

        return results

    def _find_agent_by_role(self, role: AgentRole) -> Optional[AgentNode]:
        """找到指定角色的第一个 Agent。"""
        for agent in self.agents.values():
            if agent.role == role and agent.registered:
                return agent
        return None
