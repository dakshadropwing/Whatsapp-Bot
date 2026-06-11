import { Row, Col, Badge, Form } from 'react-bootstrap'
const workflows = [
  { id: '1', name: 'Lead Qualification', trigger: 'New contact message', steps: 4, active: true, executions: 234 },
  { id: '2', name: 'Follow-up Sequence', trigger: 'After 24h no reply', steps: 3, active: true, executions: 156 },
  { id: '3', name: 'Appointment Booking', trigger: 'Keyword: "book"', steps: 5, active: true, executions: 89 },
  { id: '4', name: 'Support Escalation', trigger: 'Priority: urgent', steps: 3, active: false, executions: 45 },
  { id: '5', name: 'Onboarding Flow', trigger: 'New client registered', steps: 6, active: true, executions: 67 },
]
export default function Workflows() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Workflows</h4><p className="text-muted mb-0 fs-sm">Automate multi-step processes and triggers</p></div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}><i className="bi bi-plus-lg me-1" /> New Workflow</button>
      </div>
      <Row className="g-3">{workflows.map((w) => (
        <Col key={w.id} xl={4} md={6}><div className="data-card h-100"><div className="data-card-body">
          <div className="d-flex justify-content-between align-items-start mb-3">
            <div><div className="fw-semibold mb-1">{w.name}</div><div className="text-muted fs-xs"><i className="bi bi-lightning me-1" />{w.trigger}</div></div>
            <Form.Check type="switch" checked={w.active} onChange={() => {}} id={`wf-${w.id}`} />
          </div>
          <div className="d-flex gap-3 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
            <div><span className="fw-bold">{w.steps}</span> <span className="text-muted fs-xs">steps</span></div>
            <div><span className="fw-bold">{w.executions}</span> <span className="text-muted fs-xs">executions</span></div>
            <Badge bg={w.active ? 'success' : 'secondary'} className="badge-status ms-auto">{w.active ? 'Active' : 'Paused'}</Badge>
          </div>
        </div></div></Col>
      ))}</Row>
    </div>
  )
}
