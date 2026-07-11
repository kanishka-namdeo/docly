import { ThreadPrimitive, ComposerPrimitive, MessagePrimitive, useMessage, useThread } from '@assistant-ui/react';
import { MarkdownTextPrimitive } from '@assistant-ui/react-markdown';
import type { Citation } from '../../types';
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [expanded, setExpanded] = useState(false);

  const handleClick = async () => {
    // Toggle expanded state
    setExpanded(!expanded);
    
    // Also try to open file if clicking on the filename
    if (citation.file_path && !expanded) {
      try {
        await invoke('open_file', { path: citation.file_path });
      } catch (error) {
        console.error('Failed to open file:', error);
      }
    }
  };

  return (
    <Card className="cursor-pointer hover:bg-muted/50 transition-colors" onClick={handleClick} title="Click to expand/collapse">
      <CardContent className="p-3">
        <div className="text-xs text-muted-foreground mb-1">
          [{index}] {citation.file_path.split('/').pop()}
        </div>
        {expanded && (
          <div className="text-sm text-foreground mt-1">
            <div className="mb-1 italic text-muted-foreground">
              Score: {(citation.score * 100).toFixed(1)}%
            </div>
            <div className="max-h-[100px] overflow-auto leading-relaxed">
              {citation.text}
            </div>
          </div>
        )}
        {!expanded && (
          <div className="text-[10px] text-muted-foreground">
            Click to expand
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function AssistantMessageContent() {
  const message = useMessage()
  if (!message) return null
  
  const metadata = message.metadata as { 
    custom?: { 
      citations?: Citation[];
      reasoning?: string;
      iterations?: number;
    } 
  } | undefined
  const citations = metadata?.custom?.citations || []
  const reasoning = metadata?.custom?.reasoning
  const iterations = metadata?.custom?.iterations

  return (
    <div>
      {reasoning && (
        <details className="mb-2.5 p-2 bg-muted/30 rounded-md">
          <summary className="cursor-pointer text-xs text-muted-foreground select-none">
            🧠 Reasoning {iterations && `(${iterations} iteration${iterations > 1 ? 's' : ''})`}
          </summary>
          <div className="mt-2 text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
            {reasoning}
          </div>
        </details>
      )}
      <MessagePrimitive.Content
        components={{
          Text: () => <MarkdownTextPrimitive />,
        }}
      />
      {citations.length > 0 && (
        <div className="mt-2.5 pt-2.5 border-t border-border">
          <div className="text-xs mb-1.5 font-semibold">
            Citations ({citations.length})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {citations.map((citation, idx) => (
              <CitationCard key={idx} citation={citation} index={idx + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TypingIndicator() {
  const thread = useThread();
  const isGenerating = thread.isRunning;
  if (!isGenerating) return null;
  return (
    <div className="flex items-center gap-2 px-4 py-2 text-muted-foreground text-sm">
      <span className="opacity-60">⋯</span>
      Generating response…
    </div>
  );
}


export default function AssistantChatView() {
  return (
    <ThreadPrimitive.Root className="flex flex-col h-full min-h-0">
      <ThreadPrimitive.Viewport className="flex-1 min-h-0 overflow-auto p-5">
        <ThreadPrimitive.Empty>
          <div className="text-center text-muted-foreground py-10">
            No messages yet. Start the conversation!
          </div>
        </ThreadPrimitive.Empty>
        <ThreadPrimitive.Messages
          components={{
            UserMessage: () => (
              <MessagePrimitive.Root className="flex justify-end mb-3">
                <div className="max-w-[80%] px-4 py-3 rounded-xl bg-accent text-accent-foreground">
                  <MessagePrimitive.Content />
                </div>
              </MessagePrimitive.Root>
            ),
            AssistantMessage: () => (
              <MessagePrimitive.Root className="flex justify-start mb-3">
                <div className="max-w-[80%] px-4 py-3 rounded-xl bg-muted text-foreground">
                  <AssistantMessageContent />
                </div>
              </MessagePrimitive.Root>
            ),
          }}
        />
        <TypingIndicator />
      </ThreadPrimitive.Viewport>
      <div className="px-4 py-3 border-t border-border flex-shrink-0">
        <ComposerPrimitive.Root className="flex gap-2.5 items-end">
          <ComposerPrimitive.Input
            className={cn(
              "flex-1 px-3 py-3 border border-input rounded-md",
              "resize-none text-sm font-sans outline-none",
              "focus:ring-2 focus:ring-ring focus:border-transparent",
              "placeholder:text-muted-foreground"
            )}
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          />
          <ComposerPrimitive.Send asChild>
            <Button className="px-6 py-3 font-semibold">
              Send
            </Button>
          </ComposerPrimitive.Send>
        </ComposerPrimitive.Root>
      </div>
    </ThreadPrimitive.Root>
  );
}
