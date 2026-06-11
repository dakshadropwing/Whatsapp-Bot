import { Badge } from 'react-bootstrap'
const users = [
  { id: '1', name: 'Admin User', email: 'admin@platform.com', role: 'Super Admin', status: 'active', lastLogin: '2 hours ago' },
  { id: '2', name: 'Jane Cooper', email: 'jane@platform.com', role: 'Manager', status: 'active', lastLogin: '1 day ago' },
  { id: '3', name: 'Robert Fox', email: 'robert@platform.com', role: 'Agent', status: 'active', lastLogin: '3 hours ago' },
  { id: '4', name: 'Mary Johnson', email: 'mary@platform.com', role: 'Agent', status: 'inactive', lastLogin: '2 weeks ago' },
]
const roleColors: Record<string, string> = { 'Super Admin': 'danger', Manager: 'primary', Agent: 'success' }
export default function Users() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Users</h4><p className="text-muted mb-0 fs-sm">Manage platform users and roles</p></div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}><i className="bi bi-plus-lg me-1" /> Invite User</button>
      </div>
      <div className="data-card">
        <div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Last Login</th><th></th></tr></thead>
          <tbody>{users.map((u) => (<tr key={u.id}>
            <td><div className="d-flex align-items-center gap-2"><div className="chat-avatar" style={{ width: 34, height: 34, fontSize: '.7rem' }}>{u.name.split(' ').map(n => n[0]).join('')}</div><div><div className="fw-semibold" style={{ fontSize: '.85rem' }}>{u.name}</div><div className="text-muted" style={{ fontSize: '.7rem' }}>{u.email}</div></div></div></td>
            <td><Badge bg={roleColors[u.role] || 'secondary'} className="badge-status">{u.role}</Badge></td>
            <td><Badge bg={u.status === 'active' ? 'success' : 'secondary'} className="badge-status">{u.status}</Badge></td>
            <td className="text-muted" style={{ fontSize: '.8rem' }}>{u.lastLogin}</td>
            <td><button className="btn btn-sm btn-light"><i className="bi bi-pencil" /></button></td>
          </tr>))}</tbody>
        </table></div>
      </div>
    </div>
  )
}
