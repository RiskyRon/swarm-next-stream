// frontend/components/ChatMessage.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Message } from '@/lib/hooks/useWebSocket';

// Custom styles for code blocks
const customCodeStyle = {
  ...vscDarkPlus,
  'pre[class*="language-"]': {
    ...vscDarkPlus['pre[class*="language-"]'],
    padding: '1rem',
    margin: '0.5rem 0',
    background: 'hsl(var(--secondary))',
    border: '1px solid hsl(var(--border))',
    borderRadius: 'calc(var(--radius) - 2px)',
  },
  ':not(pre) > code[class*="language-"]': {
    ...vscDarkPlus[':not(pre) > code[class*="language-"]'],
    background: 'hsl(var(--secondary))',
    padding: '0.2em 0.4em',
    borderRadius: 'calc(var(--radius) - 4px)',
  }
};

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = React.memo(({ message }) => (
  <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
    <div className={`rounded-lg p-3 max-w-[90%] ${
      message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'
    }`}>
      <ReactMarkdown
        className="prose prose-sm dark:prose-invert max-w-none [&_pre]:!bg-transparent [&_pre]:!p-0 [&_pre]:!m-0 [&_pre]:!border-0"
        components={{
          code({ node, inline, className, children, ...props }: {
            node?: any;
            inline?: boolean;
            className?: string;
            children: React.ReactNode;
          }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <div className="relative rounded-md overflow-hidden">
                <SyntaxHighlighter
                  style={customCodeStyle}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    background: 'hsl(var(--secondary))',
                  }}
                  className="scrollbar-custom"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code className="bg-secondary px-1.5 py-0.5 rounded-md text-sm" {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {message.content}
      </ReactMarkdown>
      <p className="text-xs mt-1 opacity-50">
        {message.timestamp.toLocaleTimeString()}
      </p>
    </div>
  </div>
));

ChatMessage.displayName = 'ChatMessage';

export default ChatMessage;