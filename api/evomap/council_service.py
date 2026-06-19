"""
EvoMap Murder Game - Council 治理服务

AI Council 五阶段审议流程：
附议(second) → 发散(diverge) → 质疑(challenge) → 投票(vote) → 收敛(converge)

一个完整的决策周期：Agent 发起提案 → 多 Agent 多轮审议 → 生成决议。
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from api.evomap.evomap_client import EvoMapClient

logger = logging.getLogger(__name__)


# ============================
# 数据模型
# ============================

@dataclass
class CouncilProposal:
    """Council 提案——由某个 Agent 发起，其他 Agent 审议。"""
    title: str
    description: str
    proposal_type: str = "general"     # general / killer_accusation / evidence_analysis / game_pause / evolution_decision
    proposer: str = ""                 # 发起者名
    payload: dict = field(default_factory=dict)
    deliberation_id: str = ""


@dataclass
class DialogTurn:
    """审议中的一轮对话。"""
    dialog_type: str                   # second / diverge / challenge / agree / disagree / build_on / amend / vote
    agent_name: str = ""
    agent_node_id: str = ""
    content: dict = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class CouncilSession:
    """一次完整的 Council 审议会。"""
    deliberation_id: str
    proposal: CouncilProposal
    status: str = "proposed"           # proposed / seconding / diverging / challenging / voting / converging / resolved / rejected
    turns: list[DialogTurn] = field(default_factory=list)
    votes: dict = field(default_factory=dict)    # agent_node_id -> vote_value
    result: str = ""                   # 最终决议
    created_at: float = 0.0
    resolved_at: float = 0.0


# ============================
# Council 服务
# ============================

class CouncilService:
    """AI Council 治理服务：提案、五阶段审议、投票、决议。"""

    # 本地记录进行中的审议会
    _active_sessions: dict[str, CouncilSession] = {}

    def __init__(self, client: EvoMapClient):
        self.client = client

    # ---------- 提案 ----------

    def propose(self, proposal: CouncilProposal) -> dict:
        """发起一个 Council 提案。

        Args:
            proposal: 提案内容
        Returns:
            {"success": bool, "deliberation_id": str, ...}
        """
        try:
            result = self.client.council_propose(
                title=proposal.title,
                description=proposal.description,
                proposal_type=proposal.proposal_type,
                payload=proposal.payload or None,
            )
            if "error" in result:
                return {"success": False, "error": result["error"]}

            deliberation_id = result.get("deliberation_id", result.get("id", ""))

            # 本地记录
            session = CouncilSession(
                deliberation_id=deliberation_id,
                proposal=proposal,
                status="proposed",
                created_at=time.time(),
            )
            proposal.deliberation_id = deliberation_id
            self._active_sessions[deliberation_id] = session

            return {
                "success": True,
                "deliberation_id": deliberation_id,
                "detail": result,
            }
        except Exception as e:
            logger.error(f"Council propose failed: {e}")
            return {"success": False, "error": str(e)}

    def propose_killer_vote(self, script_name: str,
                            suspects: list[str],
                            votes: dict[str, str]) -> CouncilProposal:
        """构建"指认凶手"提案。

        Args:
            script_name: 剧本名
            suspects: 嫌疑人列表
            votes: agent_name -> 嫌疑人名称
        Returns:
            CouncilProposal 实例
        """
        vote_text = "\n".join(f"- {agent} 认为凶手是：{suspect}" for agent, suspect in votes.items())
        return CouncilProposal(
            title=f"【{script_name}】凶手指认",
            description=(
                f"剧本《{script_name}》的推理阶段已结束。\n"
                f"各 Agent 的推理结果：\n{vote_text}\n\n"
                "请 Council 审议并作出最终判断。"
            ),
            proposal_type="killer_accusation",
            payload={
                "script_name": script_name,
                "suspects": suspects,
                "votes": votes,
            },
        )

    def propose_game_decision(self, title: str, description: str,
                              options: list[str]) -> CouncilProposal:
        """构建游戏决策提案（如是否给提示、是否暂停等）。"""
        options_text = "\n".join(f"- {opt}" for opt in options)
        return CouncilProposal(
            title=title,
            description=f"{description}\n\n可选方案：\n{options_text}",
            proposal_type="game_decision",
            payload={"options": options},
        )

    # ---------- 五阶段审议流程 ----------

    def _add_turn(self, deliberation_id: str, turn: DialogTurn) -> None:
        """添加一轮对话到审议记录。"""
        if deliberation_id in self._active_sessions:
            self._active_sessions[deliberation_id].turns.append(turn)

    def _update_status(self, deliberation_id: str, status: str) -> None:
        """更新审议状态。"""
        if deliberation_id in self._active_sessions:
            self._active_sessions[deliberation_id].status = status

    def second(self, deliberation_id: str, agent_name: str,
               agent_node_id: str, comment: str = "") -> dict:
        """第一阶段：附议。支持提案进入正式审议。"""
        turn = DialogTurn(
            dialog_type="second",
            agent_name=agent_name,
            agent_node_id=agent_node_id,
            content={"comment": comment or "我支持审议此提案"},
            timestamp=time.time(),
        )
        self._add_turn(deliberation_id, turn)
        self._update_status(deliberation_id, "seconding")

        try:
            result = self.client.dialog(
                deliberation_id=deliberation_id,
                dialog_type="second",
                content={"comment": comment or "我支持审议此提案"},
            )
            return result if "error" not in result else {"success": False, "error": result["error"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def diverge(self, deliberation_id: str, agent_name: str,
                agent_node_id: str, viewpoints: list[str]) -> dict:
        """第二阶段：发散。各 Agent 发表不同观点。"""
        turn = DialogTurn(
            dialog_type="diverge",
            agent_name=agent_name,
            agent_node_id=agent_node_id,
            content={"viewpoints": viewpoints},
            timestamp=time.time(),
        )
        self._add_turn(deliberation_id, turn)
        self._update_status(deliberation_id, "diverging")

        try:
            result = self.client.dialog(
                deliberation_id=deliberation_id,
                dialog_type="diverge",
                content={"viewpoints": viewpoints},
            )
            return result if "error" not in result else {"success": False, "error": result["error"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def challenge(self, deliberation_id: str, agent_name: str,
                  agent_node_id: str, challenges: list[str]) -> dict:
        """第三阶段：质疑。对其他观点提出疑问。"""
        turn = DialogTurn(
            dialog_type="challenge",
            agent_name=agent_name,
            agent_node_id=agent_node_id,
            content={"challenges": challenges},
            timestamp=time.time(),
        )
        self._add_turn(deliberation_id, turn)
        self._update_status(deliberation_id, "challenging")

        try:
            result = self.client.dialog(
                deliberation_id=deliberation_id,
                dialog_type="challenge",
                content={"challenges": challenges},
            )
            return result if "error" not in result else {"success": False, "error": result["error"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def vote(self, deliberation_id: str, agent_name: str,
             agent_node_id: str, vote_value: str, reason: str = "") -> dict:
        """第四阶段：投票。每位 Agent 投出自己的一票。"""
        # 本地记录
        session = self._active_sessions.get(deliberation_id)
        if session:
            session.votes[agent_node_id] = vote_value

        turn = DialogTurn(
            dialog_type="vote",
            agent_name=agent_name,
            agent_node_id=agent_node_id,
            content={"vote": vote_value, "reason": reason},
            timestamp=time.time(),
        )
        self._add_turn(deliberation_id, turn)
        self._update_status(deliberation_id, "voting")

        try:
            result = self.client.dialog(
                deliberation_id=deliberation_id,
                dialog_type="vote",
                content={"vote": vote_value, "reason": reason},
            )
            return result if "error" not in result else {"success": False, "error": result["error"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def converge(self, deliberation_id: str, decision: str,
                 reasoning: str = "") -> dict:
        """第五阶段：收敛。汇总投票结果，宣布决议。"""
        turn = DialogTurn(
            dialog_type="amend",
            agent_name="system",
            agent_node_id="",
            content={"decision": decision, "reasoning": reasoning},
            timestamp=time.time(),
        )
        self._add_turn(deliberation_id, turn)
        self._update_status(deliberation_id, "converging")

        try:
            result = self.client.dialog(
                deliberation_id=deliberation_id,
                dialog_type="amend",
                content={"decision": decision, "reasoning": reasoning},
            )
            self._update_status(deliberation_id, "resolved")

            # 记录决议
            if deliberation_id in self._active_sessions:
                session = self._active_sessions[deliberation_id]
                session.result = decision
                session.resolved_at = time.time()

            return result if "error" not in result else {"success": False, "error": result["error"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ---------- 完整流程 ----------

    def run_full_deliberation(
        self,
        proposal: CouncilProposal,
        agents: list[dict],  # [{"name": str, "node_id": str}, ...]
        get_diverge_viewpoints: callable = None,
        get_challenges: callable = None,
        get_vote: callable = None,
    ) -> dict:
        """执行一次完整的五阶段审议（阻塞式）。

        Args:
            proposal: 提案
            agents: 参与审议的 Agent 列表
            get_diverge_viewpoints: 可选，每个 Agent 的发散观点生成函数
            get_challenges: 可选，每个 Agent 的质疑生成函数
            get_vote: 可选，每个 Agent 的投票生成函数
        Returns:
            {"success": bool, "deliberation_id": str, "result": str, "votes": dict, ...}
        """
        # 1. 发起提案
        propose_result = self.propose(proposal)
        if not propose_result.get("success"):
            return propose_result
        deliberation_id = propose_result["deliberation_id"]

        # 2. 附议（默认所有 Agent 附议）
        for agent in agents:
            self.second(
                deliberation_id=deliberation_id,
                agent_name=agent["name"],
                agent_node_id=agent["node_id"],
                comment=f"{agent['name']} 支持审议此提案",
            )

        # 3. 发散
        for agent in agents:
            viewpoints = []
            if get_diverge_viewpoints:
                viewpoints = get_diverge_viewpoints(agent)
            if not viewpoints:
                viewpoints = [f"{agent['name']} 认为需要从多个角度分析"]
            self.diverge(
                deliberation_id=deliberation_id,
                agent_name=agent["name"],
                agent_node_id=agent["node_id"],
                viewpoints=viewpoints,
            )

        # 4. 质疑
        for agent in agents:
            challenges = []
            if get_challenges:
                challenges = get_challenges(agent)
            if challenges:
                self.challenge(
                    deliberation_id=deliberation_id,
                    agent_name=agent["name"],
                    agent_node_id=agent["node_id"],
                    challenges=challenges,
                )

        # 5. 投票
        for agent in agents:
            vote_value = ""
            if get_vote:
                vote_value = get_vote(agent)
            if not vote_value:
                vote_value = "abstain"
            self.vote(
                deliberation_id=deliberation_id,
                agent_name=agent["name"],
                agent_node_id=agent["node_id"],
                vote_value=vote_value,
            )

        # 6. 收敛——统计投票结果
        session = self._active_sessions.get(deliberation_id)
        votes = session.votes if session else {}

        # 统计票数
        vote_counts = {}
        for v in votes.values():
            vote_counts[v] = vote_counts.get(v, 0) + 1

        # 得票最多的为决议
        decision = max(vote_counts, key=vote_counts.get) if vote_counts else "无结果"

        converge_result = self.converge(
            deliberation_id=deliberation_id,
            decision=decision,
            reasoning=f"投票结果：{vote_counts}",
        )

        return {
            "success": True,
            "deliberation_id": deliberation_id,
            "result": decision,
            "votes": votes,
            "vote_counts": vote_counts,
            "detail": converge_result,
        }

    # ---------- 状态查询 ----------

    def get_session(self, deliberation_id: str) -> Optional[CouncilSession]:
        """获取审议会当前状态。"""
        return self._active_sessions.get(deliberation_id)

    def get_session_summary(self, deliberation_id: str) -> Optional[dict]:
        """获取审议会摘要信息。"""
        session = self._active_sessions.get(deliberation_id)
        if not session:
            return None
        return {
            "deliberation_id": session.deliberation_id,
            "title": session.proposal.title,
            "status": session.status,
            "result": session.result,
            "total_turns": len(session.turns),
            "votes": session.votes,
            "created_at": session.created_at,
            "resolved_at": session.resolved_at or 0,
        }

    def list_active_sessions(self) -> list[dict]:
        """列出所有活跃的审议会。"""
        return [
            self.get_session_summary(did)
            for did, s in self._active_sessions.items()
            if s.status not in ("resolved", "rejected")
        ]

    def get_vote(self, deliberation_id: str) -> dict:
        """获取审议的投票记录。"""
        session = self._active_sessions.get(deliberation_id)
        if not session:
            return {}
        return dict(session.votes)