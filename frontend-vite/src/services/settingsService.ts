import { api } from './api'

export const settingsService = {
  get: () =>
    api.get<Record<string, any>>('/settings/').then(r => r.data),

  update: (data: Record<string, any>) =>
    api.patch<{ updated: boolean; settings: Record<string, any> }>('/settings/', data).then(r => r.data),

  getSection: (section: string) =>
    api.get<{ section: string; data: any }>(`/settings/${section}`).then(r => r.data),
}
