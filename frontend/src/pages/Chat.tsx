import { useState, useEffect } from 'react'
import { AssistantRuntimeProvider } from '@assistant-ui/react'
import { Conversation, ProviderConfig, Message, Collection } from '../types'
import { conversationsApi, settingsApi, collectionsApi } from '../services/api'
import { useDocAssistantRuntime, convertBackendMessage } from '../lib/assistant-runtime'
import AssistantChatView from '../components/Chat/AssistantChatView'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { PlusCircle, Pencil, X, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'

function MessageSquareIcon({ size = 16, className }: { size?: number; className?: string }) {
  return (
    <MessageSquare width={size} height={size} className={className} />
  )
}

function PlusCircleIcon({ size = 16 }: { size?: number }) {
  return (
    <PlusCircle width={size} height={size} />
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

  useEffect(() => {
    Promise.all([
      settingsApi.checkLMStudio().then(s => setLmStudioConnected(s.connected)).catch(() => setLmStudioConnected(false)),
      settingsApi.listProviders().then(setProviders).catch(() => setProviders([])),
      collectionsApi.list().then(setCollections).catch(() => setCollections([])),
      conversationsApi.list().then(setConversations).catch(() => setConversations([])),
    ]).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedConversation?.id) {
      setBackendMessages([])
      return
    }
    setMessagesLoading(true)
    conversationsApi.getMessages(selectedConversation.id)
      .then(setBackendMessages)
      .catch(err => {
        console.error('Failed to load messages:', err)
        toast.error('Failed to load conversation messages')
        setBackendMessages([])
      })
      .finally(() => setMessagesLoading(false))
  }, [selectedConversation?.id])


  const handleDeleteConversation = async (id: string) => {
    if (!confirm('Delete this conversation?')) return
    try {
      await conversationsApi.delete(id)
      setConversations(conversations.filter(c => c.id !== id))
      if (selectedConversation?.id === id) {
        setSelectedConversation(null)
      }
      toast.success('Conversation deleted')
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      toast.error('Failed to delete conversation')
    }
  }

  const handleRenameConversation = async (id: string, title: string) => {
    try {
      await conversationsApi.update(id, { title })
      setConversations(conversations.map(c => c.id === id ? { ...c, title } : c))
      toast.success('Conversation renamed')
    } catch (err) {
      console.error('Failed to rename conversation:', err)
      toast.error('Failed to rename conversation')
    }
  }
  const handleNewChat = async () => {
    try {
      const conv = await conversationsApi.create({ title: 'New Conversation' })
      setConversations([conv, ...conversations])
      setSelectedConversation(conv)
    } catch (err) {
      console.error('Failed to create conversation:', err)
      toast.error('Failed to create conversation')
    }
  }

  if (loading) {
    return <div className="p-5">Loading...</div>
  }

  const setupComplete = lmStudioConnected && providers.length > 0
  const setupIssues: string[] = []
  if (!lmStudioConnected) setupIssues.push('LM Studio not connected')
  if (providers.length === 0) setupIssues.push('No LLM provider configured')

  return (
    <div className="flex flex-col h-full min-h-0">
      {!setupComplete && (
        <div className="p-4 bg-yellow-50 border-b border-yellow-200 flex items-center gap-4 dark:bg-yellow-900/20 dark:border-yellow-800">
          <span className="text-sm text-yellow-800 dark:text-yellow-200">
            ⚠️ Setup incomplete: {setupIssues.join(', ')}
          </span>
          <a href="/settings" className="text-sm text-primary hover:underline">
            Go to Settings →
          </a>
        </div>
      )}
      <div className="flex flex-1 min-h-0">
        <div className="w-[250px] flex-shrink-0 border-r border-border p-2 flex flex-col h-full">
          <Button
            onClick={handleNewChat}
            disabled={!setupComplete}
            title={!setupComplete ? 'Complete setup in Settings first' : 'Start a new chat'}
            variant="default"
            className="w-full mb-2 justify-start gap-2"
          >
            <PlusCircleIcon size={16} />
            New Chat
          </Button>

          <div className="mb-2">
            <label className="text-xs text-muted-foreground">Provider:</label>
            <Select value={selectedProvider} onValueChange={setSelectedProvider}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                {providers.map(p => (
                  <SelectItem key={p.id} value={p.id}>{p.name} ({p.model})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="mb-2">
            <label className="text-xs text-muted-foreground">Scope:</label>
            <Select value={selectedCollectionId || ''} onValueChange={(v) => setSelectedCollectionId(v || null)}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="All Collections" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Collections</SelectItem>
                {collections.map(c => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <ScrollArea className="flex-1">
            {conversations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No conversations yet</p>
            ) : (
              conversations.map(conv => (
                <div
                  key={conv.id}
                  onClick={() => setSelectedConversation(conv)}
                  className={cn(
                    'p-2 mb-1 rounded-md cursor-pointer flex justify-between items-center',
                    selectedConversation?.id === conv.id ? 'bg-secondary' : 'hover:bg-muted'
                  )}
                >
                  {editingConversationId === conv.id ? (
                    <Input
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
                      className="flex-1 h-auto py-0.5 px-1 text-sm"
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <span className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap text-sm">
                        <MessageSquareIcon size={14} className="inline mr-1 align-middle" />
                        {conv.title}
                        {conv.collection_id && (
                          <Badge variant="secondary" className="ml-2 text-[10px] px-1.5 py-0 rounded-full">
                            📚 {collections.find(c => c.id === conv.collection_id)?.name || 'Unknown'}
                          </Badge>
                        )}
                      </span>
                      <div className="flex gap-0.5">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={(e) => { e.stopPropagation(); setEditingConversationId(conv.id); setEditTitle(conv.title) }}
                          title="Rename"
                        >
                          <Pencil className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-muted-foreground"
                          onClick={(e) => { e.stopPropagation(); handleDeleteConversation(conv.id) }}
                          title="Delete"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </ScrollArea>
        </div>

        <div className="flex-1 min-w-0 flex flex-col h-full">
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
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <MessageSquareIcon size={48} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">Select a conversation or start a new chat</p>
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
      <div className="flex-1 flex items-center justify-center">
        Loading messages...
      </div>
    )
  }

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="flex flex-col h-full">
        <div className="p-4 border-b border-border flex-shrink-0">
          <h2 className="m-0 text-lg font-semibold">Chat</h2>
        </div>
        <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
          <AssistantChatView />
        </div>
      </div>
    </AssistantRuntimeProvider>
  )
}
