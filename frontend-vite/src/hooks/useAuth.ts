import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '@store/auth'
import { authService } from '@services/authService'
import type { LoginRequest } from '@/types'

export function useAuth() {
  const [loading, setLoading] = useState(false)
  const { setAuth, logout: clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const login = useCallback(async (data: LoginRequest) => {
    setLoading(true)
    try {
      const res = await authService.login(data)
      setAuth(res.user, res.access_token, res.refresh_token)
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { error?: string } } })?.response?.data?.error || 'Login failed'
      toast.error(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [setAuth, navigate])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch { /* ignore */ }
    clearAuth()
    toast.success('Logged out')
    navigate('/login')
  }, [clearAuth, navigate])

  return { login, logout, loading }
}
