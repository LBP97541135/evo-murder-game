/**
 * Skill 列表页面
 *
 * 显示 Skill 列表，支持搜索、分类过滤和创建。
 */
import React, { useState, useEffect } from 'react';
import { skillsApi } from '../../api/skills';

interface Skill {
  id: string;
  name: string;
  category: string;
  status: string;
  description: string;
  createdAt: string;
}

export const SkillListPage: React.FC = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    loadSkills();
  }, [categoryFilter]);

  const loadSkills = async () => {
    setLoading(true);
    try {
      const data = await skillsApi.list({ category: categoryFilter });
      setSkills(data as any);
    } catch (error) {
      console.error('加载 Skill 列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    // 实现搜索逻辑
    console.log('搜索:', searchQuery);
  };

  const handleCreate = () => {
    // 跳转到创建页面
    console.log('创建新 Skill');
  };

  const filteredSkills = skills.filter(skill =>
    skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    skill.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="skill-list-page">
      <div className="page-header">
        <h1>Skill 管理</h1>
        <button onClick={handleCreate} className="btn-primary">
          创建 Skill
        </button>
      </div>

      <div className="filters">
        <input
          type="text"
          placeholder="搜索 Skill..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={handleSearch}
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="">全部分类</option>
          <option value="reasoning">推理</option>
          <option value="social">社交</option>
          <option value="evidence">证物</option>
        </select>
      </div>

      <div className="skill-grid">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          filteredSkills.map(skill => (
            <div key={skill.id} className="skill-card">
              <h3>{skill.name}</h3>
              <p>{skill.description}</p>
              <div className="skill-meta">
                <span className="category">{skill.category}</span>
                <span className="status">{skill.status}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
