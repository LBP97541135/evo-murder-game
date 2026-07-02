# -*- coding: utf-8 -*-
"""
游戏阶段定义模块

定义剧本杀游戏的各个阶段及其顺序。
"""

from enum import Enum


class GamePhase(str, Enum):
    """游戏阶段枚举"""
    SETUP = "setup"                          # 准备阶段
    INTRO = "intro"                          # 介绍阶段
    SCRIPT_READING = "script_reading"        # 剧本阅读
    INVESTIGATION = "investigation"          # 调查阶段
    DEDUCTION = "deduction"                  # 推理阶段
    VOTING = "voting"                        # 投票阶段
    REVEAL = "reveal"                        # 揭晓阶段
    REVIEW = "review"                        # 复盘阶段


# 游戏阶段的执行顺序
PHASE_ORDER = [
    GamePhase.SETUP,
    GamePhase.INTRO,
    GamePhase.SCRIPT_READING,
    GamePhase.INVESTIGATION,
    GamePhase.DEDUCTION,
    GamePhase.VOTING,
    GamePhase.REVEAL,
    GamePhase.REVIEW,
]


__all__ = ["GamePhase", "PHASE_ORDER"]
