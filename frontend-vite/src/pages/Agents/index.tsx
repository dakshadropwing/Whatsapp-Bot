import { useState } from 'react'
import { Row, Col, Badge, Form, Modal, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService } from '@services/agentService'
import toast from 'react-hot-toast'
import type { Agent, AgentType } from '@/types'
import { PageWrapper } from '@components/PageWrapper'
const typeIcons: Record<string, string> = {
  support: 'bi-headset', sales: 'bi-cart-check', lead: 'bi-funnel',
  project: 'bi-kanban', hr: 'bi-person-workspace', knowledge: 'bi-book', appointment: 'bi-calendar-check',
}

const typeColors: Record<string, string> = {
  support: '#25d366', sales: '#3b82f6', lead: '#8b5cf6',
  project: '#f59e0b', hr: '#ec4899', knowledge: '#06b6d4', appointment: '#10b981',
}

const typeDescriptions: Record<string, string> = {
  support: 'Handles customer support queries, FAQ, ticket creation, and escalation.',
  sales: 'Product catalog, pricing, recommendations, and upselling.',
  lead: 'Lead qualification, scoring, CRM integration, and follow-ups.',
  project: 'Project/task tracking, status updates, and sprint management.',
  hr: 'HR policy lookup, leave balance, onboarding assistance.',
  knowledge: 'RAG-powered knowledge base Q&A with document search.',
  appointment: 'Appointment scheduling, calendar management, and reminders.',
}

export default function Agents() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [roleType, setRoleType] = useState<AgentType>('support')
  const [systemPrompt, setSystemPrompt] = useState('')

  const { data, isLoading } = useQuery({ queryKey: ['agents'], queryFn: () => agentService.list({ per_page: 50 }) })

  const toggleMutation = useMutation({
    mutationFn: (id: string) => agentService.toggle(id),
    onSuccess: () => { toast.success('Agent status updated'); qc.invalidateQueries({ queryKey: ['agents'] }) },
    onError: () => toast.error('Failed to toggle status'),
  })

  const createMutation = useMutation({
    mutationFn: (newAgent: Partial<Agent>) => agentService.create(newAgent),
    onSuccess: () => { toast.success('Agent created'); setShowModal(false); setName(''); setRoleType('support'); setSystemPrompt(''); qc.invalidateQueries({ queryKey: ['agents'] }) },
    onError: () => toast.error('Failed to create agent'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => agentService.delete(id),
    onSuccess: () => { toast.success('Agent deleted'); qc.invalidateQueries({ queryKey: ['agents'] }) },
    onError: () => toast.error('Failed to delete agent'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !systemPrompt) { toast.error('Please fill in all required fields'); return }
    createMutation.mutate({ name, role_type: roleType, system_prompt: systemPrompt, provider: 'gemini', model_name: 'gemini-2.5-flash', is_active: true })
  }

  const agentsList = data?.data || []

  return (
    <PageWrapper>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">AI Agents</h4>
          <p className="text-muted mb-0 fs-sm">Configure and manage your AI specialist agents</p>
        </div>
        <button className="btn btn-wa-primary" onClick={() => setShowModal(true)}><i className="bi bi-plus-lg me-1" /> New Agent</button>
      </div>

      {isLoading ? (
        <div className="d-flex justify-content-center py-5"><div className="spinner-border text-success" role="status" /></div>
      ) : agentsList.length === 0 ? (
        <div className="text-center py-5" style={{ color: 'var(--text-muted)' }}>No agents configured. Click "New Agent" to get started.</div>
      ) : (
        <Row className="g-3 stagger-children">
          {agentsList.map((agent: any) => {
            const rt = agent.role_type || agent.type || 'support'
            const color = typeColors[rt] || '#25d366'
            return (
              <Col key={agent.id} xl={4} md={6}>
                <div className="data-card h-100">
                  <div className="data-card-body">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <div className="d-flex align-items-center gap-3">
                        <div style={{
                          width: 44, height: 44, borderRadius: 'var(--radius)',
                          background: `${color}15`, color,
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem',
                        }}>
                          <i className={`bi ${typeIcons[rt] || 'bi-robot'}`} />
                        </div>
                        <div>
                          <div className="fw-semibold" style={{ fontSize: '.95rem' }}>{agent.name}</div>
                          <Badge bg={agent.is_active ? 'success' : 'secondary'} className="badge-status">{agent.is_active ? 'Active' : 'Inactive'}</Badge>
                        </div>
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <Form.Check type="switch" checked={agent.is_active} onChange={() => toggleMutation.mutate(agent.id)} id={`switch-${agent.id}`} aria-label={`Toggle ${agent.name}`} />
                        <button className="btn btn-sm btn-light text-danger p-1" onClick={() => { if (confirm(`Delete ${agent.name}?`)) deleteMutation.mutate(agent.id) }} aria-label={`Delete ${agent.name}`}>
                          <i className="bi bi-trash" />
                        </button>
                      </div>
                    </div>
                    <p style={{ fontSize: '.83rem', color: 'var(--text-muted)' }} className="mb-3">{typeDescriptions[rt] || (agent.system_prompt || '').substring(0, 100) + '...'}</p>
                    <div className="d-flex gap-3 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
                      <div>
                        <div className="fw-bold" style={{ fontSize: '1rem', color }}>{rt.toUpperCase()}</div>
                        <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>Role Type</div>
                      </div>
                      <div>
                        <div className="fw-bold text-wa-green" style={{ fontSize: '1rem' }}>Gemini</div>
                        <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>AI Model</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Col>
            )
          })}
        </Row>
      )}

      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton><Modal.Title className="fw-bold fs-5">Create New Agent</Modal.Title></Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Agent Name</Form.Label>
              <Form.Control type="text" placeholder="e.g. Sales Assistant" value={name} onChange={(e) => setName(e.target.value)} required style={{ borderRadius: '.75rem' }} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Role/Type</Form.Label>
              <Form.Select value={roleType} onChange={(e) => setRoleType(e.target.value as AgentType)} style={{ borderRadius: '.75rem' }}>
                <option value="support">Customer Support</option><option value="sales">Sales Assistant</option><option value="lead">Lead Qualification</option>
                <option value="project">Project Manager</option><option value="hr">HR Assistant</option><option value="knowledge">RAG Knowledge Q&A</option><option value="appointment">Appointment Scheduler</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">System Prompt</Form.Label>
              <Form.Control as="textarea" rows={4} placeholder="Define the behavior..." value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)} required style={{ borderRadius: '.75rem' }} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowModal(false)} style={{ borderRadius: '.75rem' }}>Cancel</Button>
            <Button type="submit" className="btn-wa-primary" disabled={createMutation.isPending}>{createMutation.isPending ? 'Saving...' : 'Create Agent'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </PageWrapper>
  )
}
