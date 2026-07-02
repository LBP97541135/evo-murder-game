/**
 * Skill 详情页面
 *
 * 显示 Skill 的详细内容、使用统计和审核状态。
 */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { skillsApi } from '../../api/skills';

interface SkillDetail {
  id: string;
  name: string;
  category: string;
  status: string;
  description: string;
  content: string;
  signals: string[];
  usageCount: number;
  effectiveness: number;
  createdAt: string;
  updatedAt: string;
}

export const SkillDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [skill, setSkill] = useState<SkillDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      loadSkillDetail();
    }
  }, [id]);

  const loadSkillDetail = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await skillsApi.get(id);
      setSkill(data as any);
    } catch (error) {
      console.error('加载 Skill 详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  if (!skill) {
    return <div className="not-found">Skill 不存在</div>;
  }

  return (
    <div className="skill-detail-page">
      <div className="detail-header">
        <h1>{skill.name}</h1>
        <span className={`status-badge ${skill.status}`}>
          {skill.status}
        </span>
      </div>

      <div className="detail-content">
        <section className="info-section">
          <h2>基本信息</h2>
          <div className="info-grid">
            <div>
              <label>分类:</label>
              <span>{skill.category}</span>
            </div>
            <div>
              <label>使用次数:</label>
              <span>{skill.usageCount}</span>
            </div>
            <div>
              <label>有效性:</label>
              <span>{(skill.effectiveness * 100).toFixed(1)}%</span>
            </div>
          </div>
        </section>

        <section className="content-section">
          <h2>Skill 内容</h2>
          <div className="content-body">
            {skill.content}
          </div>
        </section>

        <section className="signals-section">
          <h2>触发信号</h2>
          <div className="signal-tags">
            {skill.signals.map((signal, index) => (
              <span key={index} className="signal-tag">
                {signal}
              </span>
            ))}
          </div>
        </section>

        <section className="stats-section">
          <h2>使用统计</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{skill.usageCount}</span>
              <span className="stat-label">总使用次数</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">
                {(skill.effectiveness * 100).toFixed(1)}%
              </span>
              <span className="stat-label">有效性</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
