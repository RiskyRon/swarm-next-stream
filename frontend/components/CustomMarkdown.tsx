// frontend/components/CustomMarkdown.tsx

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CustomCodeBlock } from '@/components/CustomCodeBlock';
import { CustomWeatherCard } from '@/components/CustomWeatherCard';
import { LinkIcon } from 'lucide-react';

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
        if (inline) {
          return (
            <code className="px-1.5 py-0.5 rounded font-mono text-sm bg-muted text-muted-foreground" {...props}>
              {children}
            </code>
          );
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
        <blockquote className="border-l-4 border-muted pl-4 italic my-4">
          {children}
        </blockquote>
      ),
      a: ({ href, children }) => {
        // YouTube video handling
        const youtubeMatch = href?.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/);
        if (youtubeMatch) {
          const videoId = youtubeMatch[1];
          return (
            <div className="my-4">
              <iframe
                width="320"
                height="180"
                src={`https://www.youtube.com/embed/${videoId}`}
                title="YouTube video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="rounded-lg shadow-lg"
              ></iframe>
            </div>
          );
        }

        // Regular link handling with different styles based on type
        const isEmail = href?.startsWith('mailto:');
        const isPhone = href?.startsWith('tel:');
        const isExternal = href?.startsWith('http') || href?.startsWith('https');
        
        let linkClass = "inline-flex items-center gap-1 px-2 py-0.5 rounded transition-colors ";
        let icon = null;
        
        if (isEmail) {
          linkClass += "bg-primary/10 text-primary hover:bg-primary/20";
          icon = "📧";
        } else if (isPhone) {
          linkClass += "bg-secondary/10 text-secondary hover:bg-secondary/20";
          icon = "📞";
        } else if (isExternal) {
          linkClass += "bg-accent/10 text-accent hover:bg-accent/20";
          icon = <LinkIcon className="h-3 w-3" />;
        } else {
          linkClass += "bg-muted text-muted-foreground hover:bg-muted/80";
        }

        return (
          <a 
            href={href}
            className={linkClass}
            target={isExternal ? "_blank" : undefined}
            rel={isExternal ? "noopener noreferrer" : undefined}
          >
            {icon}
            <span className="text-sm">{children}</span>
          </a>
        );
      },
      em: ({ children }) => (
        <em className="italic text-primary">
          {children}
        </em>
      ),
      strong: ({ children }) => (
        <strong className="font-bold text-primary">
          {children}
        </strong>
      ),
    }}
  >
    {content}
  </ReactMarkdown>
);
