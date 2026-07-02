"""
EvoMap Murder Game - 配置管理

从 .env 文件读取所有配置，统一管理 AI 推理、EvoMap A2A、数据库等参数。
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ============================
# AI 推理配置
# ============================
INFERENCE_SERVICE = os.getenv("INFERENCE_SERVICE", "openai")  # anthropic / openai / groq / openrouter / ollama
MODEL = os.getenv("MODEL", "")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
API_KEY = os.getenv("API_KEY", "")
PROMPTS_VERSION = os.getenv("PROMPTS_VERSION", "2.0.0")
MODEL_KEY = os.getenv("MODEL_KEY", "")

# Provider-specific URLs
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "")


# ============================
# EvoMap A2A Protocol 配置
# ============================
EVOMAP_HUB_URL = os.getenv("EVOMAP_HUB_URL", "")
EVOMAP_NODE_ID = os.getenv("EVOMAP_NODE_ID", "")
EVOMAP_NODE_SECRET = os.getenv("EVOMAP_NODE_SECRET", "")

# EvoMap LLM 中转站配置（OpenAI 兼容）
EVOMAP_LLM_BASE_URL = os.getenv("OPENAI_API_BASE", "")
EVOMAP_LLM_API_KEY = os.getenv("API_KEY", "")


# ============================
# 数据库配置
# ============================
DB_CONN_URL = os.getenv("DB_CONN_URL", "")  # PostgreSQL; 空=用 SQLite
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/murder_mystery.db")

# 兼容新代码的导入路径
if DB_CONN_URL:
    DATABASE_URL = DB_CONN_URL
else:
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"


# ============================
# 图像生成配置
# ============================
VOLC_ACCESS_KEY = os.getenv("VOLC_ACCESS_KEY", "")
VOLC_SECRET_KEY = os.getenv("VOLC_SECRET_KEY", "")


# ============================
# 应用配置
# ============================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")
