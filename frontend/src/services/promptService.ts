import { api } from './api'
import type { PromptTemplate, PaginatedResponse } from '@/types'

export const promptService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<PromptTemplate>>('/prompts/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ prompt: PromptTemplate }>(`/prompts/${id}`).then(r => r.data),

  create: (data: Partial<PromptTemplate>) =>
    api.post<PromptTemplate>('/prompts/', data).then(r => r.data),

  update: (id: string, data: Partial<PromptTemplate>) =>
    api.patch(`/prompts/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/prompts/${id}`).then(r => r.data),
}
