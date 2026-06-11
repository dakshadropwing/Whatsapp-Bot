import { useState } from 'react'
import { Badge, Dropdown } from 'react-bootstrap'

const priorityColors: Record<string, string> = { low: 'secondary', medium: 'info', high: 'warning', urgent: 'danger' }
const statusColors: Record<string, string> = { open: 'success', in_progress: 'primary', waiting_on_customer: 'warning', resolved: 'secondary', closed: 'dark' }

const tickets = [
  { id: '1', title: 'Cannot process payment', contact: 'John Smith', phone: '+1 555-0101', priority: 'urgent', status: 'open', agent: 'Support', created: '2 hours ago' },
  { id: '2', title: 'Feature request: bulk messaging', contact: 'Sarah Johnson', phone: '+1 555-0102', priority: 'low', status: 'open', agent: 'Sales', created: '3 hours ago' },
  { id: '3', title: 'Integration API timeout', contact: 'Mike Wilson', phone: '+1 555-0103', priority: 'high', status: 'in_progress', agent: 'Support', created: '5 hours ago' },
  { id: '4', title: 'Account access issue', contact: 'Emily Davis', phone: '+1 555-0104', priority: 'high', status: 'waiting_on_customer', agent: 'Support', created: '1 day ago' },
  { id: '5', title: 'Refund request', contact: 'Chris Brown', phone: '+1 555-0105', priority: 'medium', status: 'resolved', agent: 'Sales', created: '2 days ago' },
  { id: '6', title: 'Wrong order delivered', contact: 'Anna Lee', phone: '+1 555-0106', priority: 'high', status: 'in_progress', agent: 'Support', created: '2 days ago' },
]

export default function Tickets() {
  const [filter, setFilter] = useState('all')

  const filtered = tickets.filter((t) => filter === 'all' || t.status === filter)

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Support Tickets</h4>
          <p className="text-muted mb-0 fs-sm">Track and manage customer support tickets</p>
        </div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}>
          <i className="bi bi-plus-lg me-1" /> New Ticket
        </button>
      </div>

      {/* Filter tabs */}
      <div className="d-flex gap-2 mb-3">
        {['all', 'open', 'in_progress', 'waiting_on_customer', 'resolved'].map((f) => (
          <button key={f} className={`btn btn-sm ${filter === f ? 'btn-dark' : 'btn-light'}`} style={{ fontSize: '.78rem', borderRadius: '1rem', padding: '.3rem .9rem' }} onClick={() => setFilter(f)}>
            {f === 'all' ? 'All' : f.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
            <span className="ms-1 badge bg-white text-dark" style={{ fontSize: '.65rem' }}>
              {f === 'all' ? tickets.length : tickets.filter((t) => t.status === f).length}
            </span>
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="data-card">
        <div className="table-responsive">
          <table className="table table-custom mb-0">
            <thead>
              <tr>
                <th>Ticket</th>
                <th>Contact</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Agent</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.id}>
                  <td>
                    <div className="fw-semibold" style={{ fontSize: '.85rem' }}>#{t.id} {t.title}</div>
                  </td>
                  <td>
                    <div style={{ fontSize: '.85rem' }}>{t.contact}</div>
                    <div className="text-muted" style={{ fontSize: '.7rem' }}>{t.phone}</div>
                  </td>
                  <td><Badge bg={priorityColors[t.priority]} className="badge-status">{t.priority}</Badge></td>
                  <td><Badge bg={statusColors[t.status]} className="badge-status">{t.status.replace(/_/g, ' ')}</Badge></td>
                  <td style={{ fontSize: '.85rem' }}>{t.agent}</td>
                  <td className="text-muted" style={{ fontSize: '.8rem' }}>{t.created}</td>
                  <td>
                    <Dropdown align="end">
                      <Dropdown.Toggle as="button" className="btn btn-sm btn-light border-0"><i className="bi bi-three-dots" /></Dropdown.Toggle>
                      <Dropdown.Menu>
                        <Dropdown.Item><i className="bi bi-arrow-repeat me-2" /> Change Status</Dropdown.Item>
                        <Dropdown.Item><i className="bi bi-person-plus me-2" /> Reassign</Dropdown.Item>
                        <Dropdown.Item className="text-danger"><i className="bi bi-trash me-2" /> Delete</Dropdown.Item>
                      </Dropdown.Menu>
                    </Dropdown>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
