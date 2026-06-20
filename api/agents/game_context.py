"""
EvoMap Murder Game - Game Context Helper

从 game_engine 读取当前游戏状态，构建环境上下文 prompt 片段。
invoke.py 和 invoke_stream.py 共享此模块，避免重复代码。
"""

import logging
from api.agents.game_engine import game_engine, GamePhase, PHASE_CONFIG

logger = logging.getLogger(__name__)


def find_agent_key(game, actor_name: str) -> str | None:
    """通过角色名称查找 agent_key。

    前端 invoke 时传的 actor.name 是角色名（如"周野"），
    但 game_engine 中 Agent 的 key 是编排器 key（如"companion_白鸦"）。
    此函数遍历所有 agent 的 character name 来匹配。
    """
    agents = game.get("agents", {})
    # 先直接匹配 key
    if actor_name in agents:
        return actor_name
    # 再按 character name 匹配
    for key, state in agents.items():
        if state.character.get("name") == actor_name:
            return key
    return None


def build_game_context_prompt(session_id: str, actor_name: str) -> str:
    """从 game_engine 读取当前游戏状态，构建环境上下文 prompt 片段。

    注入信息：
      - 当前游戏阶段及阶段描述
      - 该 Agent 的压缩记忆和关键事实
      - 已发现的证物
      - 全局故事背景
      - 全局 phase_prompt

    通过 actor_name（角色名）自动匹配 agent_key。
    """
    game = game_engine.get_game(session_id)
    if not game:
        return ""

    phase = game.get("current_phase", "")
    phase_config = PHASE_CONFIG.get(GamePhase(phase)) if phase else None

    agent_key = find_agent_key(game, actor_name)
    agent_state = game.get("agents", {}).get(agent_key) if agent_key else None

    parts = []

    # 阶段信息
    if phase_config:
        parts.append(
            f"【当前游戏阶段】{phase_config['display_name']}\n{phase_config['description']}\n"
            f"阶段指引：{phase_config['phase_prompt']}"
        )
    else:
        parts.append(f"【当前游戏阶段】{phase}")

    # Agent 记忆
    if agent_state:
        if agent_state.compressed_summary:
            parts.append(f"【记忆摘要】{agent_state.compressed_summary}")
        if agent_state.key_facts:
            parts.append(f"【已确认的关键事实】\n" + "\n".join(f"- {f}" for f in agent_state.key_facts[-5:]))
        if agent_state.discovered_evidences:
            ev_lines = []
            for ev in agent_state.discovered_evidences[-8:]:
                ev_lines.append(f"- {ev.get('name', '?')}: {ev.get('description', '')}")
            parts.append("【已发现的证物】\n" + "\n".join(ev_lines))

    return "\n\n".join(parts)