import type {
  Collection,
  Document,
  Conversation,
  Message,
  ProviderConfig,
  ChatRequest,
  ChatResponse,
  LMStudioStatus,
  DocumentUploadResponse,
} from '../types'

const API_BASE = 'http://127.0.0.1:8000'

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}

export const collectionsApi = {
  list: () => request<Collection[]>('/collections/'),
  create: (data: { name: string; description?: string }) =>
    request<Collection>('/collections/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  get: (id: string) => request<Collection>(`/collections/${id}`),
  update: (id: string, data: { name?: string; description?: string }) =>
    request<Collection>(`/collections/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: async (id: string) => {
    const response = await fetch(`${API_BASE}/collections/${id}`, { method: 'DELETE' })
    if (!response.ok && response.status !== 204) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }
  },
}

export const documentsApi = {
  list: (collectionId: string) =>
    request<Document[]>(`/documents/collection/${collectionId}`),
  upload: async (collectionId: string, file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/documents/upload?collection_id=${collectionId}`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    return response.json()
  },
  delete: async (id: string) => {
    const response = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' })
    if (!response.ok && response.status !== 204) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }
  },
}

export const conversationsApi = {
  list: () => request<Conversation[]>('/conversations/'),
  create: (data: { title: string; collection_id?: string }) =>
    request<Conversation>('/conversations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: string, data: { title?: string; collection_id?: string | null }) =>
    request<Conversation>(`/conversations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  getMessages: (conversationId: string) =>
    request<Message[]>(`/conversations/${conversationId}/messages`),
  delete: async (id: string) => {
    const response = await fetch(`${API_BASE}/conversations/${id}`, { method: 'DELETE' })
    if (!response.ok && response.status !== 204) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }
  },
}

export const chatApi = {
  send: (data: ChatRequest) =>
    request<ChatResponse>('/chat/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

export const settingsApi = {
  listProviders: () => request<ProviderConfig[]>('/settings/providers'),
  createProvider: (data: {
    name: string
    type: string
    provider_name: string
    model: string
    base_url?: string
    api_key_ref?: string
  }) =>
    request<ProviderConfig>('/settings/providers', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateProvider: (id: string, data: {
    name?: string
    type?: string
    provider_name?: string
    model?: string
    base_url?: string
    api_key?: string
  }) =>
    request<ProviderConfig>(`/settings/providers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  testProvider: (data: {
    name: string
    type: string
    provider_name: string
    model: string
    base_url?: string
    api_key?: string
  }) =>
    request<{ success: boolean; error: string | null }>('/settings/providers/test', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteProvider: async (id: string) => {
    const response = await fetch(`${API_BASE}/settings/providers/${id}`, { method: 'DELETE' })
    if (!response.ok && response.status !== 204) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }
  },
  checkLMStudio: () => request<LMStudioStatus>('/settings/lm-studio/status'),
  setEmbeddingModel: (model: string) =>
    request<{ status: string; model: string }>('/settings/embedding/model', {
      method: 'POST',
      body: JSON.stringify({ model }),
    }),
  setDefaultProvider: (id: string) =>
    request<{ status: string; id: string; is_default: boolean }>(`/settings/providers/${id}/default`, {
      method: 'PUT',
    }),
  getPreferences: () => request<{ theme: string; language: string }>('/settings/preferences'),
  updatePreferences: (data: { theme?: string; language?: string }) =>
    request<{ theme: string; language: string }>('/settings/preferences', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
}
