import { ThreadPrimitive, ComposerPrimitive, MessagePrimitive, useMessage } from '@assistant-ui/react';
import { MarkdownTextPrimitive } from '@assistant-ui/react-markdown';
import type { Citation } from '../../types';
import { useState } from 'react';

function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        border: '1px solid #ddd',
        borderRadius: '6px',
        padding: '8px',
        maxWidth: '200px',
        backgroundColor: expanded ? '#fff' : '#fafafa',
        cursor: 'pointer',
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ fontSize: '11px', color: '#666', marginBottom: '4px' }}>
        [{index}] {citation.file_path.split('/').pop()}
      </div>
      {expanded && (
        <div style={{ fontSize: '12px', color: '#333', marginTop: '4px' }}>
          <div style={{ marginBottom: '4px', fontStyle: 'italic', color: '#888' }}>
            Score: {(citation.score * 100).toFixed(1)}%
          </div>
          <div style={{ maxHeight: '100px', overflow: 'auto', lineHeight: '1.4' }}>
            {citation.text}
          </div>
        </div>
      )}
      {!expanded && (
        <div style={{ fontSize: '10px', color: '#999' }}>
          Click to expand
        </div>
      )}
    </div>
  );
}

function AssistantMessageContent() {
  const message = useMessage()
  if (!message) return null
  
  const metadata = message.metadata as { custom?: { citations?: Citation[] } } | undefined
  const citations = metadata?.custom?.citations || []

  return (
    <div>
      <MessagePrimitive.Content
        components={{
          Text: () => <MarkdownTextPrimitive />,
        }}
      />
      {citations.length > 0 && (
        <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
          <div style={{ fontSize: '12px', marginBottom: '5px', fontWeight: 'bold' }}>
            Citations ({citations.length})
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {citations.map((citation, idx) => (
              <CitationCard key={idx} citation={citation} index={idx + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AssistantChatView() {
  return (
    <ThreadPrimitive.Root style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <ThreadPrimitive.Viewport style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
        <ThreadPrimitive.Empty>
          <div style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
            No messages yet. Start the conversation!
          </div>
        </ThreadPrimitive.Empty>
        <ThreadPrimitive.Messages
          components={{
            UserMessage: () => (
              <MessagePrimitive.Root>
                <div style={{ alignSelf: 'flex-end', maxWidth: '80%', padding: '12px 16px', borderRadius: '12px', backgroundColor: '#0066cc', color: 'white' }}>
                  <MessagePrimitive.Content />
                </div>
              </MessagePrimitive.Root>
            ),
            AssistantMessage: () => (
              <MessagePrimitive.Root>
                <div style={{ alignSelf: 'flex-start', maxWidth: '80%', padding: '12px 16px', borderRadius: '12px', backgroundColor: '#f0f0f0', color: '#333' }}>
                  <AssistantMessageContent />
                </div>
              </MessagePrimitive.Root>
            ),
          }}
        />
      </ThreadPrimitive.Viewport>
      <div style={{ padding: '15px 20px', borderTop: '1px solid #ddd' }}>
        <ComposerPrimitive.Root style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
          <ComposerPrimitive.Input
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              resize: 'none',
              fontSize: '14px',
              fontFamily: 'inherit',
              outline: 'none',
            }}
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          />
          <ComposerPrimitive.Send
            style={{
              padding: '12px 24px',
              backgroundColor: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
            }}
          >
            Send
          </ComposerPrimitive.Send>
        </ComposerPrimitive.Root>
      </div>
    </ThreadPrimitive.Root>
  );
}
