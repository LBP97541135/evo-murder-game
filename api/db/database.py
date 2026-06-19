"""
EvoMap Murder Game - Database Connection

PostgreSQL 连接池（生产）或 SQLite 回退（开发）。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.config.settings import DB_CONN_URL, SQLITE_PATH


def initialize():
    """初始化数据库——创建所有表。"""
    engine = get_engine()
    from api.db.models import Base
    Base.metadata.create_all(engine)


def get_engine():
    """获取数据库引擎。"""
    if DB_CONN_URL:
        return create_engine(DB_CONN_URL, echo=False)
    return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)


def get_session():
    """获取 SQLAlchemy Session（手动使用）。"""
    engine = get_engine()
    return Session(engine)


def get_db():
    """获取 SQLAlchemy Session（用于 FastAPI Depends 注入）。"""
    from api.db.models import get_db as _get_db
    return _get_db()
