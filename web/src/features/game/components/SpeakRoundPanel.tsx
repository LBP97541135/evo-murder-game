/**
 * 发言轮面板组件
 *
 * 管理发言轮次和消息输入。
 */
import React from 'react';

export const SpeakRoundPanel: React.FC = () => {
  return (
    <div className="speak-round-panel">
      <h3 className="panel-title">发言轮</h3>
      <div className="message-list">
        {/* 消息列表 */}
        <div className="message-item">
          <span className="sender">发言者</span>
          <span className="content">发言内容</span>
        </div>
      </div>
      <div className="message-input">
        <input type="text" placeholder="输入发言内容..." />
        <button>发送</button>
      </div>
    </div>
  );
};
