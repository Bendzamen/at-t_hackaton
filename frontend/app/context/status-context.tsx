'use client';
import { useSearchParams } from 'next/navigation';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface StatusEntry {
  stage: string;
  message: string;
  index: number;
  zip?: string;
}

export type StatusBlock = string | StatusEntry[];

export interface ChatMessage {
  type: 'user' | 'status';
  stage?: string;
  message: string;
  index: number;
  timestamp: number;
  zip?: string;
}

interface StatusContextProps {
  messages: ChatMessage[];
  isLoading: boolean;
  zipData?: string;
  uploadedFileName?: string | null;
  handleDownloadZip: () => void;
}

const StatusContext = createContext<StatusContextProps | undefined>(undefined);

export const useStatus = () => {
  const context = useContext(StatusContext);
  if (!context) throw new Error('useStatus must be used within StatusProvider');
  return context;
};

export const StatusProvider = ({ children }: { children: ReactNode }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [zipData, setZipData] = useState<string | undefined>(undefined);
  const [isPolling, setIsPolling] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    const file = searchParams.get('file');
    if (file) setUploadedFileName(decodeURIComponent(file));
  }, [searchParams]);

  useEffect(() => {
    setIsPolling(true);
  }, []);

  useEffect(() => {
    if (!isPolling) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/status', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error('Failed to fetch status');

        const result: { data: StatusBlock[] } = await response.json();

        const flattened: ChatMessage[] = [];
        let latestZip: string | undefined;

        result.data.forEach((block, blockIdx) => {
          if (typeof block === 'string') {
            flattened.push({
              type: 'user',
              message: block,
              index: flattened.length,
              timestamp: Date.now() + blockIdx,
            });
          } else if (Array.isArray(block)) {
            block.forEach((entry) => {
              flattened.push({
                type: 'status',
                stage: entry.stage,
                message: entry.message,
                index: entry.index,
                timestamp: Date.now() + entry.index + blockIdx * 10,
                zip: entry.zip,
              });
              if (entry.zip) latestZip = entry.zip;
            });
          }
        });

        // Keep messages in chronological order and avoid duplicates
        setMessages((prev) => {
          const combined = [...prev, ...flattened];
          const unique = Array.from(new Map(combined.map((m) => [`${m.type}-${m.index}-${m.message}`, m])).values());
          return unique.sort((a, b) => a.timestamp - b.timestamp);
        });

        setZipData(latestZip);

        if (latestZip) {
          setIsPolling(false);
          setIsLoading(false);
        } else {
          setIsLoading(true);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        setIsPolling(false);
      }
    }, 3000);

    return () => clearInterval(pollInterval);
  }, [isPolling]);

  const handleDownloadZip = () => {
    if (!zipData) return;
    const link = document.createElement('a');
    link.href = zipData;
    link.download = 'project.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <StatusContext.Provider value={{ messages, isLoading, zipData, uploadedFileName, handleDownloadZip }}>
      {children}
    </StatusContext.Provider>
  );
};
