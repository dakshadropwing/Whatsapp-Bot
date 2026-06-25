import { api } from './api'
import type { Ticket, PaginatedResponse } from '@/types'

export const ticketService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Ticket>>('/tickets/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ ticket: Ticket }>(`/tickets/${id}`).then(r => r.data),

  create: (data: Partial<Ticket>) =>
    api.post<Ticket>('/tickets/', data).then(r => r.data),

  update: (id: string, data: Partial<Ticket>) =>
    api.patch(`/tickets/${id}`, data).then(r => r.data),

  updateStatus: (id: string, status: string) =>
    api.patch(`/tickets/${id}/status`, { status }).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/tickets/${id}`).then(r => r.data),
}

