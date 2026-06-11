import { useState } from 'react'
import { Badge, Form, Row, Col } from 'react-bootstrap'

const clients = [
  { id: '1', name: 'Acme Corp', contact: 'John Smith', email: 'john@acme.com', phone: '+1 555-0101', conversations: 45, tags: ['enterprise', 'active'], created: 'Jan 15, 2026' },
  { id: '2', name: 'TechStart Inc', contact: 'Sarah Johnson', email: 'sarah@techstart.io', phone: '+1 555-0102', conversations: 28, tags: ['startup'], created: 'Feb 3, 2026' },
  { id: '3', name: 'Global Trade', contact: 'Mike Wilson', email: 'mike@globaltrade.com', phone: '+1 555-0103', conversations: 67, tags: ['enterprise', 'vip'], created: 'Dec 20, 2025' },
  { id: '4', name: 'QuickBite', contact: 'Emily Davis', email: 'emily@quickbite.co', phone: '+1 555-0104', conversations: 12, tags: ['startup', 'food'], created: 'Mar 10, 2026' },
  { id: '5', name: 'FitLife Gym', contact: 'Chris Brown', email: 'chris@fitlife.com', phone: '+1 555-0105', conversations: 34, tags: ['health', 'active'], created: 'Jan 28, 2026' },
  { id: '6', name: 'DataFlow AI', contact: 'Anna Lee', email: 'anna@dataflow.ai', phone: '+1 555-0106', conversations: 89, tags: ['enterprise', 'ai'], created: 'Nov 5, 2025' },
]

const tagColors: Record<string, string> = { enterprise: 'primary', startup: 'info', vip: 'warning', active: 'success', food: 'danger', health: 'success', ai: 'dark' }

export default function Clients() {
  const [search, setSearch] = useState('')
  const filtered = clients.filter((c) => c.name.toLowerCase().includes(search.toLowerCase()) || c.contact.toLowerCase().includes(search.toLowerCase()))

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Clients</h4>
          <p className="text-muted mb-0 fs-sm">Manage your customer database</p>
        </div>
        <div className="d-flex gap-2">
          <Form.Control size="sm" placeholder="Search clients..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ width: 220, borderRadius: '.5rem' }} />
          <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}>
            <i className="bi bi-plus-lg me-1" /> Add Client
          </button>
        </div>
      </div>

      {/* Stats */}
      <Row className="g-3 mb-4">
        {[
          { label: 'Total Clients', value: clients.length, icon: 'bi-people', color: '#25d366' },
          { label: 'Active', value: clients.filter((c) => c.tags.includes('active')).length, icon: 'bi-person-check', color: '#3b82f6' },
          { label: 'Enterprise', value: clients.filter((c) => c.tags.includes('enterprise')).length, icon: 'bi-building', color: '#8b5cf6' },
          { label: 'Total Conversations', value: clients.reduce((a, c) => a + c.conversations, 0), icon: 'bi-chat-dots', color: '#eab308' },
        ].map((s) => (
          <Col key={s.label} md={3}>
            <div className="stat-card">
              <div className="d-flex align-items-center gap-3">
                <div className="stat-icon" style={{ background: '#f0fdf4', color: s.color }}><i className={`bi ${s.icon}`} /></div>
                <div><div className="stat-value" style={{ fontSize: '1.4rem' }}>{s.value}</div><div className="stat-label">{s.label}</div></div>
              </div>
            </div>
          </Col>
        ))}
      </Row>

      {/* Table */}
      <div className="data-card">
        <div className="table-responsive">
          <table className="table table-custom mb-0">
            <thead>
              <tr><th>Client</th><th>Contact</th><th>Phone</th><th>Conversations</th><th>Tags</th><th>Joined</th></tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td><div className="fw-semibold" style={{ fontSize: '.85rem' }}>{c.name}</div></td>
                  <td>
                    <div style={{ fontSize: '.85rem' }}>{c.contact}</div>
                    <div className="text-muted" style={{ fontSize: '.7rem' }}>{c.email}</div>
                  </td>
                  <td style={{ fontSize: '.85rem' }}>{c.phone}</td>
                  <td><Badge bg="light" text="dark">{c.conversations}</Badge></td>
                  <td>
                    <div className="d-flex gap-1 flex-wrap">
                      {c.tags.map((tag) => <Badge key={tag} bg={tagColors[tag] || 'secondary'} className="badge-status">{tag}</Badge>)}
                    </div>
                  </td>
                  <td className="text-muted" style={{ fontSize: '.8rem' }}>{c.created}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
