/**
 * 选角面板组件
 *
 * 显示角色列表和分配状态。
 */
import React from 'react';

export const CastPanel: React.FC = () => {
  return (
    <div className="cast-panel">
      <h3 className="panel-title">选角面板</h3>
      <div className="cast-list">
        {/* 角色列表 */}
        <div className="cast-item">
          <span className="character-name">角色名</span>
          <span className="actor-type">Agent/玩家</span>
        </div>
      </div>
    </div>
  );
};
