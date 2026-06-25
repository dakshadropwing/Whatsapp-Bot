import { Dropdown } from 'react-bootstrap'
import { useAuthStore } from '@store/auth'
import { useAuth } from '@hooks/useAuth'

export default function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  const user = useAuthStore((s) => s.user)
  const { logout } = useAuth()

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U'

  return (
    <header className="top-header">
      {/* Left side — Menu Toggle (Mobile) + Search */}
      <div className="d-flex align-items-center gap-3">
        <button 
          className="btn btn-sm btn-light d-lg-none"
          onClick={onMenuClick}
          style={{ width: 38, height: 38, padding: 0 }}
        >
          <i className="bi bi-list fs-5" />
        </button>
        <div className="position-relative d-none d-md-block" style={{ width: 300 }}>
          <i className="bi bi-search position-absolute" style={{ left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569', fontSize: '.8rem' }} />
          <input
            type="text"
            className="form-control form-control-sm ps-5"
            placeholder="Search conversations, tickets..."
            style={{ borderRadius: '0.75rem', fontSize: '.85rem', height: 38 }}
          />
        </div>
      </div>

      {/* Right side — Actions + User */}
      <div className="d-flex align-items-center gap-3">
        {/* Notifications */}
        <button
          className="btn btn-sm btn-light position-relative"
          style={{ borderRadius: '0.75rem', width: 38, height: 38, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <i className="bi bi-bell" style={{ fontSize: '1rem' }} />
          <span
            className="position-absolute badge rounded-pill"
            style={{
              fontSize: '.55rem',
              padding: '.2em .45em',
              top: 4,
              right: 4,
              background: '#ef4444',
              color: '#fff',
            }}
          >
            3
          </span>
        </button>

        {/* User Dropdown */}
        <Dropdown align="end">
          <Dropdown.Toggle as="button" className="d-flex align-items-center gap-2 border-0 bg-transparent p-0" id="user-dropdown">
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #25d366, #128c7e)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '.75rem',
                fontWeight: 700,
                boxShadow: '0 2px 10px rgba(37,211,102,.25)',
              }}
            >
              {initials}
            </div>
            <div className="d-none d-md-block text-start">
              <div style={{ fontSize: '.85rem', fontWeight: 600, lineHeight: 1.2, color: 'var(--text-primary)' }}>{user?.full_name || 'User'}</div>
              <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', lineHeight: 1.2 }}>{user?.email || ''}</div>
            </div>
            <i className="bi bi-chevron-down" style={{ fontSize: '.65rem', color: 'var(--text-muted)' }} />
          </Dropdown.Toggle>
          <Dropdown.Menu>
            <Dropdown.Item href="/settings">
              <i className="bi bi-person me-2" /> Profile
            </Dropdown.Item>
            <Dropdown.Item href="/settings">
              <i className="bi bi-gear me-2" /> Settings
            </Dropdown.Item>
            <Dropdown.Divider />
            <Dropdown.Item onClick={logout} className="text-danger">
              <i className="bi bi-box-arrow-right me-2" /> Sign Out
            </Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>
    </header>
  )
}
