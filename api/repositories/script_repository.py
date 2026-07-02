# -*- coding: utf-8 -*-
"""
剧本数据访问层
"""
from sqlalchemy.orm import Session
from api.models.script import Script, ScriptCharacter, ScriptTruth
from typing import Optional, List


class ScriptRepository:
    """剧本仓库 - 封装剧本相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, status: str = "active") -> List[Script]:
        """获取所有剧本（按状态筛选）"""
        return self.db.query(Script).filter(Script.status == status).all()

    def get_by_id(self, script_id: str) -> Optional[Script]:
        """根据 ID 获取剧本"""
        return self.db.query(Script).filter(Script.id == script_id).first()

    def create(self, script: Script) -> Script:
        """创建剧本"""
        self.db.add(script)
        self.db.commit()
        self.db.refresh(script)
        return script

    def update(self, script: Script) -> Script:
        """更新剧本"""
        self.db.merge(script)
        self.db.commit()
        self.db.refresh(script)
        return script

    def get_characters(self, script_id: str) -> List[ScriptCharacter]:
        """获取剧本的所有角色"""
        return self.db.query(ScriptCharacter).filter(ScriptCharacter.script_id == script_id).all()

    def get_truth(self, script_id: str) -> Optional[ScriptTruth]:
        """获取剧本真相"""
        return self.db.query(ScriptTruth).filter(ScriptTruth.script_id == script_id).first()
