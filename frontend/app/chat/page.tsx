'use client';

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Loader2, File } from 'lucide-react';
import { useSearchParams } from 'next/navigation';

interface StatusResponse {
  stage: string;
  message: string;
  zip?: string;
  preview?: string;
  index: number;
}

interface ChatMessage {
  stage: string;
  message: string;
  index: number;
  timestamp: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [zipData, setZipData] = useState<string | undefined>(undefined);
  const [isPolling, setIsPolling] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
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

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

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
          }
        } else if (data.index === currentIndex) {
          // Same index - show loading indicator
          setIsLoading(true);
        }
      } catch (error) {
        console.error('Error polling status:', error);
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
    <main className="flex h-screen bg-background">
      {/* Left Panel - Chat Messages */}
      <div className="flex-1 flex flex-col border-r border-border md:flex-1 md:w-[70%] lg:w-[70%]">
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold text-foreground">Generation Status</h1>
          <p className="text-muted-foreground text-sm">Real-time updates from the backend</p>
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
                <p className="text-xs text-muted-foreground/60 mt-2">Polling every 5 seconds</p>
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
                  <p className="text-foreground text-sm">Generating output...</p>
                </div>
              </Card>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Right Panel - Download Button */}
      <div className="hidden md:flex md:w-[30%] lg:w-[30%] flex-col items-center justify-center p-6 bg-muted/30 border-l border-border">
        {zipData ? (
          <div className="text-center space-y-4">
            <div className="p-4 bg-primary/10 rounded-lg">
              <Download className="w-8 h-8 text-primary mx-auto" />
            </div>
            <Button onClick={handleDownloadZip} size="lg" className="w-full gap-2 animate-in fade-in duration-500">
              <Download className="w-4 h-4" />
              Download ZIP
            </Button>
            <p className="text-xs text-muted-foreground">Your project is ready</p>
          </div>
        ) : (
          <div className="text-center">
            <p className="text-muted-foreground text-sm">Download will appear here</p>
          </div>
        )}
      </div>

      {/* Mobile Download Button - shown at bottom on small screens */}
      {zipData && (
        <div className="md:hidden fixed bottom-0 left-0 right-0 p-4 bg-background border-t border-border">
          <Button onClick={handleDownloadZip} size="lg" className="w-full gap-2">
            <Download className="w-4 h-4" />
            Download ZIP
          </Button>
        </div>
      )}
    </main>
  );
}
