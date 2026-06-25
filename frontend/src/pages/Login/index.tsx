import { useState } from 'react'
import { useAuth } from '@hooks/useAuth'
import { useAuthStore } from '@store/auth'
import { Navigate } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const { login, loading } = useAuth()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await login({ email, password })
  }

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Logo */}
        <div className="text-center mb-4">
          <div
            className="d-inline-flex align-items-center justify-content-center mb-3"
            style={{
              width: 56,
              height: 56,
              borderRadius: '1rem',
              background: 'linear-gradient(135deg, #25d366, #128c7e)',
              boxShadow: '0 8px 24px rgba(37,211,102,.3)',
            }}
          >
            <i className="bi bi-whatsapp text-white" style={{ fontSize: '1.75rem' }} />
          </div>
          <h4 className="fw-bold mb-1" style={{ letterSpacing: '-0.02em' }}>Welcome back</h4>
          <p className="text-muted mb-0" style={{ fontSize: '.9rem' }}>
            Sign in to your WhatsApp Automation Platform
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label fw-semibold" style={{ fontSize: '.8rem' }}>
              Email address
            </label>
            <div className="position-relative">
              <i
                className="bi bi-envelope position-absolute"
                style={{ left: 14, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
              />
              <input
                type="email"
                className="form-control ps-4"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ height: 44, borderRadius: '.5rem' }}
              />
            </div>
          </div>

          <div className="mb-4">
            <div className="d-flex justify-content-between align-items-center mb-1">
              <label className="form-label fw-semibold mb-0" style={{ fontSize: '.8rem' }}>
                Password
              </label>
              <a href="#" className="text-decoration-none" style={{ fontSize: '.75rem', color: '#25d366' }}>
                Forgot password?
              </a>
            </div>
            <div className="position-relative">
              <i
                className="bi bi-lock position-absolute"
                style={{ left: 14, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
              />
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-control ps-4 pe-4"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ height: 44, borderRadius: '.5rem' }}
              />
              <button
                type="button"
                className="btn btn-sm position-absolute border-0 bg-transparent p-0"
                style={{ right: 14, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
                onClick={() => setShowPassword(!showPassword)}
              >
                <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`} />
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn w-100 text-white fw-semibold"
            disabled={loading}
            style={{
              height: 44,
              borderRadius: '.5rem',
              background: 'linear-gradient(135deg, #25d366, #128c7e)',
              border: 'none',
              fontSize: '.9rem',
            }}
          >
            {loading ? (
              <span className="spinner-border spinner-border-sm me-2" role="status" />
            ) : (
              <i className="bi bi-arrow-right-circle me-2" />
            )}
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-4 pt-3" style={{ borderTop: '1px solid #e2e8f0' }}>
          <p className="text-muted mb-0" style={{ fontSize: '.8rem' }}>
            <i className="bi bi-shield-check me-1" />
            Secured with AES-256 encryption & JWT authentication
          </p>
        </div>
      </div>
    </div>
  )
}
