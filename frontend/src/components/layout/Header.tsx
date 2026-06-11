import { Dropdown } from 'react-bootstrap'
import { useAuthStore } from '@store/auth'
import { useAuth } from '@hooks/useAuth'

export default function Header() {
  const user = useAuthStore((s) => s.user)
  const { logout } = useAuth()

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U'

  return (
    <header className="top-header">
      {/* Left side — Search */}
      <div className="d-flex align-items-center gap-3">
        <div className="position-relative" style={{ width: 280 }}>
          <i className="bi bi-search position-absolute" style={{ left: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', fontSize: '.8rem' }} />
          <input
            type="text"
            className="form-control form-control-sm ps-4"
            placeholder="Search conversations, tickets..."
            style={{ borderRadius: '0.5rem', border: '1px solid #e2e8f0', fontSize: '.85rem' }}
          />
        </div>
      </div>

      {/* Right side — Actions + User */}
      <div className="d-flex align-items-center gap-3">
        {/* Notifications */}
        <button className="btn btn-sm btn-light position-relative" style={{ borderRadius: '0.5rem' }}>
          <i className="bi bi-bell" style={{ fontSize: '1rem' }} />
          <span
            className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
            style={{ fontSize: '.6rem', padding: '.2em .45em' }}
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
              }}
            >
              {initials}
            </div>
            <div className="d-none d-md-block text-start">
              <div style={{ fontSize: '.85rem', fontWeight: 600, lineHeight: 1.2 }}>{user?.full_name || 'User'}</div>
              <div style={{ fontSize: '.7rem', color: '#64748b', lineHeight: 1.2 }}>{user?.email || ''}</div>
            </div>
            <i className="bi bi-chevron-down" style={{ fontSize: '.65rem', color: '#94a3b8' }} />
          </Dropdown.Toggle>
          <Dropdown.Menu style={{ borderRadius: '0.5rem', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0,0,0,.07)', minWidth: 200 }}>
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
