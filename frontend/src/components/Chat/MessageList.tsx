import { useEffect, useRef } from 'react'
import { Message } from '../../types'
import CitationCard from './CitationCard'

interface MessageListProps {
  messages: Message[]
}

export default function MessageList({ messages }: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div ref={containerRef} style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '15px' }}>
      {messages.map(msg => {
        const isUser = msg.role === 'user'
        const citations = msg.citations || []

        return (
          <div
            key={msg.id}
            style={{
              alignSelf: isUser ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: isUser ? '#0066cc' : '#f0f0f0',
              color: isUser ? 'white' : '#333',
            }}
          >
            <div style={{ marginBottom: '8px', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {msg.content}
            </div>

            {!isUser && citations.length > 0 && (
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
        )
      })}
      {messages.length === 0 && (
        <div style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
          No messages yet. Start the conversation!
        </div>
      )}
    </div>
  )
}
