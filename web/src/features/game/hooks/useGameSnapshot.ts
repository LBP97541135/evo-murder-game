/**
 * 游戏快照 hook - 从服务端 snapshot 恢复游戏状态
 * 服务端是游戏主状态唯一来源
 */
import { useState, useEffect, useCallback } from 'react';

interface GameSnapshot {
  session: {
    id: string;
    script_id: string;
    current_phase: string;
    status: string;
    title: string;
  };
  casts: Array<{
    id: string;
    character_id: string;
    actor_type: string;
    actor_id: string;
    role_name: string;
    is_player: boolean;
  }>;
  phase_history: Array<{
    from_phase: string;
    to_phase: string;
    reason: string;
    created_at: string;
  }>;
}

export function useGameSnapshot(sessionId: string | null) {
  const [snapshot, setSnapshot] = useState<GameSnapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/sessions/${sessionId}/snapshot`);
      const data = await res.json();
      if (data.success) {
        setSnapshot(data.data);
      } else {
        setError(data.error?.message || '加载失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { snapshot, loading, error, refresh };
}
