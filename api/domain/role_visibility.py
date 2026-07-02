# -*- coding: utf-8 -*-
"""
角色可见性规则模块

定义不同角色在各游戏阶段可以看到的信息范围。
"""

from typing import Dict, List, Set

from api.domain.game_phase import GamePhase


# 角色类型枚举
class RoleType(str):
    """角色类型"""
    DETECTIVE = "detective"      # 侦探
    SUSPECT = "suspect"          # 嫌疑人
    WITNESS = "witness"          # 证人
    MURDERER = "murderer"        # 凶手
    NPC = "npc"                  # NPC


# 各角色在不同阶段可见的信息类型
ROLE_VISIBILITY: Dict[str, Dict[str, Set[str]]] = {
    RoleType.DETECTIVE: {
        GamePhase.SETUP: {"own_role", "game_rules"},
        GamePhase.INTRO: {"own_role", "game_rules", "story_background", "all_players"},
        GamePhase.SCRIPT_READING: {"own_role", "own_script", "game_rules", "story_background"},
        GamePhase.INVESTIGATION: {"own_role", "own_script", "evidence", "clues"},
        GamePhase.DEDUCTION: {"own_role", "own_script", "evidence", "clues", "discussion"},
        GamePhase.VOTING: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result"},
        GamePhase.REVEAL: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "truth"},
        GamePhase.REVIEW: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "truth", "full_story"},
    },
    RoleType.SUSPECT: {
        GamePhase.SETUP: {"own_role", "game_rules"},
        GamePhase.INTRO: {"own_role", "game_rules", "story_background", "all_players"},
        GamePhase.SCRIPT_READING: {"own_role", "own_script", "game_rules", "story_background"},
        GamePhase.INVESTIGATION: {"own_role", "own_script", "evidence", "clues"},
        GamePhase.DEDUCTION: {"own_role", "own_script", "evidence", "clues", "discussion"},
        GamePhase.VOTING: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result"},
        GamePhase.REVEAL: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "truth"},
        GamePhase.REVIEW: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "truth", "full_story"},
    },
    RoleType.WITNESS: {
        GamePhase.SETUP: {"own_role", "game_rules"},
        GamePhase.INTRO: {"own_role", "game_rules", "story_background"},
        GamePhase.SCRIPT_READING: {"own_role", "own_script", "game_rules", "story_background"},
        GamePhase.INVESTIGATION: {"own_role", "own_script", "evidence"},
        GamePhase.DEDUCTION: {"own_role", "own_script", "evidence", "discussion"},
        GamePhase.VOTING: {"own_role", "own_script", "evidence", "discussion", "vote_result"},
        GamePhase.REVEAL: {"own_role", "own_script", "evidence", "discussion", "vote_result", "truth"},
        GamePhase.REVIEW: {"own_role", "own_script", "evidence", "discussion", "vote_result", "truth", "full_story"},
    },
    RoleType.MURDERER: {
        GamePhase.SETUP: {"own_role", "game_rules", "murder_plan"},
        GamePhase.INTRO: {"own_role", "game_rules", "story_background", "all_players", "murder_plan"},
        GamePhase.SCRIPT_READING: {"own_role", "own_script", "game_rules", "story_background", "murder_plan"},
        GamePhase.INVESTIGATION: {"own_role", "own_script", "evidence", "clues", "murder_plan"},
        GamePhase.DEDUCTION: {"own_role", "own_script", "evidence", "clues", "discussion", "murder_plan"},
        GamePhase.VOTING: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "murder_plan"},
        GamePhase.REVEAL: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "truth"},
        GamePhase.REVIEW: {"own_role", "own_script", "evidence", "clues", "discussion", "vote_result", "truth", "full_story"},
    },
    RoleType.NPC: {
        GamePhase.SETUP: {"own_role", "game_rules"},
        GamePhase.INTRO: {"own_role", "game_rules", "story_background"},
        GamePhase.SCRIPT_READING: {"own_role", "own_script", "game_rules", "story_background"},
        GamePhase.INVESTIGATION: {"own_role", "own_script"},
        GamePhase.DEDUCTION: {"own_role", "own_script", "discussion"},
        GamePhase.VOTING: {"own_role", "own_script", "discussion", "vote_result"},
        GamePhase.REVEAL: {"own_role", "own_script", "discussion", "vote_result", "truth"},
        GamePhase.REVIEW: {"own_role", "own_script", "discussion", "vote_result", "truth", "full_story"},
    },
}


def get_visible_info(role_type: str, phase: str) -> Set[str]:
    """
    获取指定角色在指定阶段可见的信息类型
    
    Args:
        role_type: 角色类型
        phase: 游戏阶段
    
    Returns:
        可见信息类型集合
    """
    role_visibility = ROLE_VISIBILITY.get(role_type, {})
    return role_visibility.get(phase, set())


def can_see(role_type: str, phase: str, info_type: str) -> bool:
    """
    检查指定角色在指定阶段是否可以看到某类信息
    
    Args:
        role_type: 角色类型
        phase: 游戏阶段
        info_type: 信息类型
    
    Returns:
        是否可见
    """
    return info_type in get_visible_info(role_type, phase)


__all__ = [
    "RoleType",
    "ROLE_VISIBILITY",
    "get_visible_info",
    "can_see",
]
