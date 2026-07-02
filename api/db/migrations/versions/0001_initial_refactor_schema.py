"""初始重构 - 创建新表结构

Revision ID: 0001
Revises: 
Create Date: 2026-06-25

说明：
本迁移脚本创建重构后的新表结构。对于已存在的旧表（scripts, game_sessions），
暂时保留不动，新表使用不同的名称或直接创建全新表。

全新表（直接创建）：
- script_characters: 剧本角色表
- script_truths: 剧本真相表
- game_phase_events: 游戏阶段事件表
- game_casts: 游戏角色分配表
- conversation_threads: 对话线程表
- conversation_messages: 对话消息表
- evidence_instances: 证物实例表
- agents: Agent 主表
- agent_runtime_states: Agent 运行时状态表
- experience_records: 经验记录表
- skills: Skill 表
- skill_usage_logs: Skill 使用日志表
- review_reports: 复盘报告表

注意：
- scripts 和 game_sessions 表已存在，本脚本不处理
- 后续需要数据迁移脚本来处理旧表到新表的数据迁移
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """升级：创建新表结构"""
    
    # ========== 剧本域 ==========
    
    # 剧本角色表
    op.create_table(
        'script_characters',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('script_id', sa.String(), sa.ForeignKey('scripts.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('bio', sa.Text(), default=''),
        sa.Column('personality', sa.Text(), default=''),
        sa.Column('public_context', sa.Text(), default=''),
        sa.Column('private_secret', sa.Text(), default=''),
        sa.Column('behavior_rules', sa.Text(), default=''),
        sa.Column('role_type', sa.String(), default='suspect'),
        sa.Column('is_victim', sa.Boolean(), default=False),
        sa.Column('is_killer', sa.Boolean(), default=False),
        sa.Column('is_player_candidate', sa.Boolean(), default=True),
        sa.Column('avatar_image', sa.Text(), default=''),
        sa.Column('background_image', sa.Text(), default=''),
        sa.Column('order_index', sa.Integer(), default=0),
        sa.Column('metadata_json', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # 剧本真相表
    op.create_table(
        'script_truths',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('script_id', sa.String(), sa.ForeignKey('scripts.id'), nullable=False, unique=True),
        sa.Column('global_story', sa.Text(), default=''),
        sa.Column('truth_summary', sa.Text(), default=''),
        sa.Column('killer_character_id', sa.String(), default=''),
        sa.Column('motive', sa.Text(), default=''),
        sa.Column('method', sa.Text(), default=''),
        sa.Column('timeline', sa.Text(), default=''),
        sa.Column('reveal_text', sa.Text(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # ========== 游戏会话域 ==========
    
    # 游戏阶段事件表
    op.create_table(
        'game_phase_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('from_phase', sa.String(), default=''),
        sa.Column('to_phase', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), default=''),
        sa.Column('triggered_by', sa.String(), default=''),
        sa.Column('frontend_index', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # 游戏角色分配表
    op.create_table(
        'game_casts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('character_id', sa.String(), sa.ForeignKey('script_characters.id'), nullable=False),
        sa.Column('actor_type', sa.String(), nullable=False),  # human / agent / dm
        sa.Column('actor_id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), default=''),
        sa.Column('user_id', sa.String(), default=''),
        sa.Column('role_name', sa.String(), default=''),
        sa.Column('is_player', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # ========== 对话域 ==========
    
    # 对话线程表
    op.create_table(
        'conversation_threads',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('thread_type', sa.String(), nullable=False),  # public / private / dm / system
        sa.Column('title', sa.String(), default=''),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('participant_ids', sa.JSON(), default=[]),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # 对话消息表
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('thread_id', sa.String(), sa.ForeignKey('conversation_threads.id'), nullable=False),
        sa.Column('sender_type', sa.String(), nullable=False),  # human / agent / dm / system
        sa.Column('sender_id', sa.String(), default=''),
        sa.Column('sender_name', sa.String(), default=''),
        sa.Column('target_id', sa.String(), default=''),
        sa.Column('message_type', sa.String(), default='text'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('raw_prompt', sa.Text(), default=''),
        sa.Column('raw_response', sa.Text(), default=''),
        sa.Column('critique_response', sa.Text(), default=''),
        sa.Column('final_response', sa.Text(), default=''),
        sa.Column('visibility', sa.String(), default='public'),
        sa.Column('phase', sa.String(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # ========== 证物域 ==========
    
    # 证物实例表
    op.create_table(
        'evidence_instances',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('script_evidence_id', sa.String(), default=''),
        sa.Column('script_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), default=''),
        sa.Column('importance', sa.String(), default='medium'),
        sa.Column('basic_description', sa.Text(), default=''),
        sa.Column('detailed_description', sa.Text(), default=''),
        sa.Column('deep_description', sa.Text(), default=''),
        sa.Column('discovery_state', sa.String(), default='hidden'),
        sa.Column('visibility', sa.String(), default='private'),
        sa.Column('owner_character_id', sa.String(), default=''),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('image_path', sa.Text(), default=''),
        sa.Column('unlock_level', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # ========== Agent 域 ==========
    
    # Agent 主表
    op.create_table(
        'agents',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),  # dm / companion / assistant
        sa.Column('model', sa.String(), default=''),
        sa.Column('persona_id', sa.String(), default=''),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('domains', sa.JSON(), default=[]),
        sa.Column('identity_doc', sa.Text(), default=''),
        sa.Column('constitution', sa.Text(), default=''),
        sa.Column('external_provider', sa.String(), default=''),
        sa.Column('external_ref', sa.String(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # Agent 运行时状态表
    op.create_table(
        'agent_runtime_states',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('agent_id', sa.String(), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('character_id', sa.String(), default=''),
        sa.Column('phase', sa.String(), default=''),
        sa.Column('short_memory', sa.JSON(), default=[]),
        sa.Column('compressed_summary', sa.Text(), default=''),
        sa.Column('key_facts', sa.JSON(), default=[]),
        sa.Column('known_evidence_ids', sa.JSON(), default=[]),
        sa.Column('loaded_skill_ids', sa.JSON(), default=[]),
        sa.Column('intent_json', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # ========== 复盘与 Skill 域 ==========
    
    # 复盘报告表
    op.create_table(
        'review_reports',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('truth_summary', sa.Text(), default=''),
        sa.Column('player_result_json', sa.JSON(), default={}),
        sa.Column('key_clues_json', sa.JSON(), default=[]),
        sa.Column('timeline_json', sa.JSON(), default=[]),
        sa.Column('report_content', sa.Text(), default=''),
        sa.Column('generated_by', sa.String(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # 经验记录表
    op.create_table(
        'experience_records',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), default=''),
        sa.Column('script_id', sa.String(), default=''),
        sa.Column('agent_id', sa.String(), default=''),
        sa.Column('role', sa.String(), default=''),
        sa.Column('category', sa.String(), default=''),
        sa.Column('signals', sa.JSON(), default=[]),
        sa.Column('status', sa.String(), default='success'),
        sa.Column('self_score', sa.Float(), default=0.0),
        sa.Column('summary', sa.Text(), default=''),
        sa.Column('detail', sa.Text(), default=''),
        sa.Column('dm_reviewed', sa.Boolean(), default=False),
        sa.Column('dm_score', sa.Float(), default=0.0),
        sa.Column('dm_comment', sa.Text(), default=''),
        sa.Column('dm_suggestions', sa.Text(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # Skill 表
    op.create_table(
        'skills',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('version', sa.String(), default='1.0.0'),
        sa.Column('type', sa.String(), default='prompt_skill'),
        sa.Column('category', sa.String(), default=''),
        sa.Column('applicable_roles', sa.JSON(), default=[]),
        sa.Column('signals', sa.JSON(), default=[]),
        sa.Column('description', sa.Text(), default=''),
        sa.Column('prompt_content', sa.Text(), default=''),
        sa.Column('strategy', sa.Text(), default=''),
        sa.Column('examples', sa.Text(), default=''),
        sa.Column('anti_patterns', sa.Text(), default=''),
        sa.Column('source_type', sa.String(), default='manual'),
        sa.Column('source_experience_id', sa.String(), default=''),
        sa.Column('source_session_id', sa.String(), default=''),
        sa.Column('source_script_id', sa.String(), default=''),
        sa.Column('created_by_agent_id', sa.String(), default=''),
        sa.Column('quality_score', sa.Float(), default=0.0),
        sa.Column('effectiveness_score', sa.Float(), default=0.0),
        sa.Column('review_status', sa.String(), default='draft'),
        sa.Column('reviewed_by', sa.String(), default=''),
        sa.Column('review_comment', sa.Text(), default=''),
        sa.Column('injection_mode', sa.String(), default='append_system_prompt'),
        sa.Column('injection_priority', sa.Integer(), default=50),
        sa.Column('max_tokens', sa.Integer(), default=800),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('success_count', sa.Integer(), default=0),
        sa.Column('last_used_at', sa.DateTime()),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )
    
    # Skill 使用日志表
    op.create_table(
        'skill_usage_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('skill_id', sa.String(), sa.ForeignKey('skills.id'), nullable=False),
        sa.Column('session_id', sa.String(), default=''),
        sa.Column('agent_id', sa.String(), default=''),
        sa.Column('phase', sa.String(), default=''),
        sa.Column('injection_tokens', sa.Integer(), default=0),
        sa.Column('result_status', sa.String(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), default={}),
    )


def downgrade():
    """降级：删除新创建的表"""
    # 按照依赖关系的逆序删除表
    
    # Skill 域
    op.drop_table('skill_usage_logs')
    op.drop_table('skills')
    op.drop_table('experience_records')
    op.drop_table('review_reports')
    
    # Agent 域
    op.drop_table('agent_runtime_states')
    op.drop_table('agents')
    
    # 证物域
    op.drop_table('evidence_instances')
    
    # 对话域
    op.drop_table('conversation_messages')
    op.drop_table('conversation_threads')
    
    # 游戏会话域
    op.drop_table('game_casts')
    op.drop_table('game_phase_events')
    
    # 剧本域
    op.drop_table('script_truths')
    op.drop_table('script_characters')
