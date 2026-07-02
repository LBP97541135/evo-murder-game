/**
 * 发言轮 hook
 *
 * 管理发言轮次和消息发送。
 */
import { useState, useCallback } from 'react';

interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  type: 'speech' | 'action' | 'system';
}

export function useSpeechRound(sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 发送发言 */
  const sendMessage = useCallback(async (content: string) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    setIsSpeaking(true);
    try {
      const res = await fetch(`/api/game/chat/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      const data = await res.json();
      if (data.success) {
        const newMessage: Message = {
          id: Date.now().toString(),
          sender: 'player',
          content,
          timestamp: new Date().toISOString(),
          type: 'speech',
        };
        setMessages(prev => [...prev, newMessage]);
      } else {
        setError(data.error?.message || '发送失败');
      }
    } catch (e) {
      setError('网络错误');
    } finally {
      setLoading(false);
      setIsSpeaking(false);
    }
  }, [sessionId]);

  return {
    messages,
    sendMessage,
    isSpeaking,
    loading,
    error,
  };
}
