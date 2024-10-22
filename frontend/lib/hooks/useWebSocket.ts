import { useState, useEffect, useCallback, useRef } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface WebSocketHookReturn {
  messages: Message[];
  isLoading: boolean;
  isConnected: boolean;
  currentAgent: string;
  sendMessage: (content: string) => void;
  clearMessages: () => void;
}

export const useWebSocket = (url: string): WebSocketHookReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connectWebSocket = useCallback(() => {
    const socket = new WebSocket(url);
    setWs(socket);

    socket.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'content') {
        setMessages(prevMessages => {
          const lastMessage = prevMessages[prevMessages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            return [
              ...prevMessages.slice(0, -1),
              { ...lastMessage, content: lastMessage.content + data.content }
            ];
          } else {
            return [...prevMessages, {
              id: Date.now().toString(),
              role: 'assistant',
              content: data.content,
              timestamp: new Date()
            }];
          }
        });
        setIsLoading(false);
      } else if (data.type === 'agent_change') {
        setCurrentAgent(data.agent);
      } else if (data.type === 'end') {
        setIsLoading(false);
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      socket.close();
    };
  }, [url]);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connectWebSocket]);

  const sendMessage = useCallback((content: string) => {
    if (!content.trim() || !ws || !isConnected) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);

    ws.send(content);
  }, [ws, isConnected]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    isConnected,
    currentAgent,
    sendMessage,
    clearMessages
  };
};

export type { Message };