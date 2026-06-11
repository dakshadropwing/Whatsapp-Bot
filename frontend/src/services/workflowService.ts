import { api } from './api'
import type { Workflow, PaginatedResponse } from '@/types'

export const workflowService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Workflow>>('/workflows', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ workflow: Workflow }>(`/workflows/${id}`).then(r => r.data),

  create: (data: Partial<Workflow>) =>
    api.post<Workflow>('/workflows', data).then(r => r.data),

  update: (id: string, data: Partial<Workflow>) =>
    api.patch(`/workflows/${id}`, data).then(r => r.data),

  toggle: (id: string) =>
    api.post(`/workflows/${id}/toggle`).then(r => r.data),
}
