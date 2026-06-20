"""
EvoMap Murder Game - Game Engine

游戏阶段状态机：控制一局剧本杀的完整生命周期。
阶段流转：intro → investigation → voting → reveal → review

每个阶段有：
  - 进入条件（can_enter）
  - 允许的操作（allowed_actions）
  - 退出条件（can_advance）
  - 阶段提示（phase_prompt）

v2.1 新增：
  - AgentGameState：每个 Agent 每局的运行时状态（记忆/行动/进化）
  - 阶段结束时记忆压缩（chat_history → compressed_summary）
  - 行动意图系统（Agent 自主决策 → 玩家批准）
"""

import uuid
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from api.db.models import get_session, GameSession, ConversationTurn, GameProgressRecord, AgentGameStateModel

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
# Agent 游戏状态（运行时）
# ============================

class AgentGameState:
    """每局游戏中每个 Agent 的运行时状态。

    Demo 精简版：记忆分两层（chat_history + compressed_summary），
    行动意图由 Agent 自主决策后推送给玩家审批。
    """

    def __init__(self, agent_key: str, session_id: str):
        self.agent_key = agent_key
        self.session_id = session_id

        # ---- 身份层（开局注入） ----
        self.character = {}           # AssignedCharacter 全部字段
        self.constitution = ""         # 已被胶囊注入过的 constitution
        self.all_actors = []           # SafeActor[]
        self.global_story = ""

        # ---- 记忆层（阶段结束时压缩） ----
        self.chat_history: list[dict] = []          # LLMMessage[] 当前阶段
        self.compressed_summary = ""                 # 上一阶段摘要
        self.key_facts: list[str] = []               # 上一阶段关键事实
        self.discovered_evidences: list[dict] = []   # 已发现证物 [{id, name, description}]

        # ---- 行动层 ----
        self.intents: dict = {}                      # 待审批的行动意图
        # intents 结构: {interject: {...}|null, private_chat: {...}|null, present_evidence: {...}|null}

        # ---- 进化层 ----
        self.observation_buffer: list[str] = []      # 观察到的事实
        self.loaded_capsule_ids: list[str] = []      # 本局加载的胶囊 ID

    def to_dict(self) -> dict:
        return {
            "agent_key": self.agent_key,
            "character": self.character,
            "constitution": self.constitution,
            "chat_history": self.chat_history[-20:],   # 只返回最近20条
            "compressed_summary": self.compressed_summary,
            "key_facts": self.key_facts,
            "discovered_evidences": self.discovered_evidences,
            "intents": self.intents,
            "loaded_capsule_ids": self.loaded_capsule_ids,
        }

    def to_db_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "agent_key": self.agent_key,
            "character_json": self.character,
            "constitution": self.constitution,
            "all_actors_json": self.all_actors,
            "global_story": self.global_story,
            "chat_history_json": self.chat_history,
            "compressed_summary": self.compressed_summary,
            "key_facts_json": self.key_facts,
            "discovered_evidences_json": self.discovered_evidences,
            "intents_json": self.intents,
            "observation_buffer_json": self.observation_buffer,
            "loaded_capsule_ids_json": self.loaded_capsule_ids,
        }

    @classmethod
    def from_db_dict(cls, d: dict) -> "AgentGameState":
        state = cls(d["agent_key"], d["session_id"])
        state.character = d.get("character_json", {})
        state.constitution = d.get("constitution", "")
        state.all_actors = d.get("all_actors_json", [])
        state.global_story = d.get("global_story", "")
        state.chat_history = d.get("chat_history_json", [])
        state.compressed_summary = d.get("compressed_summary", "")
        state.key_facts = d.get("key_facts_json", [])
        state.discovered_evidences = d.get("discovered_evidences_json", [])
        state.intents = d.get("intents_json", {})
        state.observation_buffer = d.get("observation_buffer_json", [])
        state.loaded_capsule_ids = d.get("loaded_capsule_ids_json", [])
        return state


class SpeakRoundState:
    """Minimal in-memory speaking round state for companion turn order."""

    def __init__(self, speakers: list[str], current_index: int = 0):
        self.speakers = [speaker for speaker in speakers if speaker]
        self.current_index = current_index if 0 <= current_index < len(self.speakers) else 0
        self.interject_stack: list[dict] = []
        self.round_active = bool(self.speakers)
        self.round_complete = not self.speakers

    @property
    def current_speaker(self) -> Optional[str]:
        if not self.round_active or self.round_complete or not self.speakers:
            return None
        if self.current_index >= len(self.speakers):
            return None
        return self.speakers[self.current_index]

    def queue(self) -> list[str]:
        current = self.current_speaker
        if not current:
            return []
        return [current]

    def next(self) -> dict:
        if not self.round_active:
            return self.to_dict()

        if self.interject_stack:
            restored = self.interject_stack.pop()
            self.current_index = restored.get("return_index", self.current_index)
        else:
            self.current_index += 1

        if self.current_index >= len(self.speakers):
            self.round_complete = True
            self.round_active = False

        return self.to_dict()

    def interject(self, speaker: str, reason: str = "") -> dict:
        if not speaker:
            return self.to_dict()

        current = self.current_speaker
        if current == speaker:
            return self.to_dict()

        if current is not None:
            self.interject_stack.append({
                "speaker": current,
                "return_index": self.current_index,
                "reason": reason,
            })

        if speaker in self.speakers:
            self.current_index = self.speakers.index(speaker)
        else:
            self.speakers.append(speaker)
            self.current_index = len(self.speakers) - 1

        self.round_active = True
        self.round_complete = False
        return self.to_dict()

    def to_dict(self) -> dict:
        return {
            "round_active": self.round_active,
            "round_complete": self.round_complete,
            "current_speaker": self.current_speaker,
            "queue": self.queue(),
            "all_speakers": list(self.speakers),
            "interject_stack": list(self.interject_stack),
        }


# ============================
# 游戏引擎
# ============================

class GameEngine:
    """游戏阶段状态机——驱动一局剧本杀的完整生命周期。

    每个活跃游戏维护:
      - game_state (阶段/投票/计数等)
      - agents[agent_key] => AgentGameState (每个 Agent 的运行时状态)
    """

    def __init__(self):
        self._games: dict[str, dict] = {}
        self._load_from_db()

    def _load_from_db(self) -> None:
        """从数据库恢复所有活跃游戏状态到内存。"""
        db_session = get_session()
        try:
            active_sessions = db_session.query(GameSession).filter(
                GameSession.status == "active"
            ).all()
            for gs in active_sessions:
                game_state = {
                    "game_id": gs.session_id,
                    "script_id": gs.script_id or "",
                    "player_role_id": gs.result.get("player_role_id", "") if gs.result else "",
                    "player_character": gs.result.get("player_character", {}) if gs.result else {},
                    "current_phase": gs.current_phase or GamePhase.INTRO,
                    "phase_history": gs.phase_history or [],
                    "votes": gs.result.get("votes", []) if gs.result else [],
                    "vote_result": gs.result.get("vote_result") if gs.result else None,
                    "started_at": gs.started_at.isoformat() if gs.started_at else "",
                    "ended_at": gs.ended_at.isoformat() if gs.ended_at else None,
                    "hints_used": gs.result.get("hints_used", 0) if gs.result else 0,
                    "chat_count": gs.result.get("chat_count", 0) if gs.result else 0,
                    "agents": {},
                }
                # 恢复每个 Agent 的状态（表可能不存在于旧数据库，捕捉异常）
                try:
                    agent_states = db_session.query(AgentGameStateModel).filter(
                        AgentGameStateModel.session_id == gs.session_id
                    ).all()
                    for ast in agent_states:
                        state = AgentGameState.from_db_dict({
                            "agent_key": ast.agent_key,
                            "session_id": ast.session_id,
                            "character_json": ast.character_json or {},
                            "constitution": ast.constitution or "",
                            "all_actors_json": ast.all_actors_json or [],
                            "global_story": ast.global_story or "",
                            "chat_history_json": ast.chat_history_json or [],
                            "compressed_summary": ast.compressed_summary or "",
                            "key_facts_json": ast.key_facts_json or [],
                            "discovered_evidences_json": ast.discovered_evidences_json or [],
                            "intents_json": ast.intents_json or {},
                            "observation_buffer_json": ast.observation_buffer_json or [],
                            "loaded_capsule_ids_json": ast.loaded_capsule_ids_json or [],
                        })
                        game_state["agents"][ast.agent_key] = state
                except Exception:
                    pass  # agent_game_states 表可能还不存在

                self._games[gs.session_id] = game_state
            if active_sessions:
                logger.info(f"从数据库恢复了 {len(active_sessions)} 个活跃游戏")
        except Exception as e:
            logger.error(f"从数据库恢复游戏状态失败: {e}")
        finally:
            db_session.close()

    def create_game(self, script_id: str, session_id: str = "", player_role_id: str = "") -> dict:
        """创建新游戏实例。

        同步初始化所有 Agent 的游戏状态（角色分配+胶囊注入）。
        """
        game_id = session_id or f"game_{uuid.uuid4().hex[:8]}"

        game_state = {
            "game_id": game_id,
            "script_id": script_id,
            "player_role_id": player_role_id,
            "player_character": {},
            "current_phase": GamePhase.INTRO,
            "phase_history": [{"phase": GamePhase.INTRO, "entered_at": datetime.now(timezone.utc).isoformat()}],
            "votes": [],
            "vote_result": None,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "ended_at": None,
            "hints_used": 0,
            "chat_count": 0,
            "agents": {},
        }

        self._games[game_id] = game_state

        # 初始化所有 Agent 游戏状态
        self._init_agent_game_states(game_id, script_id)

        # 同步到数据库
        self._sync_to_db(game_state)

        return game_state

    def _init_agent_game_states(self, game_id: str, script_id: str) -> None:
        """从 orchestrator 获取所有 Agent，将角色和胶囊注入 AgentGameState。"""
        from api.orchestrator import orchestrator
        from api.db.models import get_session, Script, Character

        game_state = self._games.get(game_id)
        if not game_state:
            return

        # 从数据库加载剧本角色
        characters = []
        global_story = ""
        db_session = get_session()
        try:
            script = db_session.query(Script).filter(Script.id == script_id).first()
            if script:
                global_story = script.global_story or ""
                characters = list(script.characters)
        finally:
            db_session.close()

        # 为每个 Agent 创建游戏状态
        player_role_id = game_state.get("player_role_id", "")
        player_character = None
        remaining_characters = list(characters)
        if player_role_id:
            for index, character in enumerate(characters):
                if character.id == player_role_id:
                    player_character = character
                    remaining_characters.pop(index)
                    break

        if player_character:
            game_state["player_character"] = {
                "id": player_character.id,
                "name": player_character.name,
                "bio": player_character.bio or "",
                "personality": player_character.personality or "",
                "context": player_character.context or "",
                "secret": player_character.secret or "",
                "violation": player_character.violation or "",
                "image": player_character.image_filename or player_character.image or "officer.png",
                "isVictim": player_character.is_victim,
                "isKiller": player_character.is_killer,
                "isAssistant": player_character.is_assistant,
                "isPlayer": True,
                "isPartner": player_character.is_partner,
                "roleType": player_character.role_type,
            }
        else:
            game_state["player_character"] = {}

        companion_idx = 0
        for key, agent in orchestrator.agents.items():
            if agent.role.value == "assistant":
                continue  # 个人助手不参与游戏

            state = AgentGameState(agent_key=key, session_id=game_id)
            state.constitution = agent.constitution  # 已被胶囊注入过
            state.global_story = global_story

            # 分配角色（companion 按顺序分配角色，DM 不分配角色）
            if agent.role.value == "companion" and companion_idx < len(remaining_characters):
                ch = remaining_characters[companion_idx]
                state.character = {
                    "id": ch.id,
                    "name": ch.name,
                    "bio": ch.bio or "",
                    "personality": ch.personality or "",
                    "context": ch.context or "",
                    "secret": ch.secret or "",
                    "violation": ch.violation or "",
                    "image": ch.image_filename or ch.image or "officer.png",
                    "isVictim": ch.is_victim,
                    "isKiller": ch.is_killer,
                    "isAssistant": ch.is_assistant,
                    "isPlayer": ch.is_player,
                    "isPartner": ch.is_partner,
                    "roleType": ch.role_type,
                }
                companion_idx += 1
            elif agent.role.value == "dm":
                state.character = {"name": agent.name, "roleType": "dm"}

            # 构建 all_actors（其他角色的公开信息）
            state.all_actors = self._build_safe_actors(game_id, key)

            # 记录胶囊 ID
            state.loaded_capsule_ids = getattr(agent, "_loaded_capsule_ids", [])

            game_state["agents"][key] = state

        logger.info(
            f"已初始化 {len(game_state['agents'])} 个 Agent 游戏状态 "
            f"(game={game_id}, script={script_id})"
        )

    def _build_safe_actors(self, game_id: str, exclude_key: str) -> list:
        """构建其他 Agent 的安全角色信息（过滤 secret/violation）。"""
        game_state = self._games.get(game_id)
        if not game_state:
            return []

        actors = []
        for key, state in game_state["agents"].items():
            if key == exclude_key:
                continue
            ch = state.character
            actors.append({
                "id": ch.get("id", ""),
                "name": ch.get("name", ""),
                "bio": ch.get("bio", ""),
                "personality": ch.get("personality", ""),
                "context": ch.get("context", ""),
                "image": ch.get("image", ""),
                "isVictim": ch.get("isVictim", False),
                "isKiller": ch.get("isKiller", False),
                "isAssistant": ch.get("isAssistant", False),
                "isPlayer": ch.get("isPlayer", False),
                "isPartner": ch.get("isPartner", False),
                "roleType": ch.get("roleType", "suspect"),
            })
        return actors

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
                    "agents": {},
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
            return True
        elif phase == GamePhase.INVESTIGATION:
            return game.get("chat_count", 0) >= 3
        elif phase == GamePhase.VOTING:
            return game.get("vote_result") is not None
        elif phase == GamePhase.REVEAL:
            return True
        elif phase == GamePhase.REVIEW:
            return False

        return False

    def advance_phase(self, game_id: str) -> dict:
        """推进到下一阶段，并触发记忆压缩。

        v2.2 新增：进入 REVEAL 阶段时自动触发后剧情（凶手交代 + DM 真相揭晓）。
        """
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        if not self.can_advance(game_id):
            current = GamePhase(game["current_phase"])
            config = PHASE_CONFIG[current]
            return {"error": "cannot_advance", "reason": f"当前阶段({config['display_name']})不满足推进条件"}

        current_phase = GamePhase(game["current_phase"])
        current_idx = PHASE_ORDER.index(current_phase)

        if current_idx >= len(PHASE_ORDER) - 1:
            return {"error": "already_final_phase"}

        # === 触发记忆压缩（压缩当前阶段 chat_history） ===
        self._compress_all_agent_memories(game_id, current_phase.value)

        next_phase = PHASE_ORDER[current_idx + 1]
        game["current_phase"] = next_phase.value
        game["phase_history"].append({
            "phase": next_phase.value,
            "entered_at": datetime.now(timezone.utc).isoformat(),
        })

        if next_phase == GamePhase.REVIEW:
            game["ended_at"] = datetime.now(timezone.utc).isoformat()
            self._trigger_capsule_generation(game_id, game.get("script_id", ""))

        # === 进入 REVEAL 阶段时自动触发生成后剧情数据 ===
        reveal_data = None
        if next_phase == GamePhase.REVEAL and current_phase == GamePhase.VOTING:
            reveal_data = self._auto_post_game_reveal(game_id)

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
            "reveal": reveal_data,  # 附带后剧情数据，前端可直接使用
        }

    def _compress_all_agent_memories(self, game_id: str, phase_name: str) -> None:
        """DM 宣布阶段结束时，为每个 Agent 压缩当前阶段记忆。

        调用 LLM 将 chat_history 摘要为 2-3 句话 + 关键事实列表，
        然后清空 chat_history 准备下一阶段。
        """
        from api.llm.llm_service import MEMORY_COMPRESSION_PROMPT, respond_initial

        game = self._games.get(game_id)
        if not game or not game.get("agents"):
            return

        for key, state in game["agents"].items():
            if not state.chat_history:
                continue

            try:
                chat_text = "\n".join(
                    f"{m.get('role', 'unknown')}: {m.get('content', '')}"
                    for m in state.chat_history[-30:]  # 最多压缩最近30条
                )

                user_msg = f"阶段：{phase_name}\n\n对话内容：\n{chat_text}\n\n{MEMORY_COMPRESSION_PROMPT}"

                result_str = respond_initial(
                    system_prompt="你是一个对话摘要专家。请严格按 JSON 格式输出。",
                    user_message=user_msg,
                    temperature=0.3,
                    max_tokens=1024,
                )

                # 解析 JSON
                try:
                    json_str = result_str.strip()
                    if "```json" in json_str:
                        json_str = json_str.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_str:
                        json_str = json_str.split("```")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                    state.compressed_summary = result.get("summary", "")
                    state.key_facts = result.get("key_facts", [])
                except (json.JSONDecodeError, IndexError):
                    # LLM 返回非 JSON，直接用原文前200字做摘要
                    state.compressed_summary = chat_text[:200]
                    state.key_facts = []

                # 清空当前阶段聊天记录
                state.chat_history = []

            except Exception as e:
                logger.error(f"Agent {key} 记忆压缩失败: {e}")
                state.compressed_summary = ""
                state.key_facts = []

    def record_chat(self, game_id: str, from_agent: str = "", content: str = "") -> None:
        """记录一次对话。

        如果指定了 from_agent 和 content，同时写入对应 Agent 的 chat_history。
        """
        game = self.get_game(game_id)
        if not game:
            return

        game["chat_count"] = game.get("chat_count", 0) + 1

        if from_agent and content:
            agent_state = game.get("agents", {}).get(from_agent)
            if agent_state:
                agent_state.chat_history.append({
                    "role": from_agent,
                    "content": content,
                })

        self._sync_to_db(game)

    def record_hint(self, game_id: str) -> None:
        """记录一次提示使用。"""
        game = self.get_game(game_id)
        if game:
            game["hints_used"] = game.get("hints_used", 0) + 1
            self._sync_to_db(game)

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

    # ============================
    # Agent 游戏状态 API
    # ============================

    def _companion_keys(self, game: dict) -> list[str]:
        return [
            key
            for key, state in game.get("agents", {}).items()
            if state.character.get("roleType") == "companion"
        ]

    def init_speak_round(self, game_id: str) -> dict:
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        speak_round = SpeakRoundState(self._companion_keys(game))
        game["speak_round"] = speak_round
        self._sync_to_db(game)
        return {"success": True, **speak_round.to_dict()}

    def get_speak_round(self, game_id: str) -> dict:
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        speak_round = game.get("speak_round")
        if not speak_round:
            return {"error": "speak_round_not_initialized"}

        if hasattr(speak_round, "to_dict"):
            return {"success": True, **speak_round.to_dict()}
        if isinstance(speak_round, dict):
            return {"success": True, **speak_round}
        return {"error": "invalid_speak_round_state"}

    def next_speaker(self, game_id: str) -> dict:
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        speak_round = game.get("speak_round")
        if not speak_round:
            return {"error": "speak_round_not_initialized"}

        result = speak_round.next()
        self._sync_to_db(game)
        return {"success": True, **result}

    def start_new_round(self, game_id: str) -> dict:
        return self.init_speak_round(game_id)

    def get_agent_state(self, game_id: str, agent_key: str) -> Optional[dict]:
        """获取指定 Agent 的游戏状态。"""
        game = self.get_game(game_id)
        if not game:
            return None
        state = game.get("agents", {}).get(agent_key)
        return state.to_dict() if state else None

    def generate_agent_intents(self, game_id: str, agent_key: str) -> dict:
        """让 Agent 根据局势自主决策行动意图。

        输入：Agent 当前状态（角色+记忆+阶段）
        输出：intents 结构化数据（插队/私聊/出示证物）
        """
        from api.llm.llm_service import INTENT_GENERATION_PROMPT, respond_initial

        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        state = game.get("agents", {}).get(agent_key)
        if not state:
            return {"error": "agent_not_found"}

        # 构建输入
        character_info = json.dumps(state.character, ensure_ascii=False, indent=2)
        chat_recent = "\n".join(
            f"{m.get('role', '?')}: {m.get('content', '')}"
            for m in state.chat_history[-10:]
        )
        phase = game.get("current_phase", "")

        user_msg = (
            f"## 角色信息\n{character_info}\n\n"
            f"## 你的记忆摘要\n上一阶段：{state.compressed_summary or '（无）'}\n"
            f"关键事实：{json.dumps(state.key_facts, ensure_ascii=False)}\n\n"
            f"## 当前阶段\n{phase}\n\n"
            f"## 最近对话\n{chat_recent or '（无）'}\n\n"
            f"## 已知证物\n{json.dumps(state.discovered_evidences, ensure_ascii=False)}\n\n"
            f"{INTENT_GENERATION_PROMPT}"
        )

        try:
            result_str = respond_initial(
                system_prompt=state.constitution,
                user_message=user_msg,
                temperature=0.5,
                max_tokens=1024,
            )

            # 解析 JSON
            json_str = result_str.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            intents = json.loads(json_str)

            # 保存意图
            state.intents = intents
            self._sync_agent_state_to_db(game_id, agent_key, state)

            return {
                "success": True,
                "agent_key": agent_key,
                "intents": intents,
            }

        except Exception as e:
            logger.error(f"Agent {agent_key} 意图生成失败: {e}")
            state.intents = {}
            return {
                "success": False,
                "agent_key": agent_key,
                "intents": {},
                "error": str(e),
            }

    def approve_intent(self, game_id: str, agent_key: str, intent_type: str, approved: bool) -> dict:
        """玩家批准或拒绝 Agent 的某个行动意图。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        state = game.get("agents", {}).get(agent_key)
        if not state:
            return {"error": "agent_not_found"}

        intent = state.intents.get(intent_type) if isinstance(state.intents, dict) else None
        if not intent:
            return {"error": f"no_{intent_type}_intent"}

        if approved:
            # 批准：执行意图并清掉
            result = self._execute_intent(game_id, agent_key, intent_type, intent)
            state.intents[intent_type] = None
            return result
        else:
            # 拒绝：清掉该意图
            state.intents[intent_type] = None
            return {"success": True, "message": f"意图 {intent_type} 已被拒绝"}

    def _execute_intent(self, game_id: str, agent_key: str, intent_type: str, intent: dict) -> dict:
        """执行已批准的意图。"""
        state = self._games.get(game_id, {}).get("agents", {}).get(agent_key)
        if not state:
            return {"error": "agent_not_found"}

        if intent_type == "interject":
            # 插队发言：将理由作为发言追加到 chat_history
            reason = intent.get("reason", "")
            state.chat_history.append({
                "role": agent_key,
                "content": f"[插队发言] {reason}",
            })
            self.record_chat(game_id, from_agent=agent_key, content=reason)
            return {"success": True, "action": "interject", "content": reason}

        elif intent_type == "private_chat":
            target = intent.get("target", "")
            topic = intent.get("topic", "")
            return {
                "success": True,
                "action": "private_chat",
                "from": agent_key,
                "to": target,
                "content": topic,
            }

        elif intent_type == "present_evidence":
            ev_id = intent.get("evidence_id", "")
            target = intent.get("target", "")
            reason = intent.get("reason", "")
            return {
                "success": True,
                "action": "present_evidence",
                "evidence_id": ev_id,
                "from": agent_key,
                "to": target,
                "reason": reason,
            }

        return {"error": f"unknown_intent_type: {intent_type}"}

    def get_agent_intents(self, game_id: str, agent_key: str) -> dict:
        """获取 Agent 当前待审批的意图。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        state = game.get("agents", {}).get(agent_key)
        if not state:
            return {"error": "agent_not_found"}

        return {
            "success": True,
            "intents": state.intents or {},
        }

    # ============================
    # 私聊系统
    # ============================

    def send_private_message(
        self, game_id: str, from_key: str, to_key: str, content: str
    ) -> dict:
        """发送私聊消息。

        Args:
            from_key: 发送者 agent_key 或 "player"
            to_key: 接收者 agent_key
            content: 消息内容
        Returns:
            {"success": bool, "thread_id": str, "message": dict}
        """
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        # 确保接收者存在
        to_state = game.get("agents", {}).get(to_key)
        if not to_state:
            return {"error": "recipient_not_found"}

        # 生成线程 ID（两人之间的私聊共享一个 thread）
        participants = sorted([from_key, to_key])
        thread_id = f"pm_{participants[0]}_{participants[1]}"

        # 初始化私聊存储
        if "private_threads" not in game:
            game["private_threads"] = {}

        if thread_id not in game["private_threads"]:
            game["private_threads"][thread_id] = {
                "thread_id": thread_id,
                "participants": [from_key, to_key],
                "messages": [],
            }

        msg = {
            "from": from_key,
            "to": to_key,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        game["private_threads"][thread_id]["messages"].append(msg)

        # 写入接收者的 chat_history
        to_state.chat_history.append({
            "role": from_key,
            "content": f"[私聊] {content}",
        })

        self._sync_to_db(game)

        return {
            "success": True,
            "thread_id": thread_id,
            "message": msg,
        }

    def get_private_threads(self, game_id: str, agent_key: str) -> dict:
        """获取某个角色参与的所有私聊线程。

        Args:
            agent_key: 查询的角色 key，或 "player"
        Returns:
            {"success": bool, "threads": list}
        """
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        threads = game.get("private_threads", {})
        my_threads = []
        for tid, thread in threads.items():
            if agent_key in thread.get("participants", []):
                my_threads.append(thread)

        return {
            "success": True,
            "threads": my_threads,
        }

    def get_private_thread(self, game_id: str, thread_id: str) -> dict:
        """获取指定私聊线程的消息历史。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        thread = game.get("private_threads", {}).get(thread_id)
        if not thread:
            return {"error": "thread_not_found"}

        return {
            "success": True,
            "thread": thread,
        }

    # ============================
    # 强制回答
    # ============================

    def force_answer(
        self, game_id: str, asker_key: str, target_key: str, question: str
    ) -> dict:
        """强制指定 Agent 回答问题——插入发言队列最前面，其他角色不可插队。

        Args:
            asker_key: 提问者（通常是 "player"）
            target_key: 被指定的 Agent key
            question: 问题内容
        Returns:
            {"success": bool, "target_key": str, "question": str}
        """
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        # 确认目标 Agent 存在
        target_state = game.get("agents", {}).get(target_key)
        if not target_state:
            return {"error": "target_agent_not_found"}

        # 写入目标 Agent 的 chat_history
        target_state.chat_history.append({
            "role": asker_key,
            "content": f"[强制回答] {question}",
        })

        # 如果有发言轮次，将目标插入队列最前面
        speak_round = game.get("speak_round")
        if speak_round:
            speak_round.interject(target_key, reason=f"被{asker_key}强制指定回答")

        # 记录强制回答状态
        if "force_answer_state" not in game:
            game["force_answer_state"] = None
        game["force_answer_state"] = {
            "asker": asker_key,
            "target": target_key,
            "question": question,
            "active": True,
        }

        self._sync_to_db(game)

        return {
            "success": True,
            "target_key": target_key,
            "target_name": target_state.character.get("name", target_key),
            "question": question,
        }

    def clear_force_answer(self, game_id: str) -> dict:
        """清除强制回答状态（回答完毕后调用）。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        game["force_answer_state"] = None
        self._sync_to_db(game)

        return {"success": True}

    def add_chat_to_agent(self, game_id: str, agent_key: str, role: str, content: str) -> None:
        """向指定 Agent 的 chat_history 追加一条消息。"""
        game = self._games.get(game_id)
        if not game:
            return

        state = game.get("agents", {}).get(agent_key)
        if not state:
            return

        state.chat_history.append({"role": role, "content": content})
        self._sync_agent_state_to_db(game_id, agent_key, state)

    # ============================
    # 持久化
    # ============================

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
                "player_role_id": game_state.get("player_role_id", ""),
                "player_character": game_state.get("player_character", {}),
            }

            if game_state.get("ended_at"):
                try:
                    game_session.ended_at = datetime.fromisoformat(game_state["ended_at"])
                except (ValueError, TypeError):
                    game_session.ended_at = datetime.now(timezone.utc)

            db_session.commit()

            # 同步所有 Agent 状态
            for key, state in game_state.get("agents", {}).items():
                self._sync_agent_state_to_db(game_id, key, state, db_session)

        except Exception as e:
            db_session.rollback()
            logger.error(f"同步游戏状态到数据库失败: {e}")
        finally:
            db_session.close()

    def _sync_agent_state_to_db(self, game_id: str, agent_key: str, state: "AgentGameState", db_session=None) -> None:
        """将单一 Agent 状态同步到数据库。"""
        own_session = False
        if db_session is None:
            db_session = get_session()
            own_session = True

        try:
            db_state = db_session.query(AgentGameStateModel).filter(
                AgentGameStateModel.session_id == game_id,
                AgentGameStateModel.agent_key == agent_key,
            ).first()

            if not db_state:
                db_state = AgentGameStateModel(
                    session_id=game_id,
                    agent_key=agent_key,
                )
                db_session.add(db_state)

            db_state.character_json = state.character
            db_state.constitution = state.constitution
            db_state.all_actors_json = state.all_actors
            db_state.global_story = state.global_story
            db_state.chat_history_json = state.chat_history
            db_state.compressed_summary = state.compressed_summary
            db_state.key_facts_json = state.key_facts
            db_state.discovered_evidences_json = state.discovered_evidences
            db_state.intents_json = state.intents
            db_state.observation_buffer_json = state.observation_buffer
            db_state.loaded_capsule_ids_json = state.loaded_capsule_ids

            db_session.commit()

        except Exception as e:
            db_session.rollback()
            logger.error(f"同步 Agent 状态到数据库失败: {agent_key}: {e}")
        finally:
            if own_session:
                db_session.close()

    def _trigger_capsule_generation(self, game_id: str, script_id: str) -> None:
        """进入复盘阶段时自动触发胶囊生成流程。"""
        try:
            from api.capsules.capsule_service import review_and_generate_capsules
            result = review_and_generate_capsules(
                session_id=game_id,
                script_id=script_id,
            )
            logger.info(f"复盘胶囊生成完成: game={game_id}, genes={len(result.get('genes', []))}, capsules={len(result.get('capsules', []))}")
        except Exception as e:
            logger.error(f"复盘胶囊生成失败: {e}")

    def _auto_post_game_reveal(self, game_id: str) -> dict:
        """从 VOTING 进入 REVEAL 时自动触发后剧情生成。

        读取投票结果，调用 orchestrator.post_game_reveal() 生成：
          - 凶手交代（LLM 生成）
          - DM 真相揭晓（LLM 生成）
        结果存入 game_state，前端可在 REVEAL 阶段直接获取。
        """
        game = self._games.get(game_id)
        if not game:
            return {"error": "game_not_found"}

        vote_result = game.get("vote_result")
        if not vote_result:
            logger.warning(f"game={game_id} 无投票结果，无法生成后剧情")
            return {"error": "no_vote_result"}

        try:
            from api.orchestrator import orchestrator

            reveal_result = orchestrator.post_game_reveal(game_id, {
                "killer": vote_result.get("killer", ""),
                "motive": vote_result.get("motive", ""),
                "voter": vote_result.get("voter", "player"),
                "correct": vote_result.get("is_correct", False),
                "script_type": game.get("script_id", ""),
            })

            # 存入 game_state 供前端查询
            game["reveal_data"] = reveal_result

            logger.info(f"game={game_id} 后剧情自动生成完成")
            return reveal_result

        except Exception as e:
            logger.error(f"game={game_id} 后剧情自动生成失败: {e}")
            return {"error": str(e)}

    def _load_capsules_for_agents(self) -> None:
        """新局开始前，为所有 Agent 搜索并消费历史胶囊，融入 constitution。"""
        try:
            from api.capsules.capsule_service import get_capsules_for_agent
            from api.orchestrator import orchestrator

            for key, agent in orchestrator.agents.items():
                capsule_prompt = get_capsules_for_agent(
                    agent_role=agent.role.value,
                    signals=agent.domains,
                    limit=3,
                )
                if capsule_prompt:
                    agent.constitution += capsule_prompt
                    logger.info(f"Agent {agent.name} 已加载历史胶囊经验")
        except Exception as e:
            logger.error(f"加载胶囊经验失败: {e}")


# ============================
# 全局单例
# ============================

game_engine = GameEngine()
