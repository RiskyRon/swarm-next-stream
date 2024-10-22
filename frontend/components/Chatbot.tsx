// frontend/components/Chatbot.tsx
'use client'

import React, { useRef, useCallback, useMemo, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Send, Trash2, Paperclip } from 'lucide-react';
import ChatMessage from '@/components/ChatMessage';
import { useWebSocket } from '@/lib/hooks/useWebSocket';

const ChatBot: React.FC = () => {
  const [input, setInput] = useState('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messageEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    isConnected,
    currentAgent,
    sendMessage,
    clearMessages
  } = useWebSocket('ws://localhost:8000/ws');

  const scrollToBottom = useCallback(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const handleSubmit = useCallback(() => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput('');
  }, [input, sendMessage]);

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
    <div className="flex flex-col h-screen w-4/5 max-w-[55rem] mx-auto max-h-[90vh] rounded-lg overflow-hidden">
      <Card className="flex flex-col h-full">
        <CardHeader className="flex-shrink-0">
          <div className="flex justify-between items-center">
            <CardTitle>AI Chatbot {currentAgent && `(${currentAgent})`}</CardTitle>
            <Button variant="outline" size="icon" onClick={clearMessages} aria-label="Clear chat history">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-grow overflow-hidden p-0">
          <ScrollArea 
            className="h-full p-4 [&_.scrollbar-thumb]:bg-muted-foreground/50 [&_.scrollbar-thumb]:hover:bg-muted-foreground/80" 
            ref={scrollAreaRef}
          >
            {messageElements}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-secondary text-secondary-foreground rounded-lg p-3 flex items-center">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                </div>
              </div>
            )}
            <div ref={messageEndRef} />
          </ScrollArea>
        </CardContent>
        <CardFooter className="flex-shrink-0 p-2">
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
