"""EvoMap Murder Game - DB 模块"""
from api.db.base import get_db, Base  # noqa: F401


def initialize():
    """初始化数据库（创建所有表）"""
    from api.db.base import engine
    from api.models import script, session, agent, conversation, evidence, review  # noqa: F401
    Base.metadata.create_all(engine)
