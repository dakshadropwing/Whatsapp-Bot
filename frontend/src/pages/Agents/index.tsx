import { Row, Col, Badge, Form } from 'react-bootstrap'

const agents = [
  { id: '1', name: 'Support Agent', type: 'support', icon: 'bi-headset', description: 'Handles customer support queries, FAQ, ticket creation, and escalation.', active: true, conversations: 342, resolution: '94%' },
  { id: '2', name: 'Sales Agent', type: 'sales', icon: 'bi-cart-check', description: 'Product catalog, pricing, recommendations, and upselling.', active: true, conversations: 215, resolution: '88%' },
  { id: '3', name: 'Lead Agent', type: 'lead', icon: 'bi-funnel', description: 'Lead qualification, scoring, CRM integration, and follow-ups.', active: true, conversations: 180, resolution: '82%' },
  { id: '4', name: 'Project Agent', type: 'project', icon: 'bi-kanban', description: 'Project/task tracking, status updates, and sprint management.', active: false, conversations: 95, resolution: '90%' },
  { id: '5', name: 'HR Agent', type: 'hr', icon: 'bi-person-workspace', description: 'HR policy lookup, leave balance, onboarding assistance.', active: true, conversations: 72, resolution: '96%' },
  { id: '6', name: 'Knowledge Agent', type: 'knowledge', icon: 'bi-book', description: 'RAG-powered knowledge base Q&A with document search.', active: true, conversations: 156, resolution: '91%' },
  { id: '7', name: 'Appointment Agent', type: 'appointment', icon: 'bi-calendar-check', description: 'Appointment scheduling, calendar management, and reminders.', active: false, conversations: 89, resolution: '85%' },
]

export default function Agents() {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">AI Agents</h4>
          <p className="text-muted mb-0 fs-sm">Configure and manage your AI specialist agents</p>
        </div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}>
          <i className="bi bi-plus-lg me-1" /> New Agent
        </button>
      </div>

      <Row className="g-3">
        {agents.map((agent) => (
          <Col key={agent.id} xl={4} md={6}>
            <div className="data-card h-100">
              <div className="data-card-body">
                <div className="d-flex justify-content-between align-items-start mb-3">
                  <div className="d-flex align-items-center gap-3">
                    <div className="stat-icon" style={{ background: agent.active ? '#f0fdf4' : '#f8fafc', color: agent.active ? '#25d366' : '#94a3b8', width: 44, height: 44, borderRadius: '.5rem' }}>
                      <i className={`bi ${agent.icon}`} style={{ fontSize: '1.25rem' }} />
                    </div>
                    <div>
                      <div className="fw-semibold" style={{ fontSize: '.95rem' }}>{agent.name}</div>
                      <Badge bg={agent.active ? 'success' : 'secondary'} className="badge-status">{agent.active ? 'Active' : 'Inactive'}</Badge>
                    </div>
                  </div>
                  <Form.Check
                    type="switch"
                    checked={agent.active}
                    onChange={() => {}}
                    id={`switch-${agent.id}`}
                  />
                </div>
                <p className="text-muted mb-3" style={{ fontSize: '.83rem' }}>{agent.description}</p>
                <div className="d-flex gap-3 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
                  <div>
                    <div className="fw-bold" style={{ fontSize: '1.1rem' }}>{agent.conversations}</div>
                    <div className="text-muted" style={{ fontSize: '.7rem' }}>Conversations</div>
                  </div>
                  <div>
                    <div className="fw-bold text-wa-green" style={{ fontSize: '1.1rem' }}>{agent.resolution}</div>
                    <div className="text-muted" style={{ fontSize: '.7rem' }}>Resolution</div>
                  </div>
                </div>
              </div>
            </div>
          </Col>
        ))}
      </Row>
    </div>
  )
}
