"""
EvoMap Murder Game - FastAPI Main Entry Point

应用初始化、中间件配置、路由挂载。
具体路由定义在 api/routes/ 下各模块中。
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.config.settings import DEBUG
from api.db.models import init_db
from api.agents.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

# ============================
# App Init
# ============================
app = FastAPI(
    title="EvoMap Murder Game",
    description="多Agent自进化剧本杀系统 - 基于 EvoMap GEP-A2A 协议",
    version="2.0.0",
    debug=DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# 全局编排器
orchestrator = AgentOrchestrator()

# 静态文件（如有前端 build）
static_dir = Path(__file__).parent.parent / "web" / "build"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================
# 挂载路由
# ============================
from api.routes.health import router as health_router
from api.routes.agents import router as agents_router
from api.routes.invoke import router as invoke_router
from api.routes.game import router as game_router
from api.routes.memory import router as memory_router
from api.routes.scripts import router as scripts_router
from api.routes.evidence import router as evidence_router

app.include_router(health_router)
app.include_router(agents_router, prefix="/agents", tags=["agents"])
app.include_router(invoke_router, prefix="/invoke", tags=["invoke"])
app.include_router(game_router, prefix="/game", tags=["game"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])
app.include_router(scripts_router, prefix="/db", tags=["scripts"])
app.include_router(evidence_router, prefix="/evidence", tags=["evidence"])
