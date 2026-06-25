import { api } from './api'
import type { EndpointConfig, PaginatedResponse } from '@/types'

export const endpointService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<EndpointConfig>>('/endpoints/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ endpoint: EndpointConfig }>(`/endpoints/${id}`).then(r => r.data),

  create: (data: Partial<EndpointConfig>) =>
    api.post<EndpointConfig>('/endpoints/', data).then(r => r.data),

  update: (id: string, data: Partial<EndpointConfig>) =>
    api.patch(`/endpoints/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/endpoints/${id}`).then(r => r.data),

  test: (id: string, payload?: Record<string, unknown>) =>
    api.post<{ id: string; success: boolean; status_code: number; response: string }>(`/endpoints/${id}/test`, { payload }).then(r => r.data),
}
