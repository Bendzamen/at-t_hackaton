'use client';
import { useStatus } from '@/app/context/status-context';
import { Card } from '@/components/ui/card';
import { Loader2, File } from 'lucide-react';
import Image from 'next/image';
import { useEffect, useRef } from 'react';

export const ChatPanel = () => {
  const { messages, isLoading, uploadedFileName } = useStatus();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages or loading changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 flex flex-col border-r border-border h-full">
      {/* Header */}
      <div className="p-6 border-b border-border bg-background sticky top-16 z-10 shrink-0">
        <h1 className="text-2xl font-bold text-foreground flex gap-1 items-center">
          <Image src="/logo.png" alt="S Logo" width={32} height={32} />
          <span className="font-bold text-lg text-foreground">lopify</span>
          Chat
        </h1>
        {uploadedFileName && (
          <div className="mt-3 p-2 bg-primary/10 rounded flex items-center gap-2 text-sm">
            <File className="w-4 h-4 text-primary" />
            <span className="text-foreground truncate">{uploadedFileName}</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={`${msg.type}-${msg.index}-${msg.timestamp}`}
            className={`flex ${
              msg.type === 'user' ? 'justify-start slide-in-from-left-4' : 'justify-end slide-in-from-right-4'
            } animate-in fade-in duration-300`}
          >
            <Card
              className={`p-4 max-w-xs ${
                msg.type === 'user'
                  ? 'bg-blue-100 border-blue-300 text-foreground text-sm'
                  : 'bg-muted/50 border-border'
              }`}
            >
              {msg.type === 'status' && <p className="text-xs font-semibold text-primary">{msg.stage}</p>}
              <p className="text-sm">{msg.message}</p>
            </Card>
          </div>
        ))}

        {/* Loading indicator for status messages */}
        {isLoading && (
          <div className="flex justify-end animate-in fade-in duration-300">
            <Card className="bg-muted/50 border-border p-4 max-w-xs">
              <div className="flex items-center gap-3">
                <Loader2 className="w-4 h-4 text-primary animate-spin" />
                <p className="text-foreground text-sm">Thinking...</p>
              </div>
            </Card>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
