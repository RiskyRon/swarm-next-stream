import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const customCodeStyle = {
  ...vscDarkPlus,
};


export const CustomCodeBlock = ({ inline, className, children, ...props }: any) => {
  const match = /language-(\w+)/.exec(className || '');
  return !inline && match ? (
    <div className="relative my-4">
      <SyntaxHighlighter
        style={customCodeStyle}
        language={match[1]}
        PreTag="div"
        customStyle={{
          margin: 0,
          background: 'hsl(var(--secondary))',
          overflowX: 'auto', // Allow horizontal scrolling
          padding: '1rem',
          border: '1px solid hsl(var(--border))',
          borderRadius: 'calc(var(--radius) - 2px)',
          whiteSpace: 'pre', // Prevent text wrapping
          wordWrap: 'normal',
        }}
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
};