/**
 * 私聊抽屉组件
 *
 * 管理私聊线程和消息。
 */
import React from 'react';

export const PrivateChatDrawer: React.FC = () => {
  return (
    <div className="private-chat-drawer">
      <h3 className="panel-title">私聊</h3>
      <div className="thread-list">
        {/* 私聊线程列表 */}
        <div className="thread-item">
          <span className="participant">对话者</span>
          <span className="last-message">最后消息</span>
        </div>
      </div>
      <div className="chat-area">
        <div className="message-list">
          {/* 私聊消息 */}
        </div>
        <div className="message-input">
          <input type="text" placeholder="输入私聊消息..." />
          <button>发送</button>
        </div>
      </div>
    </div>
  );
};
