# -*- coding: utf-8 -*-
"""
证物数据访问层
"""
from sqlalchemy.orm import Session
from api.models.evidence import EvidenceInstance
from typing import Optional, List


class EvidenceRepository:
    """证物仓库 - 封装证物相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, evidence: EvidenceInstance) -> EvidenceInstance:
        """创建证物实例"""
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_by_session(self, session_id: str) -> List[EvidenceInstance]:
        """获取会话的所有证物"""
        return self.db.query(EvidenceInstance).filter(
            EvidenceInstance.session_id == session_id
        ).all()

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceInstance]:
        """根据 ID 获取证物"""
        return self.db.query(EvidenceInstance).filter(
            EvidenceInstance.id == evidence_id
        ).first()

    def update(self, evidence: EvidenceInstance) -> EvidenceInstance:
        """更新证物"""
        self.db.merge(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_public(self, session_id: str) -> List[EvidenceInstance]:
        """获取会话的公开证物"""
        return self.db.query(EvidenceInstance).filter(
            EvidenceInstance.session_id == session_id,
            EvidenceInstance.is_public == True
        ).all()

    def get_public_by_session(self, session_id: str) -> List[EvidenceInstance]:
        """获取会话的公开证物（别名）"""
        return self.get_public(session_id)

    def create_from_script(self, session_id: str, script_id: str) -> List[EvidenceInstance]:
        """从剧本创建证物实例"""
        # TODO: 实现从剧本创建证物的逻辑
        return []
