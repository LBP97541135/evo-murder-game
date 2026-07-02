/**
 * 投票面板组件
 *
 * 管理投票环节。
 */
import React from 'react';

export const VotePanel: React.FC = () => {
  return (
    <div className="vote-panel">
      <h3 className="panel-title">投票</h3>
      <div className="vote-options">
        {/* 投票选项 */}
        <div className="vote-option">
          <input type="radio" name="vote" id="option1" />
          <label htmlFor="option1">嫌疑人1</label>
        </div>
      </div>
      <div className="vote-reason">
        <textarea placeholder="说明你的投票理由..."></textarea>
      </div>
      <button className="submit-vote">提交投票</button>
    </div>
  );
};
