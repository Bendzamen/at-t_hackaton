// context/StatusContext.tsx
'use client';

import { useSearchParams } from 'next/navigation';
import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';

export interface StatusResponse {
  stage: string;
  message: string;
  zip?: string;
  preview?: string;
  index: number;
}

export interface ChatMessage {
  stage: string;
  message: string;
  index: number;
  timestamp: number;
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
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      stage: 'Starting',
      message: 'Calling project owner agent',
      index: 0,
      timestamp: Date.now(),
    },
  ]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [zipData, setZipData] = useState<string | undefined>(undefined);
  const [isPolling, setIsPolling] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    const file = searchParams.get('file');
    if (file) {
      setUploadedFileName(decodeURIComponent(file));
    }
  }, [searchParams]);

  useEffect(() => {
    const initializeProject = async () => {
      try {
        console.log(' Calling /start API');
        const response = await fetch('/api/start', {
          method: 'POST',
        });

        if (!response.ok) {
          throw new Error('Failed to start project');
        }

        const data = await response.json();
        console.log(' Project started with ID:', data.projectId);
        setProjectId(data.projectId);
        setIsPolling(true);
      } catch (error) {
        console.error('Error initializing project:', error);
      }
    };

    initializeProject();
  }, []);

  useEffect(() => {
    if (!isPolling || !projectId) return;

    const pollInterval = setInterval(async () => {
      try {
        console.log(' Polling status for projectId:', projectId);
        const response = await fetch('/api/status', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ projectId }),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch status');
        }

        const data = await response.json();
        console.log(' Status response:', data);

        if (data.index > currentIndex) {
          // New message received
          setCurrentIndex(data.index);
          setMessages((prev) => [
            ...prev,
            {
              stage: data.stage,
              message: data.message,
              index: data.index,
              timestamp: Date.now(),
            },
          ]);
          setIsLoading(false);

          if (data.zip) {
            setZipData(data.zip);
            setIsPolling(false);
          }
        } else if (data.index === currentIndex) {
          // Same index - show loading indicator
          setIsLoading(true);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        setMessages((prev) => [
          ...prev,
          {
            stage: 'Error',
            message: 'Something went wrong',
            index: 0,
            timestamp: Date.now(),
          },
        ]);
        setIsPolling(false);
      }
    }, 5000);

    return () => clearInterval(pollInterval);
  }, [currentIndex, isPolling, projectId]);

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
