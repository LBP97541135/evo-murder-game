/**
 * 公共事件流组件
 *
 * 显示游戏中的公共消息和事件。
 */
import React from 'react';

export const PublicEventFeed: React.FC = () => {
  return (
    <div className="public-event-feed">
      <h3 className="panel-title">公共事件</h3>
      <div className="event-list">
        {/* 事件项 */}
        <div className="event-item">
          <span className="event-time">时间</span>
          <span className="event-content">事件内容</span>
        </div>
      </div>
    </div>
  );
};
