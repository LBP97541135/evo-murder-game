"""
EvoMap Murder Game - Game Context Helper

从 game_engine 读取当前游戏状态，构建环境上下文 prompt 片段。
invoke.py 和 invoke_stream.py 共享此模块，避免重复代码。
"""

import logging
from api.agents.game_engine import game_engine, GamePhase, PHASE_CONFIG

logger = logging.getLogger(__name__)


# 两轮公共发言的专用阶段指引（前端 speech_phase 传入 intro / discussion）
PUBLIC_SPEECH_PROMPTS = {
    "intro": (
        "【公共讨论·第一轮：自我介绍】\n"
        "你正在公共讨论的第一轮，只做自我介绍，规则如下：\n"
        "1. 用第一人称，说明你的角色名、公开身份、与本案/现场的表面关系\n"
        "2. 可简要提及性格或职业背景，但不要展开推理或指控任何人\n"
        "3. 禁止：泄露角色秘密、出示证物、搜证、私聊、投票、剧透案件真相\n"
        "4. 禁止：质疑其他角色、抛出关键线索、扮演 DM\n"
        "5. 篇幅 80-150 字，语气符合角色性格，自然口语化\n"
        "6. 结尾可礼貌表示「请多关照」或「愿意配合调查」一类的话"
    ),
    "discussion": (
        "【公共讨论·第二轮：线索交流】\n"
        "你正在公共讨论的线索交流轮，规则如下：\n"
        "1. 针对最近讨论内容发表看法：回应他人、提出疑问、补充线索方向\n"
        "2. 可以合理质疑他人说法，但不得凭空捏造未获得的线索\n"
        "3. 禁止泄露角色 secret 中的隐藏信息；可基于已公开讨论做推理\n"
        "4. 若你持有证物且认为有助于讨论，可在发言末尾单独一行追加：\n"
        "   [出示证物:证物名称|出示理由]\n"
        "   每轮发言最多出示 1 件，且必须是你已持有的证物\n"
        "5. 若需当场向某角色或玩家追问，可在发言末尾单独一行追加：\n"
        "   [喊话:角色名或林晓青|问题内容]\n"
        "   被喊话者必须立刻回答，不改变当前发言顺序\n"
        "6. 禁止：私聊、搜证、投票、直接自曝凶手身份（除非角色设定允许）\n"
        "7. 篇幅 100-200 字，保持角色口吻，一次只聚焦 1-2 个观点"
    ),
}


def find_agent_key(game, actor_name: str) -> str | None:
    """通过角色名称查找 agent_key。

    前端 invoke 时传的 actor.name 是角色名（如"周野"），
    但 game_engine 中 Agent 的 key 是编排器 key（如"companion_白鸦"）。
    此函数遍历所有 agent 的 character name 来匹配。
    """
    agents = game.get("agents", {})
    if actor_name in agents:
        return actor_name
    for key, state in agents.items():
        if state.character.get("name") == actor_name:
            return key
    return None


def build_game_context_prompt(
    session_id: str,
    actor_name: str,
    speech_phase: str | None = None,
) -> str:
    """从 game_engine 读取当前游戏状态，构建环境上下文 prompt 片段。"""
    game = game_engine.get_game(session_id)
    if not game:
        return ""

    phase = game.get("current_phase", "")
    phase_config = PHASE_CONFIG.get(GamePhase(phase)) if phase else None

    agent_key = find_agent_key(game, actor_name)
    agent_state = game.get("agents", {}).get(agent_key) if agent_key else None

    parts = []

    if not speech_phase:
        frontend_index = game.get("frontend_phase_index")
        if frontend_index == 2:
            speech_phase = "intro"
        elif frontend_index == 4:
            speech_phase = "discussion"

    if speech_phase and speech_phase in PUBLIC_SPEECH_PROMPTS:
        parts.append(PUBLIC_SPEECH_PROMPTS[speech_phase])
    elif phase_config:
        parts.append(
            f"【当前游戏阶段】{phase_config['display_name']}\n{phase_config['description']}\n"
            f"阶段指引：{phase_config['phase_prompt']}"
        )
    else:
        parts.append(f"【当前游戏阶段】{phase}")

    if agent_state:
        if agent_state.compressed_summary:
            parts.append(f"【记忆摘要】{agent_state.compressed_summary}")
        if agent_state.key_facts:
            parts.append(
                "【已确认的关键事实】\n"
                + "\n".join(f"- {f}" for f in agent_state.key_facts[-5:])
            )
        if agent_state.discovered_evidences:
            ev_lines = []
            for ev in agent_state.discovered_evidences[-8:]:
                if ev.get("visibility") == "public":
                    continue
                ev_lines.append(f"- {ev.get('name', '?')}: {ev.get('description', '')}")
            if ev_lines:
                parts.append("【你当前持有的证物】\n" + "\n".join(ev_lines))

    public_evidences = game.get("public_evidences") or []
    if public_evidences:
        pub_lines = []
        for ev in public_evidences[-12:]:
            line = (
                f"- 【{ev.get('presented_by', '?')} 出示】"
                f"{ev.get('name', '?')}: {ev.get('description', '')}"
            )
            if ev.get("reason"):
                line += f"（理由：{ev['reason']}）"
            pub_lines.append(line)
        parts.append("【已公开证物（全场可见）】\n" + "\n".join(pub_lines))

    return "\n\n".join(parts)
