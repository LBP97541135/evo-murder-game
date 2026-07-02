/**
 * 真相揭示面板组件
 *
 * 游戏结束时揭示真相。
 */
import React from 'react';

export const RevealPanel: React.FC = () => {
  return (
    <div className="reveal-panel">
      <h3 className="panel-title">真相揭示</h3>
      <div className="reveal-content">
        <p>真相内容将在这里显示...</p>
      </div>
    </div>
  );
};
