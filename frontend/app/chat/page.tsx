import { StatusProvider } from '../context/status-context';
import { ChatPanel } from './_components/chat-messages';
import { DownloadPanel } from './_components/preview-pannel';

export default function ChatPage() {
  return (
    <StatusProvider>
      <main className="flex h-screen bg-background">
        <ChatPanel />
        <DownloadPanel />
      </main>
    </StatusProvider>
  );
}
