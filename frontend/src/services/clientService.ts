import { api } from './api'
import type { Client, PaginatedResponse } from '@/types'

export const clientService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Client>>('/clients/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ client: Client }>(`/clients/${id}`).then(r => r.data),

  create: (data: Partial<Client>) =>
    api.post<Client>('/clients/', data).then(r => r.data),

  update: (id: string, data: Partial<Client>) =>
    api.patch(`/clients/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/clients/${id}`).then(r => r.data),
}
