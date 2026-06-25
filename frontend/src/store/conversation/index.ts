import { create } from 'zustand'
import type { Conversation, Message } from '@/types'

interface ConversationState {
  conversations: Conversation[]
  activeConversationId: string | null
  messages: Message[]
  loading: boolean

  setConversations: (conversations: Conversation[]) => void
  setActiveConversation: (id: string | null) => void
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  setLoading: (loading: boolean) => void
}

export const useConversationStore = create<ConversationState>()((set) => ({
  conversations: [],
  activeConversationId: null,
  messages: [],
  loading: false,

  setConversations: (conversations) => set({ conversations }),
  setActiveConversation: (id) => set({ activeConversationId: id, messages: [] }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((s) => ({ messages: [...s.messages, message] })),
  setLoading: (loading) => set({ loading }),
}))
