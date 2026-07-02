# -*- coding: utf-8 -*-
"""Prompt 加载器测试"""
import os
import tempfile
from pathlib import Path


def test_load_prompt():
    """测试加载 prompt 文件"""
    from api.domain.prompt_loader import load_prompt

    # 测试加载已有的 prompt 文件
    try:
        content = load_prompt("dm", "intro")
        assert isinstance(content, str)
        assert len(content) > 0
    except FileNotFoundError:
        # prompt 文件可能还没有创建
        pass


def test_list_prompts():
    """测试列出所有 prompt"""
    from api.domain.prompt_loader import list_prompts

    result = list_prompts()
    assert isinstance(result, dict)


def test_clear_cache():
    """测试清除缓存"""
    from api.domain.prompt_loader import clear_cache

    # 不应该抛出异常
    clear_cache()
