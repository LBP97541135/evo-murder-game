# -*- coding: utf-8 -*-
"""
游戏规则模块

定义剧本杀游戏的核心规则和约束。
"""

# 玩家人数限制
MIN_PLAYERS = 4
MAX_PLAYERS = 8

# 投票规则
MIN_VOTES_TO_ACCUSE = 1  # 最少需要多少票才能指控

# 阶段切换条件
PHASE_TRANSITIONS = {
    "setup": ["intro"],
    "intro": ["script_reading"],
    "script_reading": ["investigation"],
    "investigation": ["deduction"],
    "deduction": ["voting"],
    "voting": ["reveal"],
    "reveal": ["review"],
    "review": [],  # 最终阶段，不可再切换
}


def can_transition(from_phase: str, to_phase: str) -> bool:
    """
    检查是否可以从一个阶段切换到另一个阶段
    
    Args:
        from_phase: 当前阶段
        to_phase: 目标阶段
    
    Returns:
        是否允许切换
    """
    allowed = PHASE_TRANSITIONS.get(from_phase, [])
    return to_phase in allowed


__all__ = [
    "MIN_PLAYERS",
    "MAX_PLAYERS",
    "MIN_VOTES_TO_ACCUSE",
    "PHASE_TRANSITIONS",
    "can_transition",
]
