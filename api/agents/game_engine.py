"""
EvoMap Murder Game - Game Engine

游戏阶段状态机：控制一局剧本杀的完整生命周期。
阶段流转：intro → investigation → voting → reveal → review

每个阶段有：
  - 进入条件（can_enter）
  - 允许的操作（allowed_actions）
  - 退出条件（can_advance）
  - 阶段提示（phase_prompt）
"""

import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from api.db.models import get_session, GameSession, ConversationTurn, GameProgressRecord

logger = logging.getLogger(__name__)


# ============================
# 游戏阶段枚举
# ============================

class GamePhase(str, Enum):
    INTRO = "intro"                  # 开场介绍
    INVESTIGATION = "investigation"  # 自由调查
    VOTING = "voting"                # 提交推理
    REVEAL = "reveal"                # 真相揭示
    REVIEW = "review"                # 复盘反思


# ============================
# 阶段配置
# ============================

PHASE_CONFIG = {
    GamePhase.INTRO: {
        "display_name": "开场介绍",
        "description": "DM介绍案件背景、受害者信息、玩家身份",
        "allowed_actions": ["read_intro", "acknowledge"],
        "phase_prompt": (
            "游戏刚刚开始。请以DM身份介绍案件背景：\n"
            "1. 受害者是谁，如何遇害\n"
            "2. 案发时间和地点\n"
            "3. 在场嫌疑人名单\n"
            "4. 玩家的身份和任务\n"
            "注意：不要透露任何凶手信息或关键线索。"
        ),
    },
    GamePhase.INVESTIGATION: {
        "display_name": "自由调查",
        "description": "玩家自由与角色对话、收集证物、推理线索",
        "allowed_actions": [
            "chat", "present_evidence", "share_note",
            "investigate_evidence", "combine_evidence",
            "request_hint", "review_notes",
        ],
        "phase_prompt": (
            "玩家正在调查阶段。你可以：\n"
            "- 与任何角色对话\n"
            "- 出示证物给角色\n"
            "- 调查和组合证物\n"
            "- 请求DM提示\n"
            "当你认为已经找到凶手时，可以提交推理。"
        ),
    },
    GamePhase.VOTING: {
        "display_name": "提交推理",
        "description": "玩家选择凶手和作案动机",
        "allowed_actions": ["submit_vote", "change_vote", "confirm_vote"],
        "phase_prompt": (
            "玩家正在提交推理。请选择：\n"
            "1. 你认为谁是凶手？\n"
            "2. 作案动机是什么？\n"
            "请仔细思考后再提交。"
        ),
    },
    GamePhase.REVEAL: {
        "display_name": "真相揭示",
        "description": "揭晓答案，凶手交代真相",
        "allowed_actions": ["read_reveal", "ask_killer"],
        "phase_prompt": (
            "真相揭晓阶段。凶手已被揭露，请以凶手身份完整交代：\n"
            "1. 作案动机\n"
            "2. 作案时间线\n"
            "3. 作案手法\n"
            "4. 如何掩盖罪行\n"
            "请以角色口吻讲述，不要遗漏关键细节。"
        ),
    },
    GamePhase.REVIEW: {
        "display_name": "复盘反思",
        "description": "游戏结束，Agent自评并记录经验",
        "allowed_actions": ["view_summary", "record_experience"],
        "phase_prompt": (
            "游戏复盘阶段。请回顾整局游戏：\n"
            "1. 关键转折点是什么？\n"
            "2. 哪些线索最关键？\n"
            "3. 玩家的推理过程如何？\n"
            "4. 有什么可以改进的地方？"
        ),
    },
}

# 阶段流转顺序
PHASE_ORDER = [GamePhase.INTRO, GamePhase.INVESTIGATION, GamePhase.VOTING, GamePhase.REVEAL, GamePhase.REVIEW]


# ============================
# 游戏引擎
# ============================

class GameEngine:
    """游戏阶段状态机——驱动一局剧本杀的完整生命周期。"""

    def __init__(self):
        # 内存中的活跃游戏状态
        self._games: dict[str, dict] = {}

    def create_game(self, script_id: str, session_id: str = "") -> dict:
        """创建新游戏实例。"""
        game_id = session_id or f"game_{uuid.uuid4().hex[:8]}"

        game_state = {
            "game_id": game_id,
            "script_id": script_id,
            "current_phase": GamePhase.INTRO,
            "phase_history": [{"phase": GamePhase.INTRO, "entered_at": datetime.now(timezone.utc).isoformat()}],
            "votes": [],           # 投票记录
            "vote_result": None,   # 投票结果
            "started_at": datetime.now(timezone.utc).isoformat(),
            "ended_at": None,
            "hints_used": 0,
            "chat_count": 0,       # 对话轮数
        }

        self._games[game_id] = game_state

        # 同步到数据库
        self._sync_to_db(game_state)

        return game_state

    def get_game(self, game_id: str) -> Optional[dict]:
        """获取游戏状态。"""
        if game_id in self._games:
            return self._games[game_id]

        # 尝试从数据库加载
        db_session = get_session()
        try:
            game_session = db_session.query(GameSession).filter(
                GameSession.session_id == game_id
            ).first()
            if game_session:
                game_state = {
                    "game_id": game_id,
                    "script_id": game_session.script_id or "",
                    "current_phase": game_session.current_phase or GamePhase.INTRO,
                    "phase_history": game_session.phase_history or [],
                    "votes": game_session.result.get("votes", []) if game_session.result else [],
                    "vote_result": game_session.result.get("vote_result") if game_session.result else None,
                    "started_at": game_session.started_at.isoformat() if game_session.started_at else "",
                    "ended_at": game_session.ended_at.isoformat() if game_session.ended_at else None,
                    "hints_used": 0,
                    "chat_count": 0,
                }
                self._games[game_id] = game_state
                return game_state
        finally:
            db_session.close()

        return None

    def get_current_phase(self, game_id: str) -> Optional[GamePhase]:
        """获取当前阶段。"""
        game = self.get_game(game_id)
        if game:
            return GamePhase(game["current_phase"])
        return None

    def get_phase_info(self, game_id: str) -> dict:
        """获取当前阶段的详细信息。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        phase = GamePhase(game["current_phase"])
        config = PHASE_CONFIG[phase]

        # 计算下一阶段
        current_idx = PHASE_ORDER.index(phase)
        next_phase = PHASE_ORDER[current_idx + 1] if current_idx < len(PHASE_ORDER) - 1 else None

        return {
            "game_id": game_id,
            "current_phase": phase.value,
            "display_name": config["display_name"],
            "description": config["description"],
            "allowed_actions": config["allowed_actions"],
            "phase_prompt": config["phase_prompt"],
            "next_phase": next_phase.value if next_phase else None,
            "can_advance": self.can_advance(game_id),
            "phase_history": game["phase_history"],
            "chat_count": game.get("chat_count", 0),
            "hints_used": game.get("hints_used", 0),
        }

    def can_advance(self, game_id: str) -> bool:
        """检查是否可以推进到下一阶段。"""
        game = self.get_game(game_id)
        if not game:
            return False

        phase = GamePhase(game["current_phase"])

        if phase == GamePhase.INTRO:
            # 开场介绍后始终可以推进
            return True
        elif phase == GamePhase.INVESTIGATION:
            # 至少对话3轮后才能提交推理
            return game.get("chat_count", 0) >= 3
        elif phase == GamePhase.VOTING:
            # 投票完成后才能揭示
            return game.get("vote_result") is not None
        elif phase == GamePhase.REVEAL:
            # 真相揭示后可以复盘
            return True
        elif phase == GamePhase.REVIEW:
            # 复盘是最后阶段
            return False

        return False

    def advance_phase(self, game_id: str) -> dict:
        """推进到下一阶段。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        if not self.can_advance(game_id):
            current = GamePhase(game["current_phase"])
            config = PHASE_CONFIG[current]
            return {"error": f"cannot_advance", "reason": f"当前阶段({config['display_name']})不满足推进条件"}

        current_phase = GamePhase(game["current_phase"])
        current_idx = PHASE_ORDER.index(current_phase)

        if current_idx >= len(PHASE_ORDER) - 1:
            return {"error": "already_final_phase"}

        next_phase = PHASE_ORDER[current_idx + 1]
        game["current_phase"] = next_phase.value
        game["phase_history"].append({
            "phase": next_phase.value,
            "entered_at": datetime.now(timezone.utc).isoformat(),
        })

        if next_phase == GamePhase.REVIEW:
            game["ended_at"] = datetime.now(timezone.utc).isoformat()

        # 同步到数据库
        self._sync_to_db(game)

        next_config = PHASE_CONFIG[next_phase]
        return {
            "success": True,
            "previous_phase": current_phase.value,
            "current_phase": next_phase.value,
            "display_name": next_config["display_name"],
            "phase_prompt": next_config["phase_prompt"],
            "allowed_actions": next_config["allowed_actions"],
        }

    def record_chat(self, game_id: str) -> None:
        """记录一次对话（用于推进条件判断）。"""
        game = self.get_game(game_id)
        if game:
            game["chat_count"] = game.get("chat_count", 0) + 1

    def record_hint(self, game_id: str) -> None:
        """记录一次提示使用。"""
        game = self.get_game(game_id)
        if game:
            game["hints_used"] = game.get("hints_used", 0) + 1

    def submit_vote(self, game_id: str, killer: str, motive: str = "", voter: str = "player") -> dict:
        """提交推理投票。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        if GamePhase(game["current_phase"]) != GamePhase.VOTING:
            return {"error": "not_in_voting_phase"}

        vote = {
            "voter": voter,
            "killer": killer,
            "motive": motive,
            "voted_at": datetime.now(timezone.utc).isoformat(),
        }
        game["votes"].append(vote)

        # 查询正确答案
        db_session = get_session()
        try:
            from api.db.models import Script
            script = db_session.query(Script).filter(Script.id == game["script_id"]).first()
            correct_killer = script.killer_role if script else ""
            is_correct = (killer == correct_killer) if correct_killer else True

            game["vote_result"] = {
                "killer": killer,
                "motive": motive,
                "is_correct": is_correct,
                "correct_killer": correct_killer,
            }

            # 同步到数据库
            self._sync_to_db(game)

            return {
                "success": True,
                "is_correct": is_correct,
                "correct_killer": correct_killer if not is_correct else "",
                "message": "推理正确！" if is_correct else f"推理有误，真凶是{correct_killer}",
            }
        finally:
            db_session.close()

    def force_phase(self, game_id: str, target_phase: str) -> dict:
        """强制跳转到指定阶段（DM权限，用于调试或异常恢复）。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        try:
            phase = GamePhase(target_phase)
        except ValueError:
            return {"error": "invalid_phase", "valid_phases": [p.value for p in GamePhase]}

        previous = game["current_phase"]
        game["current_phase"] = phase.value
        game["phase_history"].append({
            "phase": phase.value,
            "entered_at": datetime.now(timezone.utc).isoformat(),
            "forced": True,
        })

        if phase == GamePhase.REVIEW:
            game["ended_at"] = datetime.now(timezone.utc).isoformat()

        self._sync_to_db(game)

        config = PHASE_CONFIG[phase]
        return {
            "success": True,
            "previous_phase": previous,
            "current_phase": phase.value,
            "display_name": config["display_name"],
            "phase_prompt": config["phase_prompt"],
        }

    def _sync_to_db(self, game_state: dict) -> None:
        """将游戏状态同步到数据库。"""
        db_session = get_session()
        try:
            game_id = game_state["game_id"]
            game_session = db_session.query(GameSession).filter(
                GameSession.session_id == game_id
            ).first()

            if not game_session:
                game_session = GameSession(
                    id=f"gs_{uuid.uuid4().hex[:8]}",
                    session_id=game_id,
                    script_id=game_state.get("script_id", ""),
                )
                db_session.add(game_session)

            game_session.current_phase = game_state["current_phase"]
            game_session.phase_history = game_state.get("phase_history", [])
            game_session.status = "completed" if game_state.get("ended_at") else "active"
            game_session.result = {
                "votes": game_state.get("votes", []),
                "vote_result": game_state.get("vote_result"),
                "hints_used": game_state.get("hints_used", 0),
                "chat_count": game_state.get("chat_count", 0),
            }

            if game_state.get("ended_at"):
                try:
                    game_session.ended_at = datetime.fromisoformat(game_state["ended_at"])
                except (ValueError, TypeError):
                    game_session.ended_at = datetime.now(timezone.utc)

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logger.error(f"同步游戏状态到数据库失败: {e}")
        finally:
            db_session.close()


# ============================
# 全局单例
# ============================

game_engine = GameEngine()
