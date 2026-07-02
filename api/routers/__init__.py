# -*- coding: utf-8 -*-
"""EvoMap Murder Game - 路由模块

导出所有路由供主应用注册使用。
"""

from api.routers.health import router as health_router
from api.routers.scripts import router as scripts_router
from api.routers.sessions import router as sessions_router
from api.routers.phases import router as phases_router
from api.routers.casting import router as casting_router
from api.routers.evidences import router as evidences_router
from api.routers.conversations import router as conversations_router
from api.routers.agents import router as agents_router
from api.routers.reviews import router as reviews_router
from api.routers.skills import router as skills_router
from api.routers.users import router as users_router

__all__ = [
    "health_router",
    "scripts_router",
    "sessions_router",
    "phases_router",
    "casting_router",
    "evidences_router",
    "conversations_router",
    "agents_router",
    "reviews_router",
    "skills_router",
    "users_router",
]
