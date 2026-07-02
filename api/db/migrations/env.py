"""
Alembic 环境配置文件
用于数据库迁移的初始化和运行配置
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# 将项目根目录添加到 Python 路径，确保能导入 api 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入所有模型，确保 metadata 包含所有表定义
from api.models import (
    Script, ScriptCharacter, ScriptTruth,
    GameSession, GamePhaseEvent, GameCast,
    ConversationThread, ConversationMessage,
    EvidenceInstance,
    Agent, AgentRuntimeState,
    ReviewReport, ExperienceRecord, Skill, SkillUsageLog,
)
from api.db.base import Base

# Alembic 配置对象，用于访问 .ini 文件中的值
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置 metadata，用于自动生成迁移脚本
target_metadata = Base.metadata


def get_database_url():
    """
    动态获取数据库连接 URL
    优先从环境变量读取，否则使用配置文件中的默认值
    """
    # 从环境变量获取数据库连接 URL
    db_conn_url = os.getenv("DB_CONN_URL", "")
    
    if db_conn_url:
        # 如果配置了 PostgreSQL 或其他数据库，直接使用
        return db_conn_url
    else:
        # 否则使用 SQLite
        sqlite_path = os.getenv("SQLITE_PATH", "data/murder_mystery.db")
        return f"sqlite:///{sqlite_path}"


def run_migrations_offline():
    """
    在'离线'模式下运行迁移
    不需要实际的数据库连接，只生成 SQL 脚本
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    在'在线'模式下运行迁移
    创建实际的数据库连接并执行迁移
    """
    # 获取配置中的 URL 并动态覆盖
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# 根据当前运行模式选择执行方式
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
