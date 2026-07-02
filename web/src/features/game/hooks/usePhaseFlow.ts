/**
 * 阶段推进 hook
 *
 * 管理游戏阶段的推进和状态查询。
 */
import { useState, useCallback } from 'react';

interface PhaseInfo {
  display_name: string;
  description: string;
  allowed_actions: string[];
}

export function usePhaseFlow(sessionId: string | null) {
  const [currentPhase, setCurrentPhase] = useState<string>('');
  const [phaseInfo, setPhaseInfo] = useState<PhaseInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 推进到下一阶段 */
  const advancePhase = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/game/phase/${sessionId}/advance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      if (data.success) {
        setCurrentPhase(data.data.phase);
        setPhaseInfo(data.data.phase_info);
      } else {
        setError(data.error?.message || '阶段推进失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /** 强制跳转到指定阶段 */
  const forcePhase = useCallback(async (phase: string) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/game/phase/${sessionId}/force`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phase }),
      });
      const data = await res.json();
      if (data.success) {
        setCurrentPhase(data.data.phase);
        setPhaseInfo(data.data.phase_info);
      } else {
        setError(data.error?.message || '阶段跳转失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /** 是否可以推进阶段 */
  const canAdvance = phaseInfo?.allowed_actions?.includes('advance') ?? false;

  return {
    currentPhase,
    canAdvance,
    advancePhase,
    forcePhase,
    phaseInfo,
    loading,
    error,
  };
}
