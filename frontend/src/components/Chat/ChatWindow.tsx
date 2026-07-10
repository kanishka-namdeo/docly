import { useState, useEffect } from 'react'
import { Conversation, Message, ChatRequest } from '../../types'
import { conversationsApi, chatApi } from '../../services/api'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

interface ChatWindowProps {
  conversation: Conversation
  providerConfigId: string
}

export default function ChatWindow({ conversation, providerConfigId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    setLoading(true)
    conversationsApi.getMessages(conversation.id)
      .then(setMessages)
      .catch(err => console.error('Failed to load messages:', err))
      .finally(() => setLoading(false))
  }, [conversation.id])

  const handleSend = async (content: string) => {
    if (!providerConfigId) return

    const tempId = `temp-${Date.now()}`
    const userMessage: Message = {
      id: tempId,
      conversation_id: conversation.id,
      role: 'user',
      content,
      citations: null,
      created_at: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setSending(true)

    try {
      const payload: ChatRequest = {
        message: content,
        conversation_id: conversation.id,
        provider_config_id: providerConfigId,
      }

      const response = await chatApi.send(payload)

      const assistantMessage: Message = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.content,
        citations: response.citations,
        created_at: new Date().toISOString(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Failed to send message:', err)
      setMessages(prev => prev.filter(m => m.id !== tempId))
    } finally {
      setSending(false)
    }
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '15px 20px', borderBottom: '1px solid #ddd' }}>
        <h2 style={{ margin: 0, fontSize: '18px' }}>{conversation.title}</h2>
      </div>

      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {loading ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            Loading messages...
          </div>
        ) : (
          <>
            <div style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
              <MessageList messages={messages} />
            </div>
            <div style={{ padding: '15px 20px', borderTop: '1px solid #ddd' }}>
              <MessageInput onSend={handleSend} disabled={sending || !providerConfigId} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
