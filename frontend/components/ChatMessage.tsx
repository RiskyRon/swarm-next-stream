import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Message } from '@/lib/hooks/useWebSocket';

// Separate direct styles
const customCodeStyle = {
  ...vscDarkPlus,
};

// Separate nested styles
const customWrapperStyle = {
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
    <div className={`flex items-start pt-5 gap-2 max-w-[100%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className="flex-shrink-0">
        <img
          src={message.role === 'user' ? '/images/user-avatar.png' : '/images/bot-avatar.png'}
          alt={`${message.role} avatar`}
          className="w-10 h-10 rounded-full"
        />
      </div>
      <div className={`rounded-lg p-3 ${
        message.role === 'user' 
          ? 'bg-secondary text-secondary-foreground border' 
          : 'bg-secondary text-secondary-foreground'
      }`}>
        <ReactMarkdown
          className="prose prose-sm dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0"
          components={{
            code({ inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <div className="relative rounded-md overflow-hidden my-4">
                  <SyntaxHighlighter
                    style={customCodeStyle}
                    language={match[1]}
                    PreTag="div"
                    wrapperStyle={customWrapperStyle}
                    customStyle={{
                      margin: 0,
                      background: 'hsl(var(--secondary))',
                    }}
                    className="scrollbar-custom p-4"
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
            p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
            ul: ({ children }) => <ul className="list-disc pl-6 mb-4 last:mb-0">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 last:mb-0">{children}</ol>,
            li: ({ children }) => <li className="mb-2 last:mb-0">{children}</li>,
            h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 mt-6">{children}</h1>,
            h2: ({ children }) => <h2 className="text-xl font-bold mb-3 mt-5">{children}</h2>,
            h3: ({ children }) => <h3 className="text-lg font-bold mb-2 mt-4">{children}</h3>,
            blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4">{children}</blockquote>,
          }}
        >
          {message.content}
        </ReactMarkdown>
        <p className="text-xs mt-2 opacity-50">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  </div>
));

ChatMessage.displayName = 'ChatMessage';

export default ChatMessage;
