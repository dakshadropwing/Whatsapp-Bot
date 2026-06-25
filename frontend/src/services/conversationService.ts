import { api } from './api'
import type { Conversation, Message, PaginatedResponse } from '@/types'

export const conversationService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Conversation>>('/conversations/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ conversation: Conversation }>(`/conversations/${id}`).then(r => r.data),

  getMessages: (id: string, params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Message>>(`/conversations/${id}/messages`, params).then(r => r.data),

  assign: (id: string, data: { assigned_user_id?: string; assigned_agent_id?: string }) =>
    api.patch(`/conversations/${id}`, data).then(r => r.data),

  resolve: (id: string) =>
    api.post(`/conversations/${id}/resolve`).then(r => r.data),

  escalate: (id: string) =>
    api.post(`/conversations/${id}/escalate`).then(r => r.data),
}
