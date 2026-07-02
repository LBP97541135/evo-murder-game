"""
EvoMap Murder Game - Database Connection

数据库连接入口，提供数据库初始化和会话管理。
"""

from api.db.base import engine, Base, SessionLocal, get_db


def initialize():
    """初始化数据库——创建所有表（幂等，仅新增不覆盖）。"""
    import os
    from api.config.settings import SQLITE_PATH

    # 确保 SQLite 数据库目录存在
    db_path = SQLITE_PATH
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # 导入所有模型以确保它们被注册
    from api.models import script, session, agent, conversation, evidence, review
    from api.models.agent_persona import AgentPersona  # noqa: F401

    Base.metadata.create_all(engine)
    return engine


def get_session():
    """获取 SQLAlchemy Session。"""
    return SessionLocal()


def get_engine():
    """获取数据库引擎。"""
    return engine


__all__ = ["initialize", "get_session", "get_engine", "get_db"]
