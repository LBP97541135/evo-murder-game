# -*- coding: utf-8 -*-
"""
基础配置模块

从现有 api/config/settings.py 导入配置，提供统一的配置访问接口。
"""

# 从现有配置模块导入所有配置
from api.config.settings import (
    # AI 推理配置
    INFERENCE_SERVICE,
    MODEL,
    MAX_TOKENS,
    API_KEY,
    PROMPTS_VERSION,
    MODEL_KEY,
    OLLAMA_URL,
    GROQ_API_BASE,
    OPENROUTER_API_BASE,
    OPENAI_API_BASE,
    # EvoMap A2A Protocol 配置
    EVOMAP_HUB_URL,
    EVOMAP_NODE_ID,
    EVOMAP_NODE_SECRET,
    EVOMAP_LLM_BASE_URL,
    EVOMAP_LLM_API_KEY,
    # 数据库配置
    DB_CONN_URL,
    SQLITE_PATH,
    # 图像生成配置
    VOLC_ACCESS_KEY,
    VOLC_SECRET_KEY,
    # 应用配置
    DEBUG,
)

__all__ = [
    "INFERENCE_SERVICE",
    "MODEL",
    "MAX_TOKENS",
    "API_KEY",
    "PROMPTS_VERSION",
    "MODEL_KEY",
    "OLLAMA_URL",
    "GROQ_API_BASE",
    "OPENROUTER_API_BASE",
    "OPENAI_API_BASE",
    "EVOMAP_HUB_URL",
    "EVOMAP_NODE_ID",
    "EVOMAP_NODE_SECRET",
    "EVOMAP_LLM_BASE_URL",
    "EVOMAP_LLM_API_KEY",
    "DB_CONN_URL",
    "SQLITE_PATH",
    "VOLC_ACCESS_KEY",
    "VOLC_SECRET_KEY",
    "DEBUG",
]
