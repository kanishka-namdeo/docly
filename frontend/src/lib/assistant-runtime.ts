import { useMemo } from 'react';
import { useLocalRuntime } from '@assistant-ui/react';
import type { ChatModelAdapter, ChatModelRunOptions, ChatModelRunResult, ThreadMessageLike } from '@assistant-ui/react';
import type { Citation } from '../types';

const API_BASE = 'http://127.0.0.1:8000';

interface AdapterContext {
  getConversationId: () => string | undefined;
  getProviderConfigId: () => string | undefined;
}

function createChatModelAdapter(ctx: AdapterContext): ChatModelAdapter {
  return {
    async run({ messages, abortSignal }: ChatModelRunOptions): Promise<ChatModelRunResult> {
      // Find last user message
      const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
      if (!lastUserMsg) {
        return { content: [{ type: 'text', text: '' }] };
      }

      const textPart = lastUserMsg.content.find((p) => p.type === 'text');
      const userText = textPart?.type === 'text' ? textPart.text : '';

      const conversationId = ctx.getConversationId();
      const providerConfigId = ctx.getProviderConfigId();
      if (!providerConfigId || !conversationId) {
        return { content: [{ type: 'text', text: 'No provider or conversation selected.' }] };
      }

      const response = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          conversation_id: conversationId,
          provider_config_id: providerConfigId,
        }),
        signal: abortSignal,
      });

      if (!response.ok) throw new Error(`Chat API error: ${response.status}`);

      const data = await response.json();

      return {
        content: [{ type: 'text', text: data.content }],
        metadata: {
          custom: {
            citations: data.citations as Citation[],
            messageId: data.message_id,
            conversationId: data.conversation_id,
          },
        },
      };
    },
  };
}

export function convertBackendMessage(msg: {
  id: string;
  role: string;
  content: string;
  citations?: Citation[] | null;
  created_at?: string | null;
}): ThreadMessageLike {
  return {
    id: msg.id,
    role: msg.role as 'user' | 'assistant',
    content: [{ type: 'text' as const, text: msg.content }],
    createdAt: msg.created_at ? new Date(msg.created_at) : new Date(),
    metadata: {
      custom: {
        citations: msg.citations || [],
      },
    },
  };
}

interface UseDocAssistantRuntimeOptions {
  conversationId: string | undefined;
  providerConfigId: string | undefined;
  initialMessages?: ThreadMessageLike[];
}

export function useDocAssistantRuntime({
  conversationId,
  providerConfigId,
  initialMessages,
}: UseDocAssistantRuntimeOptions) {
  const convIdRef = { current: conversationId };
  convIdRef.current = conversationId;
  const provIdRef = { current: providerConfigId };
  provIdRef.current = providerConfigId;

  const adapter = useMemo(
    () =>
      createChatModelAdapter({
        getConversationId: () => convIdRef.current,
        getProviderConfigId: () => provIdRef.current,
      }),
    [] // stable — refs handle updates
  );

  return useLocalRuntime(adapter, {
    initialMessages,
  });
}
