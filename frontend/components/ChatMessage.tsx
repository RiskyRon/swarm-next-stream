import React from 'react';
import type { Message } from '@/lib/hooks/useWebSocket';
import { CustomMarkdown } from '@/components/CustomMarkdown';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = React.memo(({ message }) => (
  <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
    <div className={`flex items-start pt-5 gap-2 max-w-full ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className="flex-shrink-0">
        <img
          src={message.role === 'user' ? '/images/user-avatar.png' : '/images/bot-avatar.png'}
          alt={`${message.role} avatar`}
          className="w-10 h-10 rounded-full"
        />
      </div>
      <div className={`rounded-lg p-3 overflow-hidden ${
        message.role === 'user' 
          ? 'bg-secondary text-secondary-foreground border' 
          : 'bg-secondary text-secondary-foreground'
      }`}>
        <div className="max-w-full overflow-x-auto">
          <CustomMarkdown content={message.content} />
        </div>
        <p className="text-xs mt-2 opacity-50">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  </div>
));

ChatMessage.displayName = 'ChatMessage';

export default ChatMessage;
