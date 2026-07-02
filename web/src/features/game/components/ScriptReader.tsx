/**
 * 剧本阅读组件
 *
 * 显示玩家的角色剧本内容。
 */
import React from 'react';

export const ScriptReader: React.FC = () => {
  return (
    <div className="script-reader">
      <h3 className="panel-title">我的剧本</h3>
      <div className="script-content">
        <p>剧本内容将在这里显示...</p>
      </div>
    </div>
  );
};
