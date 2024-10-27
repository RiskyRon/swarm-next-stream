// frontend/components/CustomMarkdown.tsx

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CustomCodeBlock } from '@/components/CustomCodeBlock';
import { CustomWeatherCard } from '@/components/CustomWeatherCard';

interface CustomMarkdownProps {
  content: string;
}

export const CustomMarkdown: React.FC<CustomMarkdownProps> = ({ content }) => (
  <ReactMarkdown
    className="prose prose-sm dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0"
    components={{
      code({ node, inline, className, children, ...props }: any) {
        const match = /language-(\w+)/.exec(className || '');
        if (match && match[1] === 'weather') {
          try {
            const data = JSON.parse(String(children).replace(/\n$/, ''));
            return <CustomWeatherCard data={data} />;
          } catch (error) {
            console.error('Error parsing weather data:', error);
            return <div>Error displaying weather data</div>;
          }
        }
        return (
          <CustomCodeBlock
            inline={inline}
            className={className}
            {...props}
          >
            {children}
          </CustomCodeBlock>
        );
      },
      p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
      ul: ({ children }) => <ul className="list-disc pl-6 mb-4 last:mb-0">{children}</ul>,
      ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 last:mb-0">{children}</ol>,
      li: ({ children }) => <li className="mb-2 last:mb-0">{children}</li>,
      h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 mt-6">{children}</h1>,
      h2: ({ children }) => <h2 className="text-xl font-bold mb-3 mt-5">{children}</h2>,
      h3: ({ children }) => <h3 className="text-lg font-bold mb-2 mt-4">{children}</h3>,
      blockquote: ({ children }) => (
        <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4">
          {children}
        </blockquote>
      ),
      a: ({ href, children }) => {
        const youtubeMatch = href?.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/);
        if (youtubeMatch) {
          const videoId = youtubeMatch[1];
          return (
            <iframe
              width="320"
              height="180"
              src={`https://www.youtube.com/embed/${videoId}`}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              style={{ borderRadius: '8px' }}
            ></iframe>
          );
        }
        return <a href={href}>{children}</a>;
      },
    }}
  >
    {content}
  </ReactMarkdown>
);
