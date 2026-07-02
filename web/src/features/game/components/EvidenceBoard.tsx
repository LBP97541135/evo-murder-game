/**
 * 证物面板组件
 *
 * 显示已发现的证物和公共证物。
 */
import React from 'react';

export const EvidenceBoard: React.FC = () => {
  return (
    <div className="evidence-board">
      <h3 className="panel-title">证物面板</h3>
      <div className="evidence-grid">
        {/* 证物卡片 */}
        <div className="evidence-card">
          <div className="evidence-name">证物名称</div>
          <div className="evidence-desc">证物描述</div>
        </div>
      </div>
    </div>
  );
};
