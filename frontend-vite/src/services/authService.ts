import { api } from './api'
import type { LoginRequest, LoginResponse, User } from '@/types'

export const authService = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data).then(r => r.data),

  refreshToken: () =>
    api.post<{ access_token: string }>('/auth/refresh').then(r => r.data),

  logout: () =>
    api.post('/auth/logout').then(r => r.data),

  getProfile: () =>
    api.get<{ user: User }>('/auth/me').then(r => r.data),
}
