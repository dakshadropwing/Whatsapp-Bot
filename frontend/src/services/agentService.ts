import { api } from './api'
import type { Agent, PaginatedResponse } from '@/types'

export const agentService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Agent>>('/agents/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ agent: Agent }>(`/agents/${id}`).then(r => r.data),

  create: (data: Partial<Agent>) =>
    api.post<Agent>('/agents/', data).then(r => r.data),

  update: (id: string, data: Partial<Agent>) =>
    api.patch(`/agents/${id}`, data).then(r => r.data),

  toggle: (id: string) =>
    api.post(`/agents/${id}/toggle`).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/agents/${id}`).then(r => r.data),
}
