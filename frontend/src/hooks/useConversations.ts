import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { conversationService } from '@services/conversationService'
import { useConversationStore } from '@store/conversation'
import toast from 'react-hot-toast'

export function useConversations(params?: Record<string, unknown>) {
  const { setConversations } = useConversationStore()

  return useQuery({
    queryKey: ['conversations', params],
    queryFn: async () => {
      const data = await conversationService.list(params)
      setConversations(data.data)
      return data
    },
  })
}

export function useConversationMessages(conversationId: string | null) {
  const { setMessages } = useConversationStore()

  return useQuery({
    queryKey: ['messages', conversationId],
    queryFn: async () => {
      if (!conversationId) return { data: [], total: 0, page: 1, per_page: 50, total_pages: 0 }
      const data = await conversationService.getMessages(conversationId)
      setMessages(data.data)
      return data
    },
    enabled: !!conversationId,
  })
}

export function useResolveConversation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => conversationService.resolve(id),
    onSuccess: () => {
      toast.success('Conversation resolved')
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => toast.error('Failed to resolve'),
  })
}

export function useEscalateConversation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => conversationService.escalate(id),
    onSuccess: () => {
      toast.success('Conversation escalated')
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => toast.error('Failed to escalate'),
  })
}
