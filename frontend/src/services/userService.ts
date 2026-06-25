import { api } from './api'
import type { User, PaginatedResponse } from '@/types'

export const userService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<User>>('/users/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ user: User }>(`/users/${id}`).then(r => r.data),

  create: (data: Partial<User> & Record<string, unknown>) =>
    api.post<User>('/users/', data).then(r => r.data),

  update: (id: string, data: Partial<User>) =>
    api.patch(`/users/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/users/${id}`).then(r => r.data),

  getRoles: () =>
    api.get<{ roles: { id: string; name: string; description: string }[] }>('/users/roles').then(r => r.data),
}
