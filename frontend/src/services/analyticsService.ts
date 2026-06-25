import { api } from './api'
import type { DashboardStats, AnalyticsOverview } from '@/types'

export const analyticsService = {
  getStats: () =>
    api.get<DashboardStats>('/analytics/stats').then(r => r.data),

  getOverview: (params?: { period?: string }) =>
    api.get<AnalyticsOverview>('/analytics/overview', params as Record<string, unknown>).then(r => r.data),

  getMessagesByDay: (params?: { days?: number }) =>
    api.get('/analytics/messages-by-day', params as Record<string, unknown>).then(r => r.data),

  getAgentUsage: () =>
    api.get('/analytics/agent-usage').then(r => r.data),

  getResponseTimes: () =>
    api.get('/analytics/response-times').then(r => r.data),
}
