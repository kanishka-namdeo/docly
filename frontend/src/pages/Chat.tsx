import { useState, useEffect } from 'react'
import { Conversation, ProviderConfig } from '../types'
import { conversationsApi, settingsApi } from '../services/api'
import ChatWindow from '../components/Chat/ChatWindow'

function MessageSquareIcon({ size = 16, style }: { size?: number; style?: React.CSSProperties }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={style}>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  )
}

function PlusCircleIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="16" />
      <line x1="8" y1="12" x2="16" y2="12" />
    </svg>
  )
}

export default function Chat() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [providers, setProviders] = useState<ProviderConfig[]>([])
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const [convos, provs] = await Promise.all([
          conversationsApi.list(),
          settingsApi.listProviders(),
        ])
        setConversations(convos)
        setProviders(provs)
        if (provs.length > 0) {
          setSelectedProvider(provs[0].id)
        }
      } catch (err) {
        console.error('Failed to load chat data:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleNewChat = async () => {
    if (!selectedProvider) return
    try {
      const newConv = await conversationsApi.create({
        title: `New Chat ${conversations.length + 1}`,
      })
      setConversations([newConv, ...conversations])
      setSelectedConversation(newConv)
    } catch (err) {
      console.error('Failed to create conversation:', err)
    }
  }

  const handleDeleteConversation = async (id: string) => {
    try {
      await conversationsApi.delete(id)
      setConversations(conversations.filter(c => c.id !== id))
      if (selectedConversation?.id === id) {
        setSelectedConversation(null)
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err)
    }
  }

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: '250px', borderRight: '1px solid #ddd', padding: '10px', display: 'flex', flexDirection: 'column' }}>
        <button
          onClick={handleNewChat}
          disabled={!selectedProvider}
          style={{
            padding: '10px',
            marginBottom: '10px',
            backgroundColor: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: selectedProvider ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <PlusCircleIcon size={16} />
          New Chat
        </button>

        <div style={{ marginBottom: '10px' }}>
          <label style={{ fontSize: '12px', color: '#666' }}>Provider:</label>
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            style={{ width: '100%', padding: '5px', marginTop: '5px' }}
          >
            {providers.map(p => (
              <option key={p.id} value={p.id}>{p.name} ({p.model})</option>
            ))}
          </select>
        </div>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          {conversations.length === 0 ? (
            <p style={{ color: '#999', fontSize: '14px' }}>No conversations yet</p>
          ) : (
            conversations.map(conv => (
              <div
                key={conv.id}
                onClick={() => setSelectedConversation(conv)}
                style={{
                  padding: '10px',
                  marginBottom: '5px',
                  backgroundColor: selectedConversation?.id === conv.id ? '#e6f0ff' : 'transparent',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  <MessageSquareIcon size={14} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
                  {conv.title}
                </span>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDeleteConversation(conv.id) }}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#999',
                    padding: '2px',
                  }}
                >
                  ×
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedConversation ? (
          <ChatWindow
            conversation={selectedConversation}
            providerConfigId={selectedProvider}
          />
        ) : (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            <div style={{ textAlign: 'center' }}>
              <MessageSquareIcon size={48} style={{ marginBottom: '10px' }} />
              <p>Select a conversation or start a new chat</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
