import { Badge, Form } from 'react-bootstrap'
const endpoints = [
  { id: '1', name: 'crm_update', url: 'https://api.crm.com/v1/contacts', method: 'POST', active: true, calls: 234 },
  { id: '2', name: 'order_status', url: 'https://orders.internal.com/api/status', method: 'GET', active: true, calls: 456 },
  { id: '3', name: 'webhook_notify', url: 'https://hooks.slack.com/services/xxx', method: 'POST', active: false, calls: 89 },
]
const methodColors: Record<string, string> = { GET: 'success', POST: 'primary', PUT: 'warning', PATCH: 'info' }
export default function Endpoints() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">External Endpoints</h4><p className="text-muted mb-0 fs-sm">Configure webhook URLs for external integrations</p></div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}><i className="bi bi-plus-lg me-1" /> Add Endpoint</button>
      </div>
      <div className="data-card"><div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Name</th><th>URL</th><th>Method</th><th>Status</th><th>Total Calls</th><th></th></tr></thead>
        <tbody>{endpoints.map((e) => (<tr key={e.id}>
          <td><code className="fw-semibold" style={{ color: '#1e293b' }}>{e.name}</code></td>
          <td className="text-muted" style={{ fontSize: '.8rem', maxWidth: 300 }}><span className="text-truncate d-block">{e.url}</span></td>
          <td><Badge bg={methodColors[e.method]} className="badge-status">{e.method}</Badge></td>
          <td><Badge bg={e.active ? 'success' : 'secondary'} className="badge-status">{e.active ? 'Active' : 'Inactive'}</Badge></td>
          <td style={{ fontSize: '.85rem' }}>{e.calls}</td>
          <td><Form.Check type="switch" checked={e.active} onChange={() => {}} id={`ep-${e.id}`} /></td>
        </tr>))}</tbody></table></div></div>
    </div>
  )
}
