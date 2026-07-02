/**
 * Skill 搜索组件
 *
 * 提供 Skill 搜索功能。
 */
import React, { useState } from 'react';

interface SkillSearchBarProps {
  onSearch: (query: string, category: string) => void;
}

export const SkillSearchBar: React.FC<SkillSearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');

  const handleSearch = () => {
    onSearch(query, category);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="skill-search-bar">
      <input
        type="text"
        placeholder="搜索 Skill..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        className="search-input"
      />
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="category-select"
      >
        <option value="">全部分类</option>
        <option value="reasoning">推理</option>
        <option value="social">社交</option>
        <option value="evidence">证物</option>
      </select>
      <button onClick={handleSearch} className="search-button">
        搜索
      </button>
    </div>
  );
};
