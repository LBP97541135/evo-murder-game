/**
 * 阶段头部组件
 *
 * 显示当前阶段名称、描述、进度。
 */
import React from 'react';

export const PhaseHeader: React.FC = () => {
  return (
    <div className="phase-header">
      <div className="phase-info">
        <h2 className="phase-name">当前阶段</h2>
        <p className="phase-description">阶段描述</p>
      </div>
      <div className="phase-progress">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: '0%' }}></div>
        </div>
      </div>
    </div>
  );
};
