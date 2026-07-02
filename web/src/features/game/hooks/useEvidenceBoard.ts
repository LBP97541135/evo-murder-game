/**
 * 证物 hook
 *
 * 管理证物的发现、出示和查询。
 */
import { useState, useCallback } from 'react';

interface Evidence {
  id: string;
  name: string;
  description: string;
  category: string;
  discoveryState: string;
  isPublic: boolean;
}

export function useEvidenceBoard(sessionId: string | null, scriptId: string | null) {
  const [evidences, setEvidences] = useState<Evidence[]>([]);
  const [publicEvidences, setPublicEvidences] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 发现证物 */
  const discoverEvidence = useCallback(async (evidenceId: string) => {
    if (!sessionId || !scriptId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/evidence/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scriptId,
          sessionId,
          scriptEvidenceId: evidenceId,
          discoveredBy: 'player',
        }),
      });
      const data = await res.json();
      if (data.success) {
        setEvidences(prev => [...prev, data.data.evidence]);
      } else {
        setError(data.error?.message || '发现证物失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId, scriptId]);

  /** 出示证物 */
  const presentEvidence = useCallback(async (evidenceId: string, target: string) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/evidence/present', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evidenceId,
          presentedTo: target,
          presentedBy: 'player',
        }),
      });
      const data = await res.json();
      if (data.success) {
        // 出示成功后，将证物加入公共证物列表
        const evidence = evidences.find(e => e.id === evidenceId);
        if (evidence) {
          setPublicEvidences(prev => [...prev, { ...evidence, isPublic: true }]);
        }
      } else {
        setError(data.error?.message || '出示证物失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId, evidences]);

  return {
    evidences,
    publicEvidences,
    discoverEvidence,
    presentEvidence,
    loading,
    error,
  };
}
