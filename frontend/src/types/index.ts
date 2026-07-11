export interface Collection {
  id: string
  name: string
  description: string | null
  created_at: string | null
  updated_at: string | null
}

export interface Document {
  id: string
  collection_id: string
  file_path: string
  file_type: string
  file_size: number
  status: string
  error_message: string | null
  created_at: string | null
  updated_at: string | null
  indexed_at: string | null
}

export interface DocumentUploadResponse {
  id: string
  collection_id: string
  file_path: string
  file_type: string
  file_size: number
  status: string
  error_message: string | null
  created_at: string | null
  updated_at: string | null
  indexed_at: string | null
}

export interface Conversation {
  id: string
  title: string
  collection_id: string | null
  summary: string | null
  created_at: string | null
  updated_at: string | null
}

export interface Message {
  id: string
  conversation_id: string
  role: string
  content: string
  citations: Citation[] | null
  reasoning: string | null
  created_at: string | null
}

export interface Citation {
  text: string
  score: number
  file_path: string
  collection_id: string | null
  document_id: string | null
  chunk_index?: number
  parent_context?: string
}

export interface ProviderConfig {
  id: string
  name: string
  type: string
  provider_name: string
  model: string
  base_url: string | null
  api_key_ref: string | null
  created_at: string | null
  is_default: boolean
}

export interface ChatRequest {
  message: string
  conversation_id?: string
  collection_id?: string
  limit?: number
  provider_config_id?: string
}
export interface ChatResponse {
  conversation_id: string
  message_id: string
  content: string
  citations: Citation[]
  reasoning?: string
  iterations?: number
}
export interface LMStudioStatus {
  connected: boolean
  url: string
  model: string | null
  models: string[] | null
  error: string | null
}
