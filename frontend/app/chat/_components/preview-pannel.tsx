'use client';
import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';
import { useStatus } from '@/app/context/status-context';

export const DownloadPanel = () => {
  const { zipData, handleDownloadZip } = useStatus();

  return (
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
        <p className="text-muted-foreground text-sm text-center">Download will appear here</p>
      )}
    </div>
  );
};
