# -*- coding: utf-8 -*-
"""
Skill 数据访问层
"""
from sqlalchemy.orm import Session
from api.models.review import Skill, SkillUsageLog, ExperienceRecord
from typing import Optional, List


class SkillRepository:
    """Skill 仓库 - 封装 Skill 相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def list(self, status: Optional[str] = None, category: Optional[str] = None) -> List[Skill]:
        """列出 Skill（别名，同 get_all）。"""
        return self.get_all(status=status, category=category)

    def get_all(self, status: Optional[str] = None, category: Optional[str] = None) -> List[Skill]:
        """获取所有 Skill（可按状态和分类筛选）"""
        query = self.db.query(Skill)
        if status:
            query = query.filter(Skill.status == status)
        if category:
            query = query.filter(Skill.category == category)
        return query.all()

    def get_by_id(self, skill_id: str) -> Optional[Skill]:
        """根据 ID 获取 Skill"""
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def create(self, skill: Skill) -> Skill:
        """创建 Skill"""
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def update(self, skill: Skill) -> Skill:
        """更新 Skill"""
        self.db.merge(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def delete(self, skill_id: str) -> bool:
        """删除 Skill"""
        skill = self.get_by_id(skill_id)
        if skill:
            self.db.delete(skill)
            self.db.commit()
            return True
        return False

    def search(
        self,
        role: Optional[str] = None,
        category: Optional[str] = None,
        signals: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Skill]:
        """搜索 Skill（支持角色、分类、信号筛选）"""
        query = self.db.query(Skill).filter(Skill.status == "active")

        if role:
            # 检查 role 是否在 applicable_roles 列表中
            query = query.filter(Skill.applicable_roles.contains([role]))

        if category:
            query = query.filter(Skill.category == category)

        if signals:
            # 检查 signals 是否有交集
            for signal in signals:
                query = query.filter(Skill.signals.contains([signal]))

        return query.limit(limit).all()

    def add_usage_log(self, log: SkillUsageLog) -> SkillUsageLog:
        """添加 Skill 使用日志"""
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def create_usage_log(self, log: SkillUsageLog) -> SkillUsageLog:
        """添加 Skill 使用日志（别名）"""
        return self.add_usage_log(log)

    def get_usage_logs(self, skill_id: str) -> List[SkillUsageLog]:
        """获取 Skill 的使用日志"""
        return self.db.query(SkillUsageLog).filter(
            SkillUsageLog.skill_id == skill_id
        ).all()

    def create_experience(self, exp: ExperienceRecord) -> ExperienceRecord:
        """创建经验记录"""
        self.db.add(exp)
        self.db.commit()
        self.db.refresh(exp)
        return exp

    def get_experiences(self, session_id: Optional[str] = None) -> List[ExperienceRecord]:
        """获取经验记录列表（可按会话筛选）"""
        query = self.db.query(ExperienceRecord)
        if session_id:
            query = query.filter(ExperienceRecord.session_id == session_id)
        return query.all()

    def get_experience_by_id(self, exp_id: str) -> Optional[ExperienceRecord]:
        """根据 ID 获取经验记录"""
        return self.db.query(ExperienceRecord).filter(
            ExperienceRecord.id == exp_id
        ).first()

    def get_experience(self, exp_id: str) -> Optional[ExperienceRecord]:
        """根据 ID 获取经验记录（别名）"""
        return self.get_experience_by_id(exp_id)

    def update_experience(self, exp: ExperienceRecord) -> ExperienceRecord:
        """更新经验记录"""
        self.db.merge(exp)
        self.db.commit()
        self.db.refresh(exp)
        return exp
