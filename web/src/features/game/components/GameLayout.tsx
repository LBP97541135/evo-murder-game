/**
 * 游戏布局组件
 *
 * 组合所有游戏子组件，根据当前阶段渲染不同界面。
 */
import React from 'react';
import { PhaseHeader } from './PhaseHeader';
import { CastPanel } from './CastPanel';
import { EvidenceBoard } from './EvidenceBoard';
import { PublicEventFeed } from './PublicEventFeed';
import { SpeakRoundPanel } from './SpeakRoundPanel';
import { PrivateChatDrawer } from './PrivateChatDrawer';
import { VotePanel } from './VotePanel';
import { RevealPanel } from './RevealPanel';
import { ScriptReader } from './ScriptReader';

interface GameLayoutProps {
  sessionId: string;
}

export const GameLayout: React.FC<GameLayoutProps> = ({ sessionId }) => {
  // 使用各种 hook 获取状态
  // 根据当前阶段渲染不同组件
  return (
    <div className="game-layout">
      <PhaseHeader />
      <div className="game-content">
        <CastPanel />
        <div className="game-main">
          <ScriptReader />
          <EvidenceBoard />
          <PublicEventFeed />
          <SpeakRoundPanel />
        </div>
      </div>
      <VotePanel />
      <RevealPanel />
      <PrivateChatDrawer />
    </div>
  );
};
