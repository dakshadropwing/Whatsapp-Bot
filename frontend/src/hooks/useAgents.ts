import { useQuery } from '@tanstack/react-query'
import { agentService } from '@services/agentService'

export function useAgents(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['agents', params],
    queryFn: () => agentService.list(params),
  })
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: ['agents', id],
    queryFn: () => agentService.get(id),
    enabled: !!id,
  })
}
