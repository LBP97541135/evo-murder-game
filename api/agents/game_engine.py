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

PUBLIC_PRESENT_TARGETS = {"公开", "所有人", "all", "public"}

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

PLAYER_VOTERS = {"player", "林晓青", "player_default", "human"}


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
                    "current_phase": gs.current_phase or GamePhase.INTRO,
                    "phase_history": gs.phase_history or [],
                    "votes": gs.result.get("votes", []) if gs.result else [],
                    "vote_result": gs.result.get("vote_result") if gs.result else None,
                    "started_at": gs.started_at.isoformat() if gs.started_at else "",
                    "ended_at": gs.ended_at.isoformat() if gs.ended_at else None,
                    "hints_used": gs.result.get("hints_used", 0) if gs.result else 0,
                    "chat_count": gs.result.get("chat_count", 0) if gs.result else 0,
                    "public_evidences": gs.result.get("public_evidences", []) if gs.result else [],
                    "role_evidences": gs.result.get("role_evidences", {}) if gs.result else {},
                    "player_character_name": gs.result.get("player_character_name", "") if gs.result else "",
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

    def create_game(self, script_id: str, session_id: str = "", player_character_name: str = "") -> dict:
        """创建新游戏实例。

        同步初始化所有 Agent 的游戏状态（角色分配+胶囊注入）。
        player_character_name: 玩家选择扮演的角色名，为空则使用 is_player 标记的角色。
        """
        game_id = session_id or f"game_{uuid.uuid4().hex[:8]}"

        game_state = {
            "game_id": game_id,
            "script_id": script_id,
            "current_phase": GamePhase.INTRO,
            "phase_history": [{"phase": GamePhase.INTRO, "entered_at": datetime.now(timezone.utc).isoformat()}],
            "votes": [],
            "vote_result": None,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "ended_at": None,
            "hints_used": 0,
            "chat_count": 0,
            "agents": {},
            "player_character_name": player_character_name,
            "public_evidences": [],
        }

        self._games[game_id] = game_state

        # 初始化所有 Agent 游戏状态
        self._init_agent_game_states(game_id, script_id, player_character_name)

        # 注入全部历史胶囊到 Agent constitution
        self._load_capsules_for_agents()

        # 同步到数据库
        self._sync_to_db(game_state)

        return game_state

    def _init_agent_game_states(self, game_id: str, script_id: str, player_character_name: str = "") -> None:
        """从 orchestrator 获取所有 Agent，将角色和胶囊注入 AgentGameState。

        player_character_name: 玩家选择扮演的角色名，该角色不会被分配给 Agent。
        """
        from api.orchestrator import orchestrator
        from api.db.models import get_session, Script, Character

        game_state = self._games.get(game_id)
        if not game_state:
            return

        # 从数据库加载剧本角色，过滤掉真人玩家选择的角色
        companion_characters = []
        global_story = ""
        db_session = get_session()
        try:
            script = db_session.query(Script).filter(Script.id == script_id).first()
            if script:
                global_story = script.global_story or ""
                if player_character_name:
                    companion_characters = [
                        ch for ch in script.characters
                        if ch.name != player_character_name and not ch.is_victim
                    ]
                else:
                    companion_characters = [
                        ch for ch in script.characters
                        if not ch.is_player and not ch.is_victim
                    ]
        finally:
            db_session.close()

        # 为每个 Agent 创建游戏状态
        companion_idx = 0
        for key, agent in orchestrator.agents.items():
            if agent.role.value == "assistant":
                continue  # 个人助手不参与游戏

            state = AgentGameState(agent_key=key, session_id=game_id)
            state.constitution = agent.constitution  # 已被胶囊注入过
            state.global_story = global_story

            # 分配角色（companion 按顺序分配非玩家角色，DM 不分配角色）
            if agent.role.value == "companion" and companion_idx < len(companion_characters):
                ch = companion_characters[companion_idx]
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

    def apply_cast(
        self,
        game_id: str,
        cast: list[dict],
        player_character_name: str | None = None,
    ) -> dict:
        """按前端选角结果重新分配 Agent 角色（intro 阶段）。"""
        from api.orchestrator import orchestrator
        from api.db.models import get_session, Script

        game_state = self._games.get(game_id)
        if not game_state:
            raise ValueError(f"Game {game_id} not found")

        current_phase = game_state.get("current_phase", GamePhase.INTRO)
        if current_phase != GamePhase.INTRO:
            raise ValueError("只能在 intro 阶段调整选角")

        script_id = game_state.get("script_id", "")
        global_story = ""
        char_by_name: dict[str, dict] = {}
        db_session = get_session()
        try:
            script = db_session.query(Script).filter(Script.id == script_id).first()
            if not script:
                raise ValueError("Script not found")
            global_story = script.global_story or ""
            for ch in script.characters:
                char_by_name[ch.name] = {
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
        finally:
            db_session.close()

        if player_character_name:
            game_state["player_character_name"] = player_character_name

        def resolve_orchestrator_key(raw_key: str) -> str | None:
            if not raw_key:
                return None
            if raw_key in orchestrator.agents:
                return raw_key
            for ok, agent in orchestrator.agents.items():
                if getattr(agent, "persona_key", "") == raw_key:
                    return ok
            for ok, agent in orchestrator.agents.items():
                if agent.role.value != "companion":
                    continue
                if ok.endswith(f"_{raw_key}") or raw_key in ok:
                    return ok
            from api.agents.agent_persona_service import get_persona_by_key
            persona = get_persona_by_key(raw_key)
            if persona:
                pname = persona.get("name", "")
                for ok, agent in orchestrator.agents.items():
                    if agent.name == pname:
                        return ok
            return None

        new_agents: dict = {}
        for entry in cast:
            if entry.get("type") != "agent":
                continue
            raw_key = entry.get("agentKey") or entry.get("agent_key")
            agent_key = resolve_orchestrator_key(raw_key or "")
            role_name = (entry.get("role") or "").strip()
            if not agent_key or not role_name:
                continue
            if agent_key not in orchestrator.agents:
                continue
            ch = char_by_name.get(role_name)
            if not ch or ch.get("isVictim"):
                continue

            agent = orchestrator.agents[agent_key]
            if agent.role.value == "assistant":
                continue

            old_state = game_state["agents"].get(agent_key)
            state = AgentGameState(agent_key=agent_key, session_id=game_id)
            state.constitution = agent.constitution
            state.global_story = global_story
            state.character = ch
            state.all_actors = self._build_safe_actors_for_cast(
                cast, char_by_name, player_character_name, exclude_key=agent_key
            )
            state.loaded_capsule_ids = (
                getattr(old_state, "loaded_capsule_ids", [])
                if old_state
                else getattr(agent, "_loaded_capsule_ids", [])
            )
            new_agents[agent_key] = state

        for key, old_state in game_state["agents"].items():
            if key not in new_agents:
                agent = orchestrator.agents.get(key)
                if agent and agent.role.value == "dm":
                    new_agents[key] = old_state

        if not any(
            entry.get("type") == "agent"
            and (entry.get("agentKey") or entry.get("agent_key")) in new_agents
            for entry in cast
        ):
            raise ValueError("No valid agent cast entries")

        game_state["agents"].update(new_agents)
        game_state["cast"] = cast
        role_evidences = self._assign_role_evidences(game_state, script_id)
        game_state["role_evidences"] = role_evidences
        self._sync_to_db(game_state)

        logger.info(f"Applied cast for game {game_id}: {len(new_agents)} agents")
        return {"agents": len(new_agents), "cast": cast, "role_evidences": role_evidences}

    def _assign_role_evidences(self, game_state: dict, script_id: str) -> dict[str, list[dict]]:
        """为每个角色分配 4 件证物：2 件角色关联 + 2 件随机。"""
        import json
        import random
        from api.db.models import get_session, ScriptEvidence

        db_session = get_session()
        try:
            rows = db_session.query(ScriptEvidence).filter(
                ScriptEvidence.script_id == script_id
            ).all()
        finally:
            db_session.close()

        if not rows:
            return {}

        all_items: list[tuple[dict, list[str]]] = []
        by_role: dict[str, list[dict]] = {}
        for row in rows:
            related = (
                json.loads(row.related_characters)
                if isinstance(row.related_characters, str)
                else (row.related_characters or [])
            )
            item = {
                "id": row.id,
                "name": row.name,
                "description": row.description or "",
                "category": row.category or "physical",
            }
            all_items.append((item, related))
            for role_name in related:
                by_role.setdefault(role_name, []).append(item)

        assigned_ids: set[str] = set()
        result: dict[str, list[dict]] = {}

        def pick_for_role(role_name: str) -> list[dict]:
            role_pool = list(by_role.get(role_name, []))
            random.shuffle(role_pool)

            fixed: list[dict] = []
            for item in role_pool:
                if len(fixed) >= 2:
                    break
                if item["id"] not in assigned_ids:
                    fixed.append(item)
                    assigned_ids.add(item["id"])

            if len(fixed) < 2:
                fallback = [it for it, _ in all_items if it["id"] not in assigned_ids]
                random.shuffle(fallback)
                for item in fallback:
                    if len(fixed) >= 2:
                        break
                    fixed.append(item)
                    assigned_ids.add(item["id"])

            random_pool = [it for it, _ in all_items if it["id"] not in assigned_ids]
            random.shuffle(random_pool)
            extras = random_pool[: max(0, 4 - len(fixed))]
            for item in extras:
                assigned_ids.add(item["id"])

            return (fixed + extras)[:4]

        for _key, state in game_state.get("agents", {}).items():
            role_name = (state.character or {}).get("name", "")
            if not role_name or state.character.get("isVictim"):
                continue
            picks = pick_for_role(role_name)
            state.discovered_evidences = picks
            result[role_name] = picks

        player_role = game_state.get("player_character_name", "")
        if player_role and player_role not in result:
            result[player_role] = pick_for_role(player_role)

        return result

    def _build_safe_actors_for_cast(
        self,
        cast: list[dict],
        char_by_name: dict[str, dict],
        player_character_name: str | None,
        exclude_key: str,
    ) -> list:
        """从 cast 构建其他角色的安全信息（不含 secret/violation）。"""
        actors = []
        seen_names: set[str] = set()
        for entry in cast:
            role_name = (entry.get("role") or "").strip()
            if not role_name or role_name in seen_names:
                continue
            if entry.get("type") == "agent":
                key = entry.get("agentKey") or entry.get("agent_key")
                if key == exclude_key:
                    continue
            ch = char_by_name.get(role_name)
            if not ch or ch.get("isVictim"):
                continue
            seen_names.add(role_name)
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
        if player_character_name and player_character_name not in seen_names:
            pch = char_by_name.get(player_character_name)
            if pch and not pch.get("isVictim"):
                actors.append({
                    "id": pch.get("id", ""),
                    "name": pch.get("name", ""),
                    "bio": pch.get("bio", ""),
                    "personality": pch.get("personality", ""),
                    "context": pch.get("context", ""),
                    "image": pch.get("image", ""),
                    "isVictim": pch.get("isVictim", False),
                    "isKiller": pch.get("isKiller", False),
                    "isAssistant": pch.get("isAssistant", False),
                    "isPlayer": pch.get("isPlayer", False),
                    "isPartner": pch.get("isPartner", False),
                    "roleType": pch.get("roleType", "suspect"),
                })
        return actors

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
                    "hints_used": game_session.result.get("hints_used", 0) if game_session.result else 0,
                    "chat_count": game_session.result.get("chat_count", 0) if game_session.result else 0,
                    "public_evidences": game_session.result.get("public_evidences", []) if game_session.result else [],
                    "role_evidences": game_session.result.get("role_evidences", {}) if game_session.result else {},
                    "player_character_name": game_session.result.get("player_character_name", "") if game_session.result else "",
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

    def record_evidence_presentation(
        self,
        game_id: str,
        evidence: dict,
        presented_by: str,
        presented_to: str,
        reason: str = "",
        ai_response: str = "",
    ) -> dict:
        """证物出示后写入 Agent 记忆，公开证物同步到 game.public_evidences。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        from api.agents.game_context import find_agent_key

        ev_id = evidence.get("id", "")
        ev_name = evidence.get("name", "")
        ev_desc = evidence.get("description") or evidence.get("basic_description", "")
        presented_to_norm = (presented_to or "").strip()
        is_public = (
            presented_to_norm in PUBLIC_PRESENT_TARGETS
            or presented_to_norm.lower() in PUBLIC_PRESENT_TARGETS
        )

        if is_public:
            memory_line = f"[公共证物] {presented_by} 公开出示「{ev_name}」"
        else:
            memory_line = f"[证物出示] {presented_by} 向{presented_to_norm}出示「{ev_name}」"
        if reason:
            memory_line += f"；理由：{reason}"
        if ai_response:
            memory_line += f"。反应：{ai_response}"

        if is_public:
            public_list = game.setdefault("public_evidences", [])
            if not any(e.get("id") == ev_id for e in public_list):
                public_list.append({
                    "id": ev_id,
                    "name": ev_name,
                    "description": ev_desc,
                    "presented_by": presented_by,
                    "reason": reason,
                    "ai_response": ai_response,
                    "presented_at": datetime.now(timezone.utc).isoformat(),
                })

            for _key, state in game.get("agents", {}).items():
                state.chat_history.append({"role": "public", "content": memory_line})
                if ev_id and not any(e.get("id") == ev_id for e in state.discovered_evidences):
                    state.discovered_evidences.append({
                        "id": ev_id,
                        "name": ev_name,
                        "description": ev_desc,
                        "source": "公开出示",
                        "visibility": "public",
                    })
        else:
            target_key = find_agent_key(game, presented_to_norm)
            if target_key:
                target_state = game.get("agents", {}).get(target_key)
                if target_state:
                    target_state.chat_history.append({"role": "private", "content": memory_line})
                    if ev_id and not any(e.get("id") == ev_id for e in target_state.discovered_evidences):
                        target_state.discovered_evidences.append({
                            "id": ev_id,
                            "name": ev_name,
                            "description": ev_desc,
                            "source": f"{presented_by}私聊出示",
                            "visibility": "private",
                        })

            presenter_key = find_agent_key(game, presented_by)
            if presenter_key:
                presenter_state = game.get("agents", {}).get(presenter_key)
                if presenter_state:
                    presenter_state.chat_history.append({
                        "role": presenter_key,
                        "content": memory_line,
                    })

        self._sync_to_db(game)
        return {"success": True, "public": is_public}

    def record_hint(self, game_id: str) -> None:
        """记录一次提示使用。"""
        game = self.get_game(game_id)
        if game:
            game["hints_used"] = game.get("hints_used", 0) + 1
            self._sync_to_db(game)

    def _get_correct_killer(self, game_id: str) -> str:
        game = self.get_game(game_id)
        if not game:
            return ""
        db_session = get_session()
        try:
            from api.db.models import Script
            script = db_session.query(Script).filter(Script.id == game.get("script_id", "")).first()
            if script:
                return (script.killer_role or script.fixed_killer or "").strip()
        finally:
            db_session.close()
        return ""

    def _get_votable_roles(self, game_id: str) -> list[str]:
        game = self.get_game(game_id)
        if not game:
            return []
        roles: list[str] = []
        for _key, state in game.get("agents", {}).items():
            ch = state.character or {}
            if ch.get("isVictim") or ch.get("roleType") == "dm":
                continue
            name = (ch.get("name") or "").strip()
            if name and name not in roles:
                roles.append(name)
        return roles

    def _vote_tallies(self, game: dict) -> dict[str, int]:
        tallies: dict[str, int] = {}
        for vote in game.get("votes", []):
            killer = vote.get("killer", "")
            if killer:
                tallies[killer] = tallies.get(killer, 0) + 1
        return tallies

    def _refresh_vote_result(self, game: dict, game_id: str) -> dict:
        """以玩家（侦探）投票为准判定胜负，并汇总票数。"""
        correct_killer = self._get_correct_killer(game_id)

        player_vote = next(
            (v for v in game.get("votes", []) if v.get("voter") in PLAYER_VOTERS),
            None,
        )
        primary = player_vote or (game.get("votes")[-1] if game.get("votes") else None)
        if not primary:
            return {}

        is_correct = (primary["killer"] == correct_killer) if correct_killer else True
        result = {
            "killer": primary["killer"],
            "motive": primary.get("motive", ""),
            "voter": primary.get("voter", "player"),
            "is_correct": is_correct,
            "correct_killer": correct_killer,
            "accused_killer": primary["killer"],
            "tallies": self._vote_tallies(game),
        }
        game["vote_result"] = result
        return result

    def submit_vote(self, game_id: str, killer: str, motive: str = "", voter: str = "player") -> dict:
        """提交推理投票（同一投票者可改票）。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        if GamePhase(game["current_phase"]) != GamePhase.VOTING:
            return {"error": "not_in_voting_phase"}

        killer = (killer or "").strip()
        if not killer:
            return {"error": "killer_required"}

        vote = {
            "voter": voter,
            "killer": killer,
            "motive": motive or "",
            "voted_at": datetime.now(timezone.utc).isoformat(),
        }

        votes = game.setdefault("votes", [])
        replaced = False
        for idx, existing in enumerate(votes):
            if existing.get("voter") == voter:
                votes[idx] = vote
                replaced = True
                break
        if not replaced:
            votes.append(vote)

        game["game_id"] = game_id
        result = self._refresh_vote_result(game, game_id)
        self._sync_to_db(game)

        is_player = voter in PLAYER_VOTERS
        is_correct = result.get("is_correct", True) if is_player else None
        correct_killer = result.get("correct_killer", "")

        return {
            "success": True,
            "is_correct": is_correct,
            "correct_killer": correct_killer if is_player and not is_correct else "",
            "message": (
                "推理正确！"
                if is_player and is_correct
                else f"推理有误，真凶是{correct_killer}"
                if is_player and correct_killer
                else "投票已记录"
            ),
            "votes": votes,
            "tallies": result.get("tallies", {}),
            "voted_count": len(votes),
            "vote_result": result,
        }

    def _generate_agent_vote(
        self,
        game_id: str,
        agent_key: str,
        state,
        suspects: list[str],
        correct_killer: str,
    ) -> tuple[str, str]:
        my_role = (state.character or {}).get("name", "").strip()
        others = [s for s in suspects if s and s != my_role]
        if not others:
            return "", ""

        if my_role == correct_killer:
            import random
            target = random.choice(others)
            return target, f"我认为{target}的嫌疑最大，多条线索指向其作案可能。"

        chat_recent = "\n".join(
            f"{m.get('role', '?')}: {m.get('content', '')}"
            for m in (state.chat_history or [])[-8:]
        )
        suspect_list = "、".join(others)
        prompt = (
            f"你是剧本杀角色「{my_role}」。现在进入投票阶段。\n"
            f"可选嫌疑人：{suspect_list}\n"
            f"你的记忆与讨论摘要：{state.compressed_summary or '（无）'}\n"
            f"最近对话：\n{chat_recent or '（无）'}\n\n"
            "请根据已知信息投票。输出严格 JSON：\n"
            '{"killer": "角色名", "motive": "30字内理由"}\n'
            "killer 必须是上述嫌疑人之一，不能投自己。"
        )
        try:
            import json
            from api.llm.llm_service import respond_initial

            raw = respond_initial(
                system_prompt=(
                    "你是剧本杀中的嫌疑人角色，正在独立提交推理投票。"
                    "不要泄露自己的秘密，按 JSON 输出。"
                ),
                user_message=prompt,
                temperature=0.6,
                max_tokens=200,
            )
            json_str = raw.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            parsed = json.loads(json_str)
            target = (parsed.get("killer") or "").strip()
            motive = (parsed.get("motive") or "").strip()
            if target not in others:
                target = others[0]
            return target, motive or f"综合讨论，我认为{target}最为可疑。"
        except Exception as e:
            logger.warning(f"Agent {agent_key} 投票 LLM 失败: {e}")
            import random
            target = random.choice(others)
            return target, f"根据现有线索，我投给{target}。"

    def submit_agent_votes(self, game_id: str) -> dict:
        """为所有 Agent 角色生成并提交投票。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        if GamePhase(game["current_phase"]) != GamePhase.VOTING:
            return {"error": "not_in_voting_phase"}

        suspects = self._get_votable_roles(game_id)
        correct_killer = self._get_correct_killer(game_id)
        if not suspects:
            return {"error": "no_suspects"}

        agent_results = []
        for agent_key, state in game.get("agents", {}).items():
            ch = state.character or {}
            if ch.get("isVictim") or ch.get("roleType") == "dm":
                continue
            role_name = (ch.get("name") or "").strip()
            if not role_name:
                continue
            if any(v.get("voter") == agent_key for v in game.get("votes", [])):
                continue

            target, motive = self._generate_agent_vote(
                game_id, agent_key, state, suspects, correct_killer,
            )
            if not target:
                continue

            vote_result = self.submit_vote(game_id, target, motive, voter=agent_key)
            agent_results.append({
                "agent_key": agent_key,
                "role": role_name,
                "killer": target,
                "motive": motive,
                "success": vote_result.get("success", False),
            })

        game = self.get_game(game_id) or game
        return {
            "success": True,
            "agent_votes": agent_results,
            "votes": game.get("votes", []),
            "tallies": self._vote_tallies(game),
            "vote_result": game.get("vote_result"),
            "voted_count": len(game.get("votes", [])),
        }

    def force_phase(
        self,
        game_id: str,
        target_phase: str,
        frontend_phase_index: int | None = None,
    ) -> dict:
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
        if frontend_phase_index is not None:
            game["frontend_phase_index"] = frontend_phase_index
        game["phase_history"].append({
            "phase": phase.value,
            "entered_at": datetime.now(timezone.utc).isoformat(),
            "forced": True,
        })

        if phase == GamePhase.REVIEW:
            game["ended_at"] = datetime.now(timezone.utc).isoformat()
            self._trigger_capsule_generation(game_id, game.get("script_id", ""))

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
        """记录公共喊话——被喊话者须立刻回复，但不改变发言队列顺序。"""
        game = self.get_game(game_id)
        if not game:
            return {"error": "game_not_found"}

        target_state = game.get("agents", {}).get(target_key)
        if not target_state:
            return {"error": "target_agent_not_found"}

        asker_label = asker_key if asker_key != "player" else "玩家"
        target_state.chat_history.append({
            "role": asker_label,
            "content": f"[喊话] {question}",
        })

        public_list = game.get("public_evidences") or []
        if public_list:
            pub_summary = "；".join(
                f"【{ev.get('presented_by', '?')} 公开】{ev.get('name', '?')}：{ev.get('description', '')}"
                for ev in public_list[-6:]
            )
            target_state.chat_history.append({
                "role": "public",
                "content": f"[喊话语境·已公开证物] {pub_summary}",
            })

        for key, state in game.get("agents", {}).items():
            if key == target_key:
                continue
            state.chat_history.append({
                "role": "public",
                "content": f"[喊话] {asker_label} 向{target_state.character.get('name', target_key)}喊话：{question}",
            })

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
                "public_evidences": game_state.get("public_evidences", []),
                "role_evidences": game_state.get("role_evidences", {}),
                "player_character_name": game_state.get("player_character_name", ""),
                "cast": game_state.get("cast", []),
                "frontend_phase_index": game_state.get("frontend_phase_index"),
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
        """进入复盘阶段时触发完整自进化流水线。"""
        try:
            from api.capsules.dm_evolution_service import run_full_evolution_pipeline
            result = run_full_evolution_pipeline(game_id)
            summary = result.get("evolution_summary", {})
            logger.info(
                f"复盘自进化完成: game={game_id}, "
                f"genes={summary.get('genes_created', 0)}, "
                f"capsules={summary.get('capsules_created', 0)}"
            )
        except Exception as e:
            logger.error(f"复盘自进化失败: {e}")

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
        """新局开始前，为所有 Agent 注入全部历史胶囊。"""
        try:
            from api.capsules.dm_evolution_service import load_all_capsules_prompt, _resolve_agent_db_id
            from api.orchestrator import orchestrator

            for key, agent in orchestrator.agents.items():
                if not agent.registered or not agent.node_id:
                    continue
                db_id = _resolve_agent_db_id(agent.node_id) or agent.node_id
                prompt = load_all_capsules_prompt(db_id, agent.role.value)
                if prompt and prompt not in (agent.constitution or ""):
                    agent.constitution = (agent.constitution or "") + prompt
                    logger.info(f"Agent {agent.name} 已注入全部历史胶囊")
        except Exception as e:
            logger.error(f"加载胶囊经验失败: {e}")


# ============================
# 全局单例
# ============================

game_engine = GameEngine()