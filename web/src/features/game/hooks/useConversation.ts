/**
 * 对话 hook
 *
 * 管理公共对话和私聊线程。
 */
import { useState, useCallback } from 'react';

interface Thread {
  id: string;
  participants: string[];
  isPrivate: boolean;
  lastMessage?: string;
  updatedAt: string;
}

interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  threadId: string;
}

export function useConversation(sessionId: string | null) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 发送消息 */
  const sendMessage = useCallback(async (content: string, threadId?: string) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/game/chat/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          thread_id: threadId,
        }),
      });
      const data = await res.json();
      if (data.success) {
        const newMessage: Message = {
          id: Date.now().toString(),
          sender: 'player',
          content,
          timestamp: new Date().toISOString(),
          threadId: threadId || 'public',
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
  }, [sessionId]);

  /** 创建私聊线程 */
  const createPrivateThread = useCallback(async (participantId: string) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/game/private-chat/${sessionId}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_key: 'player',
          to_key: participantId,
        }),
      });
      const data = await res.json();
      if (data.success) {
        const newThread: Thread = {
          id: data.data.thread_id,
          participants: ['player', participantId],
          isPrivate: true,
          updatedAt: new Date().toISOString(),
        };
        setThreads(prev => [...prev, newThread]);
      } else {
        setError(data.error?.message || '创建私聊失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return {
    threads,
    messages,
    sendMessage,
    createPrivateThread,
    loading,
    error,
  };
}
