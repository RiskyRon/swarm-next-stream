'use client'

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Send, Trash2, Paperclip } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const ChatMessage: React.FC<{ message: Message }> = React.memo(({ message }) => (
  <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
    <div className={`rounded-lg p-3 max-w-[70%] ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'}`}>
      <p>{message.content}</p>
      <p className="text-xs mt-1 opacity-50">
        {message.timestamp.toLocaleTimeString()}
      </p>
    </div>
  </div>
));

ChatMessage.displayName = 'ChatMessage';

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();


  const connectWebSocket = useCallback(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');
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
            return [...prevMessages, { id: Date.now().toString(), role: 'assistant', content: data.content, timestamp: new Date() }];
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
  }, []);

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

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = useCallback(() => {
    if (!input.trim() || !ws || !isConnected) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: input, timestamp: new Date() };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);

    ws.send(input);
  }, [input, ws, isConnected]);

  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  const handleUpload = useCallback(() => {
    console.log("File upload triggered");
    // Implement file upload logic here
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const messageElements = useMemo(() => (
    messages.map(message => (
      <ChatMessage key={message.id} message={message} />
    ))
  ), [messages]);

  return (
<div className="flex flex-col h-screen w-4/5 max-w-3xl mx-auto max-h-[90vh] rounded-lg overflow-hidden">
      <Card className="flex flex-col h-full">
        <CardHeader className="flex-shrink-0">
          <div className="flex justify-between items-center">
            <CardTitle>AI Chatbot {currentAgent && `(${currentAgent})`}</CardTitle>
            <Button variant="outline" size="icon" onClick={clearChat} aria-label="Clear chat history">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-grow overflow-hidden p-0">
          <ScrollArea className="h-full p-4" ref={scrollAreaRef}>
            {messageElements}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-secondary text-secondary-foreground rounded-lg p-3 flex items-center">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Thinking...
                </div>
              </div>
            )}
          </ScrollArea>
        </CardContent>
        <CardFooter className="flex-shrink-0 border-t p-4">
          <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="w-full">
            <div className="relative w-full">
              <Textarea
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  e.target.style.height = 'auto';
                  e.target.style.height = `${e.target.scrollHeight}px`;
                }}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                className="pr-24 border resize-none rounded-md w-full overflow-hidden"
                rows={1}
                aria-label="Chat input"
                style={{ minHeight: '7.5rem', maxHeight: '30rem' }}
              />
              <div className="absolute bottom-2 right-2 flex space-x-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={handleUpload}
                  disabled={isLoading || !isConnected}
                >
                  <Paperclip className="h-4 w-4" />
                  <span className="sr-only">Attach file</span>
                </Button>
                <Button 
                  type="submit" 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8"
                  disabled={isLoading || !isConnected}
                >
                  <Send className="h-4 w-4" />
                  <span className="sr-only">Send message</span>
                </Button>
              </div>
            </div>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
};

export default ChatBot;
