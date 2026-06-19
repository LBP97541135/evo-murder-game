"""
EvoMap Murder Game - Database Connection

PostgreSQL 连接池（生产）或 SQLite 回退（开发）。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.settings import DB_CONN_URL, SQLITE_PATH
from api.models import Base


def initialize():
    """初始化数据库——创建所有表。"""
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_engine():
    """获取数据库引擎。"""
    if DB_CONN_URL:
        return create_engine(DB_CONN_URL, echo=False)
    return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)


def get_session():
    """获取 SQLAlchemy Session。"""
    engine = get_engine()
    return Session(engine)
