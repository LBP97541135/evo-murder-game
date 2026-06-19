"""
EvoMap Murder Game - Database Connection

数据库连接入口，委托给 api.db.models 中的实现。
保留此文件以兼容旧导入路径。
"""

from api.db.models import get_engine, get_session, init_db as initialize  # noqa: F401
