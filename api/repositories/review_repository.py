# -*- coding: utf-8 -*-
"""
复盘报告数据访问层
"""
from sqlalchemy.orm import Session
from api.models.review import ReviewReport
from typing import Optional


class ReviewRepository:
    """复盘报告仓库 - 封装复盘报告相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, report: ReviewReport) -> ReviewReport:
        """创建复盘报告"""
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_session(self, session_id: str) -> Optional[ReviewReport]:
        """根据会话 ID 获取复盘报告"""
        return self.db.query(ReviewReport).filter(
            ReviewReport.session_id == session_id
        ).first()

    def update(self, report: ReviewReport) -> ReviewReport:
        """更新复盘报告"""
        self.db.merge(report)
        self.db.commit()
        self.db.refresh(report)
        return report
