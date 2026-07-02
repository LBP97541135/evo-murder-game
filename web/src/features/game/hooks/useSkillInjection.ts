/**
 * Skill 注入 hook
 *
 * 管理 Skill 的加载和注入。
 */
import { useState, useCallback } from 'react';

interface Skill {
  id: string;
  name: string;
  category: string;
  content: string;
  signals: string[];
}

export function useSkillInjection(sessionId: string | null) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loadedSkills, setLoadedSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 注入 Skills */
  const injectSkills = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/skills/inject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          skill_ids: skills.map(s => s.id),
        }),
      });
      const data = await res.json();
      if (data.success) {
        setLoadedSkills(skills);
      } else {
        setError(data.error?.message || '注入失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId, skills]);

  return {
    skills,
    loadedSkills,
    injectSkills,
    loading,
    error,
  };
}
