const employees = [
  { id: '1', name: 'Alex Morgan', email: 'alex@company.com', phone: '+1 555-0201', department: 'Support', role: 'Agent', status: 'online' },
  { id: '2', name: 'Taylor Swift', email: 'taylor@company.com', phone: '+1 555-0202', department: 'Sales', role: 'Manager', status: 'online' },
  { id: '3', name: 'Jordan Lee', email: 'jordan@company.com', phone: '+1 555-0203', department: 'Support', role: 'Agent', status: 'away' },
  { id: '4', name: 'Casey Park', email: 'casey@company.com', phone: '+1 555-0204', department: 'Operations', role: 'Lead', status: 'offline' },
]
const statusColors: Record<string, string> = { online: 'success', away: 'warning', offline: 'secondary' }
export default function Employees() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Employees</h4><p className="text-muted mb-0 fs-sm">Manage your team members</p></div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}><i className="bi bi-person-plus me-1" /> Add Employee</button>
      </div>
      <div className="data-card"><div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Employee</th><th>Department</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>{employees.map((e) => (<tr key={e.id}>
          <td><div className="d-flex align-items-center gap-2"><div className="chat-avatar" style={{ width: 34, height: 34, fontSize: '.7rem' }}>{e.name.split(' ').map(n => n[0]).join('')}</div><div><div className="fw-semibold" style={{ fontSize: '.85rem' }}>{e.name}</div><div className="text-muted" style={{ fontSize: '.7rem' }}>{e.email}</div></div></div></td>
          <td style={{ fontSize: '.85rem' }}>{e.department}</td><td style={{ fontSize: '.85rem' }}>{e.role}</td>
          <td><span className="d-inline-flex align-items-center gap-1"><span style={{ width: 8, height: 8, borderRadius: '50%', background: statusColors[e.status] === 'success' ? '#22c55e' : statusColors[e.status] === 'warning' ? '#eab308' : '#94a3b8' }} /><span className="fs-xs">{e.status}</span></span></td>
          <td><button className="btn btn-sm btn-light me-1"><i className="bi bi-pencil" /></button><button className="btn btn-sm btn-light"><i className="bi bi-trash" /></button></td>
        </tr>))}</tbody></table></div></div>
    </div>
  )
}
