"""
EvoMap Murder Game - FastAPI Main Entry Point

应用初始化、中间件配置、路由挂载。
具体路由定义在 api/routers/ 下各模块中。
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.config.settings import DEBUG, CORS_ORIGINS
from api.db.base import Base
from api.db.database import initialize as init_db

logger = logging.getLogger(__name__)

# ============================
# App Init
# ============================
app = FastAPI(
    title="AI Murder Game",
    description="AI剧本杀游戏系统 - EvoMap 为可选集成",
    version="2.0.0",
    debug=DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# 静态文件（如有前端 build）
static_dir = Path(__file__).parent.parent / "web" / "build"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================
# 挂载路由
# ============================
from api.routers.health import router as health_router
from api.routers.sessions import router as sessions_router
from api.routers.phases import router as phases_router
from api.routers.evidences import router as evidences_router
from api.routers.conversations import router as conversations_router
from api.routers.agents import router as agents_router
from api.routers.reviews import router as reviews_router
from api.routers.skills import router as skills_router
from api.routers.casting import router as casting_router
from api.routers.scripts import router as scripts_router
from api.routers.users import router as users_router

app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(phases_router)
app.include_router(evidences_router)
app.include_router(conversations_router)
app.include_router(agents_router)
app.include_router(reviews_router)
app.include_router(skills_router)
app.include_router(casting_router)
app.include_router(scripts_router)
app.include_router(users_router)
