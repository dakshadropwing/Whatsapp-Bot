import { Badge } from 'react-bootstrap'
const prompts = [
  { id: '1', name: 'Lead Qualification', category: 'agents', system: 'You are a lead qualification specialist...', vars: ['customer_name', 'company'], updated: '2 days ago' },
  { id: '2', name: 'Support FAQ', category: 'agents', system: 'You are a helpful support agent...', vars: ['knowledge_context'], updated: '1 week ago' },
  { id: '3', name: 'Follow-up Reminder', category: 'templates', system: 'Send a friendly follow-up...', vars: ['customer_name', 'days_since'], updated: '3 days ago' },
  { id: '4', name: 'Appointment Confirmation', category: 'templates', system: 'Confirm the appointment details...', vars: ['date', 'time', 'service'], updated: '5 days ago' },
]
const catColors: Record<string, string> = { agents: 'primary', templates: 'info', system: 'dark' }
export default function Prompts() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Prompt Templates</h4><p className="text-muted mb-0 fs-sm">Manage AI system prompts and message templates</p></div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}><i className="bi bi-plus-lg me-1" /> New Prompt</button>
      </div>
      <div className="data-card"><div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Name</th><th>Category</th><th>System Prompt</th><th>Variables</th><th>Updated</th></tr></thead>
        <tbody>{prompts.map((p) => (<tr key={p.id}>
          <td className="fw-semibold" style={{ fontSize: '.85rem' }}>{p.name}</td>
          <td><Badge bg={catColors[p.category] || 'secondary'} className="badge-status">{p.category}</Badge></td>
          <td style={{ fontSize: '.8rem', maxWidth: 300 }} className="text-truncate">{p.system}</td>
          <td><div className="d-flex gap-1 flex-wrap">{p.vars.map((v) => <code key={v} className="text-wa-green" style={{ fontSize: '.7rem', background: '#f0fdf4', padding: '1px 6px', borderRadius: 4 }}>{v}</code>)}</div></td>
          <td className="text-muted" style={{ fontSize: '.8rem' }}>{p.updated}</td>
        </tr>))}</tbody></table></div></div>
    </div>
  )
}
