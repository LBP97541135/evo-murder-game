/**
 * 选角 hook
 *
 * 管理角色分配和 Agent 绑定。
 */
import { useState, useCallback } from 'react';

interface CastItem {
  type: string;
  role: string;
  agentKey?: string;
}

export function useCasting(sessionId: string | null) {
  const [casts, setCasts] = useState<CastItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 提交选角结果 */
  const submitCast = useCallback(async (castList: CastItem[], playerCharacterName = '') => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/game/cast/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cast: castList,
          player_character_name: playerCharacterName,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setCasts(castList);
      } else {
        setError(data.error?.message || '选角失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /** 重置选角 */
  const resetCast = useCallback(async () => {
    setCasts([]);
    setError(null);
  }, []);

  return {
    casts,
    loading,
    error,
    submitCast,
    resetCast,
  };
}
