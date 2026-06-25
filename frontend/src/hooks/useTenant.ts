import { useAuthStore } from '@store/auth'

export function useTenant() {
  const user = useAuthStore((s) => s.user)
  return { orgId: user?.organization_id ?? null }
}
