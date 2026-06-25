import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '@services/analyticsService'

export function useDashboardStats() {
  return useQuery({
    queryKey: ['analytics', 'stats'],
    queryFn: () => analyticsService.getStats(),
    refetchInterval: 60000,
  })
}

export function useAnalyticsOverview(period?: string) {
  return useQuery({
    queryKey: ['analytics', 'overview', period],
    queryFn: () => analyticsService.getOverview({ period }),
  })
}
