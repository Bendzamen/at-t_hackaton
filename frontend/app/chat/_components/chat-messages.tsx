'use client';
import { useStatus } from '@/app/context/status-context';
import { Card } from '@/components/ui/card';
import { Loader2, File } from 'lucide-react';
import Image from 'next/image';

import { useEffect, useRef } from 'react';

export const ChatPanel = () => {
  const { messages, isLoading, uploadedFileName } = useStatus();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 flex flex-col border-r border-border">
      <div className="p-6 border-b border-border bg-background ">
        <h1 className="text-2xl font-bold text-foreground flex gap-1">
          <span className="flex items-center">
            <Image src="/logo.png" alt="S Logo" width={32} height={32} />
            <span className="font-bold text-lg text-foreground">lopify</span>
          </span>
          Chat
        </h1>
        {uploadedFileName && (
          <div className="mt-3 p-2 bg-primary/10 rounded flex items-center gap-2 text-sm">
            <File className="w-4 h-4 text-primary" />
            <span className="text-foreground truncate">{uploadedFileName}</span>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <p className="text-muted-foreground">
                {uploadedFileName ? 'Processing your file...' : 'Waiting for updates...'}
              </p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.timestamp} className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <Card className="bg-muted/50 border-border p-4">
              <div className="flex items-start gap-3">
                <div className="flex-1">
                  <p className="text-xs font-semibold text-primary mb-1">{msg.stage}</p>
                  <p className="text-foreground text-sm">{msg.message}</p>
                </div>
              </div>
            </Card>
          </div>
        ))}

        {isLoading && (
          <div className="animate-in fade-in duration-300">
            <Card className="bg-muted/50 border-border p-4">
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
