import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE = '/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    })

    // Request interceptor — attach JWT
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const raw = localStorage.getItem('auth-storage')
        if (raw) {
          try {
            const parsed = JSON.parse(raw)
            const token = parsed?.state?.accessToken
            if (token && config.headers) {
              config.headers.Authorization = `Bearer ${token}`
            }
          } catch { /* ignore */ }
        }
        return config
      },
      (err) => Promise.reject(err),
    )

    // Response interceptor — handle 401
    this.client.interceptors.response.use(
      (res) => res,
      async (err: AxiosError) => {
        if (err.response?.status === 401) {
          // Try refresh
          const raw = localStorage.getItem('auth-storage')
          if (raw) {
            try {
              const parsed = JSON.parse(raw)
              const refreshToken = parsed?.state?.refreshToken
              if (refreshToken && !err.config?.url?.includes('/refresh')) {
                const { data } = await axios.post(`${API_BASE}/auth/refresh`, {}, {
                  headers: { Authorization: `Bearer ${refreshToken}` },
                })
                // Update token
                parsed.state.accessToken = data.access_token
                localStorage.setItem('auth-storage', JSON.stringify(parsed))
                // Retry original request
                if (err.config?.headers) {
                  err.config.headers.Authorization = `Bearer ${data.access_token}`
                }
                return this.client(err.config!)
              }
            } catch { /* refresh failed */ }
          }
          // Clear auth and redirect
          localStorage.removeItem('auth-storage')
          window.location.href = '/login'
        }
        return Promise.reject(err)
      },
    )
  }

  // ── Public Methods ──────────────────────────────────────

  get<T>(url: string, params?: Record<string, unknown>) {
    return this.client.get<T>(url, { params })
  }

  post<T>(url: string, data?: unknown) {
    return this.client.post<T>(url, data)
  }

  put<T>(url: string, data?: unknown) {
    return this.client.put<T>(url, data)
  }

  patch<T>(url: string, data?: unknown) {
    return this.client.patch<T>(url, data)
  }

  delete<T>(url: string) {
    return this.client.delete<T>(url)
  }
}

export const api = new ApiClient()
