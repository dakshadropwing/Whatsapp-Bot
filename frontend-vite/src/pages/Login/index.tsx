import { useState } from 'react'
import { useAuth } from '@hooks/useAuth'
import { useAuthStore } from '@store/auth'
import { Navigate } from 'react-router-dom'
import { PageWrapper } from '@components/PageWrapper'
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
    <PageWrapper className="login-page">
      {/* Extra floating orb */}
      <div style={{
        position: 'absolute', top: '40%', left: '50%', width: 300, height: 300,
        borderRadius: '50%', background: 'radial-gradient(circle, rgba(37,211,102,.06) 0%, transparent 70%)',
        animation: 'floatOrb 18s ease-in-out infinite', pointerEvents: 'none',
      }} />

      <div className="login-card">
        {/* Logo */}
        <div className="text-center mb-4">
          <div
            className="d-inline-flex align-items-center justify-content-center mb-3"
            style={{
              width: 60,
              height: 60,
              borderRadius: '1.25rem',
              background: 'linear-gradient(135deg, #25d366, #128c7e)',
              boxShadow: '0 8px 30px rgba(37,211,102,.35)',
              animation: 'pulseGlow 3s ease-in-out infinite',
            }}
          >
            <i className="bi bi-whatsapp text-white" style={{ fontSize: '1.9rem' }} />
          </div>
          <h4 className="fw-bold mb-1" style={{ letterSpacing: '-0.02em', color: '#f1f5f9' }}>Welcome back</h4>
          <p style={{ fontSize: '.9rem', color: '#64748b' }}>
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
              <i className="bi bi-envelope position-absolute" style={{ left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569' }} />
              <input
                type="email"
                className="form-control ps-5"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ height: 46, borderRadius: '.75rem' }}
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
              <i className="bi bi-lock position-absolute" style={{ left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-control ps-5 pe-5"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ height: 46, borderRadius: '.75rem' }}
              />
              <button
                type="button"
                className="btn btn-sm position-absolute border-0 bg-transparent p-0"
                style={{ right: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569' }}
                onClick={() => setShowPassword(!showPassword)}
              >
                <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`} />
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-wa-primary w-100"
            disabled={loading}
            style={{ height: 46, fontSize: '.9rem' }}
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
        <div className="text-center mt-4 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,.06)' }}>
          <p className="mb-0" style={{ fontSize: '.78rem', color: '#475569' }}>
            <i className="bi bi-shield-check me-1" style={{ color: '#25d366' }} />
            Secured with AES-256 encryption & JWT authentication
          </p>
        </div>
      </div>
    </PageWrapper>
  )
}
