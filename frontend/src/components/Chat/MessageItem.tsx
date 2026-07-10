import CitationCard from './CitationCard'
import type { Message } from '../../types'

interface MessageItemProps {
  message: Message
}

export default function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user'
  const citations = message.citations || []

  return (
    <div style={{
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      gap: '12px',
      maxWidth: '80%'
    }}>
      <div style={{
        width: '36px',
        height: '36px',
        borderRadius: '50%',
        backgroundColor: isUser ? '#0066cc' : '#28a745',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '14px',
        flexShrink: 0
      }}>
        {isUser ? 'U' : 'AI'}
      </div>
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{
          padding: '12px 16px',
          borderRadius: '12px',
          backgroundColor: isUser ? '#0066cc' : '#f0f0f0',
          color: isUser ? 'white' : '#333',
          lineHeight: '1.5',
          whiteSpace: 'pre-wrap'
        }}>
          {message.content}
        </div>
        {citations.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {citations.map((citation, index) => (
              <CitationCard key={index} citation={citation} index={index + 1} />
            ))}
          </div>
        )}
        <div style={{ fontSize: '12px', color: '#999', textAlign: isUser ? 'right' : 'left' }}>
          {new Date(message.created_at || Date.now()).toLocaleString()}
        </div>
      </div>
    </div>
  )
}
