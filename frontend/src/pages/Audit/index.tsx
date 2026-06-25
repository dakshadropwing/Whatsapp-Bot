import { Badge } from 'react-bootstrap'
const logs = [
  { id: '1', action: 'user.login', user: 'admin@platform.com', resource: 'Auth', detail: 'Successful login from 192.168.1.1', time: '2 min ago', level: 'info' },
  { id: '2', action: 'ticket.created', user: 'system', resource: 'Ticket', detail: 'New ticket #45 created by AI agent', time: '15 min ago', level: 'info' },
  { id: '3', action: 'agent.escalated', user: 'system', resource: 'Conversation', detail: 'Conversation escalated to human agent', time: '1 hour ago', level: 'warning' },
  { id: '4', action: 'settings.updated', user: 'admin@platform.com', resource: 'Settings', detail: 'WhatsApp configuration updated', time: '2 hours ago', level: 'info' },
  { id: '5', action: 'user.failed_login', user: 'unknown@test.com', resource: 'Auth', detail: 'Invalid credentials from 10.0.0.5', time: '3 hours ago', level: 'danger' },
  { id: '6', action: 'encryption.key_rotated', user: 'system', resource: 'Security', detail: 'AES encryption key rotated automatically', time: '1 day ago', level: 'info' },
]
const levelColors: Record<string, string> = { info: 'info', warning: 'warning', danger: 'danger' }
export default function Audit() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Audit Log</h4><p className="text-muted mb-0 fs-sm">Track all system actions and security events</p></div>
        <div className="d-flex gap-2"><select className="form-select form-select-sm" style={{ width: 140, borderRadius: '.5rem' }}><option>All Actions</option><option>Auth</option><option>Settings</option></select><button className="btn btn-sm btn-light"><i className="bi bi-download me-1" />Export</button></div>
      </div>
      <div className="data-card"><div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Action</th><th>User</th><th>Resource</th><th>Detail</th><th>Time</th></tr></thead>
        <tbody>{logs.map((l) => (<tr key={l.id}>
          <td><Badge bg={levelColors[l.level]} className="badge-status">{l.action}</Badge></td>
          <td className="fs-sm">{l.user}</td><td className="fs-sm">{l.resource}</td>
          <td className="text-muted fs-sm">{l.detail}</td><td className="text-muted" style={{ fontSize: '.8rem' }}>{l.time}</td>
        </tr>))}</tbody></table></div></div>
    </div>
  )
}
