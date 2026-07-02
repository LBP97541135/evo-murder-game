/**
 * 私聊 hook
 *
 * 管理私聊线程和消息。
 */
import { useState, useCallback } from 'react';

interface PrivateThread {
  id: string;
  participantId: string;
  participantName: string;
  lastMessage?: string;
  updatedAt: string;
}

interface PrivateMessage {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
}

export function usePrivateChat(sessionId: string | null) {
  const [privateThreads, setPrivateThreads] = useState<PrivateThread[]>([]);
  const [currentThread, setCurrentThread] = useState<PrivateThread | null>(null);
  const [messages, setMessages] = useState<PrivateMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 选择私聊线程 */
  const selectThread = useCallback((threadId: string) => {
    const thread = privateThreads.find(t => t.id === threadId);
    setCurrentThread(thread || null);
    // 加载该线程的消息历史
    setMessages([]); // 实际应从 API 加载
  }, [privateThreads]);

  /** 发送私聊消息 */
  const sendPrivateMessage = useCallback(async (content: string) => {
    if (!sessionId || !currentThread) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/game/private-chat/${sessionId}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_key: 'player',
          to_key: currentThread.participantId,
          content,
        }),
      });
      const data = await res.json();
      if (data.success) {
        const newMessage: PrivateMessage = {
          id: Date.now().toString(),
          sender: 'player',
          content,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, newMessage]);
      } else {
        setError(data.error?.message || '发送失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId, currentThread]);

  return {
    privateThreads,
    currentThread,
    messages,
    selectThread,
    sendPrivateMessage,
    loading,
    error,
  };
}
