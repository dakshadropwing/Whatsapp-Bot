import { useState } from 'react'
import { Row, Col, Badge, Form, Modal, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService } from '@services/agentService'
import toast from 'react-hot-toast'
import type { Agent, AgentType } from '@/types'

const typeIcons: Record<string, string> = {
  support: 'bi-headset',
  sales: 'bi-cart-check',
  lead: 'bi-funnel',
  project: 'bi-kanban',
  hr: 'bi-person-workspace',
  knowledge: 'bi-book',
  appointment: 'bi-calendar-check',
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

  // 1. Fetch Agents
  const { data, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentService.list({ per_page: 50 }),
  })

  // 2. Toggle Status Mutation
  const toggleMutation = useMutation({
    mutationFn: (id: string) => agentService.toggle(id),
    onSuccess: () => {
      toast.success('Agent status updated')
      qc.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => toast.error('Failed to toggle status'),
  })

  // 3. Create Agent Mutation
  const createMutation = useMutation({
    mutationFn: (newAgent: Partial<Agent>) => agentService.create(newAgent),
    onSuccess: () => {
      toast.success('Agent created successfully')
      setShowModal(false)
      setName('')
      setRoleType('support')
      setSystemPrompt('')
      qc.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => toast.error('Failed to create agent'),
  })

  // 4. Delete Agent Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => agentService.delete(id),
    onSuccess: () => {
      toast.success('Agent deleted successfully')
      qc.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => toast.error('Failed to delete agent'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !systemPrompt) {
      toast.error('Please fill in all required fields')
      return
    }
    createMutation.mutate({
      name,
      role_type: roleType,
      system_prompt: systemPrompt,
      provider: 'gemini',
      model_name: 'gemini-2.5-flash',
      is_active: true,
    })
  }

  const agentsList = data?.data || []

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">AI Agents</h4>
          <p className="text-muted mb-0 fs-sm">Configure and manage your AI specialist agents</p>
        </div>
        <button
          className="btn btn-sm text-white"
          onClick={() => setShowModal(true)}
          style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}
        >
          <i className="bi bi-plus-lg me-1" /> New Agent
        </button>
      </div>

      {isLoading ? (
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-success" role="status" />
        </div>
      ) : agentsList.length === 0 ? (
        <div className="text-center py-5 text-muted">No agents configured. Click "New Agent" to get started.</div>
      ) : (
        <Row className="g-3">
          {agentsList.map((agent: any) => {
            const roleType = agent.role_type || agent.type || 'support'
            const systemPrompt = agent.system_prompt || agent.description || ''
            return (
              <Col key={agent.id} xl={4} md={6}>
                <div className="data-card h-100">
                  <div className="data-card-body">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <div className="d-flex align-items-center gap-3">
                        <div
                          className="stat-icon"
                          style={{
                            background: agent.is_active ? '#f0fdf4' : '#f8fafc',
                            color: agent.is_active ? '#25d366' : '#94a3b8',
                            width: 44,
                            height: 44,
                            borderRadius: '.5rem',
                          }}
                        >
                          <i className={`bi ${typeIcons[roleType] || 'bi-robot'}`} style={{ fontSize: '1.25rem' }} />
                        </div>
                        <div>
                          <div className="fw-semibold" style={{ fontSize: '.95rem' }}>{agent.name}</div>
                          <Badge bg={agent.is_active ? 'success' : 'secondary'} className="badge-status">
                            {agent.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <Form.Check
                          type="switch"
                          checked={agent.is_active}
                          onChange={() => toggleMutation.mutate(agent.id)}
                          id={`switch-${agent.id}`}
                          aria-label={`Toggle active status for ${agent.name}`}
                        />
                        <button
                          className="btn btn-sm btn-light text-danger border-0 p-1"
                          title="Delete Agent"
                          aria-label={`Delete agent ${agent.name}`}
                          onClick={() => {
                            if (confirm(`Are you sure you want to delete ${agent.name}?`)) {
                              deleteMutation.mutate(agent.id)
                            }
                          }}
                        >
                          <i className="bi bi-trash" />
                        </button>
                      </div>
                    </div>
                    <p className="text-muted mb-3" style={{ fontSize: '.83rem' }}>
                      {typeDescriptions[roleType] || systemPrompt.substring(0, 100) + '...'}
                    </p>
                    <div className="d-flex gap-3 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
                      <div>
                        <div className="fw-bold" style={{ fontSize: '1.1rem' }}>{roleType.toUpperCase()}</div>
                        <div className="text-muted" style={{ fontSize: '.7rem' }}>Role Type</div>
                      </div>
                      <div>
                        <div className="fw-bold text-wa-green" style={{ fontSize: '1.1rem' }}>Gemini</div>
                        <div className="text-muted" style={{ fontSize: '.7rem' }}>AI Model</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Col>
            )
          })}
        </Row>
      )}

      {/* Create Agent Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Create New Agent</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Agent Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Sales Assistant"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Role/Type</Form.Label>
              <Form.Select
                value={roleType}
                onChange={(e) => setRoleType(e.target.value as AgentType)}
                style={{ borderRadius: '.5rem' }}
              >
                <option value="support">Customer Support (Aria)</option>
                <option value="sales">Sales Assistant</option>
                <option value="lead">Lead Qualification</option>
                <option value="project">Project Manager</option>
                <option value="hr">HR Assistant</option>
                <option value="knowledge">RAG Knowledge Q&A</option>
                <option value="appointment">Appointment Scheduler</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">System Prompt</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                placeholder="Define the behavior, instructions, and rules for the AI agent..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowModal(false)} style={{ borderRadius: '.5rem' }}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="success"
              style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', border: 'none', borderRadius: '.5rem' }}
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Saving...' : 'Create Agent'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  )
}

