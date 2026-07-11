import { useState, useEffect } from 'react'
import { AssistantRuntimeProvider } from '@assistant-ui/react'
import { Conversation, ProviderConfig, Message, Collection } from '../types'
import { conversationsApi, settingsApi, collectionsApi } from '../services/api'
import { useDocAssistantRuntime, convertBackendMessage } from '../lib/assistant-runtime'
import AssistantChatView from '../components/Chat/AssistantChatView'
import { useToast } from '../components/common/ToastContext'

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
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [backendMessages, setBackendMessages] = useState<Message[]>([])
  const [messagesLoading, setMessagesLoading] = useState(false)
  const [editingConversationId, setEditingConversationId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [lmStudioConnected, setLmStudioConnected] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    async function loadData() {
      try {
        const [convos, provs, colls, lmStatus] = await Promise.all([
          conversationsApi.list(),
          settingsApi.listProviders(),
          collectionsApi.list(),
          settingsApi.checkLMStudio(),
        ])
        setConversations(convos)
        setProviders(provs)
        setCollections(colls)
        setLmStudioConnected(lmStatus.connected)
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

  useEffect(() => {
    if (!selectedConversation) {
      setBackendMessages([])
      return
    }
    // Sync collection ID from conversation
    setSelectedCollectionId(selectedConversation.collection_id)
    setMessagesLoading(true)
    conversationsApi.getMessages(selectedConversation.id)
      .then(setBackendMessages)
      .catch(err => {
        console.error('Failed to load messages:', err)
        showToast('Failed to load messages', 'error')
      })
      .finally(() => setMessagesLoading(false))
  }, [selectedConversation?.id])

  const handleNewChat = async () => {
    if (!selectedProvider) return
    try {
      const newConv = await conversationsApi.create({
        title: `New Chat ${conversations.length + 1}`,
        collection_id: selectedCollectionId || undefined,
      })
      setConversations([newConv, ...conversations])
      setSelectedConversation(newConv)
    } catch (err) {
      console.error('Failed to create conversation:', err)
      showToast('Failed to create conversation', 'error')
    }
  }

  const handleDeleteConversation = async (id: string) => {
    try {
      await conversationsApi.delete(id)
      setConversations(conversations.filter(c => c.id !== id))
      if (selectedConversation?.id === id) {
        setSelectedConversation(null)
      }
      showToast('Conversation deleted', 'success')
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      showToast('Failed to delete conversation', 'error')
    }
  }

  const handleRenameConversation = async (id: string, title: string) => {
    try {
      const updated = await conversationsApi.update(id, { title })
      setConversations(conversations.map(c => c.id === id ? updated : c))
      if (selectedConversation?.id === id) {
        setSelectedConversation(updated)
      }
    } catch (err) {
      console.error('Failed to rename conversation:', err)
      showToast('Failed to rename conversation', 'error')
    }
  }

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>
  }

  const setupComplete = lmStudioConnected && providers.length > 0
  const setupIssues: string[] = []
  if (!lmStudioConnected) setupIssues.push('LM Studio not connected')
  if (providers.length === 0) setupIssues.push('No LLM provider configured')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
      {!setupComplete && (
        <div style={{
          padding: '12px 20px',
          backgroundColor: '#fff3cd',
          borderBottom: '1px solid #ffc107',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          <span style={{ fontSize: '14px', color: '#856404' }}>
            ⚠️ Setup incomplete: {setupIssues.join(', ')}
          </span>
          <a href="/settings" style={{ fontSize: '13px', color: '#0066cc', textDecoration: 'none' }}>
            Go to Settings →
          </a>
        </div>
      )}
      <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
        <div style={{ width: '250px', flexShrink: 0, borderRight: '1px solid #ddd', padding: '10px', display: 'flex', flexDirection: 'column', height: '100%' }}>
        <button
          onClick={handleNewChat}
          disabled={!setupComplete}
          title={!setupComplete ? 'Complete setup in Settings first' : 'Start a new chat'}
          style={{
            padding: '10px',
            marginBottom: '10px',
            backgroundColor: setupComplete ? '#0066cc' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: setupComplete ? 'pointer' : 'not-allowed',
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

        <div style={{ marginBottom: '10px' }}>
          <label style={{ fontSize: '12px', color: '#666' }}>Scope:</label>
          <select
            value={selectedCollectionId || ''}
            onChange={(e) => setSelectedCollectionId(e.target.value || null)}
            style={{ width: '100%', padding: '5px', marginTop: '5px' }}
          >
            <option value="">All Collections</option>
            {collections.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
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
                {editingConversationId === conv.id ? (
                  <input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={() => {
                      if (editTitle.trim() && editTitle !== conv.title) {
                        handleRenameConversation(conv.id, editTitle.trim())
                      }
                      setEditingConversationId(null)
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        if (editTitle.trim() && editTitle !== conv.title) {
                          handleRenameConversation(conv.id, editTitle.trim())
                        }
                        setEditingConversationId(null)
                      }
                      if (e.key === 'Escape') setEditingConversationId(null)
                    }}
                    autoFocus
                    style={{
                      flex: 1,
                      padding: '2px 4px',
                      border: '1px solid #0066cc',
                      borderRadius: '2px',
                      fontSize: '14px',
                    }}
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <>
                    <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      <MessageSquareIcon size={14} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
                      {conv.title}
                      {conv.collection_id && (
                        <span style={{ marginLeft: '8px', fontSize: '11px', color: '#666', backgroundColor: '#e0e0e0', padding: '2px 6px', borderRadius: '10px' }}>
                          📚 {collections.find(c => c.id === conv.collection_id)?.name || 'Unknown'}
                        </span>
                      )}
                    </span>
                    <button
                      onClick={(e) => { e.stopPropagation(); setEditingConversationId(conv.id); setEditTitle(conv.title) }}
                      style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#666',
                        padding: '2px',
                        marginRight: '4px',
                      }}
                      title="Rename"
                    >
                      ✏️
                    </button>
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
                  </>
                )}
              </div>
            ))
          )}
        </div>
        </div>

      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', height: '100%' }}>
        {selectedConversation ? (
          <ChatViewWrapper
            key={selectedConversation.id}
            conversationId={selectedConversation.id}
            providerConfigId={selectedProvider}
            collectionId={selectedCollectionId}
            backendMessages={backendMessages}
            messagesLoading={messagesLoading}
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
    </div>
  )
}

function ChatViewWrapper({
  conversationId,
  providerConfigId,
  collectionId,
  backendMessages,
  messagesLoading,
}: {
  conversationId: string
  providerConfigId: string
  collectionId: string | null
  backendMessages: Message[]
  messagesLoading: boolean
}) {
  const initialMessages = backendMessages.map(convertBackendMessage)
  const runtime = useDocAssistantRuntime({
    conversationId,
    providerConfigId,
    collectionId: collectionId || undefined,
    initialMessages,
  })

  if (messagesLoading) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Loading messages...
      </div>
    )
  }

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ padding: '15px 20px', borderBottom: '1px solid #ddd', flexShrink: 0 }}>
          <h2 style={{ margin: 0, fontSize: '18px' }}>Chat</h2>
        </div>
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <AssistantChatView />
        </div>
      </div>
    </AssistantRuntimeProvider>
  )
}
