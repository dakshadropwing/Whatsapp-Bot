import { NavLink, useLocation } from 'react-router-dom'

interface NavItem {
  label: string
  path: string
  icon: string
}

interface NavSection {
  title: string
  items: NavItem[]
}

const navSections: NavSection[] = [
  {
    title: 'Main',
    items: [
      { label: 'Dashboard', path: '/dashboard', icon: 'bi-grid-1x2-fill' },
      { label: 'Conversations', path: '/conversations', icon: 'bi-chat-dots-fill' },
      { label: 'Tickets', path: '/tickets', icon: 'bi-ticket-detailed' },
    ],
  },
  {
    title: 'AI & Automation',
    items: [
      { label: 'Agents', path: '/agents', icon: 'bi-robot' },
      { label: 'Workflows', path: '/workflows', icon: 'bi-diagram-3-fill' },
      { label: 'Prompts', path: '/prompts', icon: 'bi-braces' },
      { label: 'Endpoints', path: '/endpoints', icon: 'bi-plug-fill' },
    ],
  },
  {
    title: 'Management',
    items: [
      { label: 'Clients', path: '/clients', icon: 'bi-people-fill' },
      { label: 'Employees', path: '/employees', icon: 'bi-person-badge-fill' },
      { label: 'Users', path: '/users', icon: 'bi-person-gear' },
      { label: 'WhatsApp', path: '/whatsapp', icon: 'bi-whatsapp' },
    ],
  },
  {
    title: 'Insights',
    items: [
      { label: 'Analytics', path: '/analytics', icon: 'bi-graph-up-arrow' },
      { label: 'Audit Log', path: '/audit', icon: 'bi-journal-text' },
      { label: 'Security', path: '/security', icon: 'bi-shield-lock-fill' },
      { label: 'Settings', path: '/settings', icon: 'bi-gear-fill' },
    ],
  },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <i className="bi bi-whatsapp" />
        </div>
        <span className="sidebar-brand-text">WA Platform</span>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navSections.map((section) => (
          <div key={section.title}>
            <div className="sidebar-section-title">{section.title}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-link${isActive || location.pathname.startsWith(item.path + '/') ? ' active' : ''}`
                }
              >
                <i className={`bi ${item.icon}`} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid rgba(255,255,255,.06)' }}>
        <div className="d-flex align-items-center gap-2">
          <div
            style={{
              width: 32,
              height: 32,
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
            AI
          </div>
          <div>
            <div style={{ color: '#e2e8f0', fontSize: '.8rem', fontWeight: 600 }}>v1.0.0</div>
            <div style={{ color: '#64748b', fontSize: '.65rem' }}>WhatsApp Platform</div>
          </div>
        </div>
      </div>
    </aside>
  )
}
