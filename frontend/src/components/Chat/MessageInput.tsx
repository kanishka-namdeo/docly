import { useState, useRef, useEffect } from 'react'

interface MessageInputProps {
  onSend: (content: string) => void
  disabled?: boolean
}

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [content, setContent] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`
    }
  }, [content])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim() || disabled) return
    onSend(content.trim())
    setContent('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
      <textarea
        ref={textareaRef}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
        disabled={disabled}
        rows={1}
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
      />
      <button
        type="submit"
        disabled={disabled || !content.trim()}
        style={{
          padding: '12px 24px',
          backgroundColor: disabled || !content.trim() ? '#ccc' : '#0066cc',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: disabled || !content.trim() ? 'not-allowed' : 'pointer',
          fontWeight: 'bold',
        }}
      >
        Send
      </button>
    </form>
  )
}
