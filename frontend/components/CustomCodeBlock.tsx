import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const customCodeStyle = {
  ...vscDarkPlus,
};

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

export const CustomCodeBlock = ({ inline, className, children, ...props }: any) => {
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
};
