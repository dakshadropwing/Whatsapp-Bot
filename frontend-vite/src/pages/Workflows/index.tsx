import { useState } from 'react'
import { Row, Col, Badge, Form, Modal, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workflowService } from '@services/workflowService'
import toast from 'react-hot-toast'
import { PageWrapper } from '@components/PageWrapper'
import type { Workflow } from '@/types'

export default function Workflows() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)

  // Form states
  const [name, setName] = useState('')
  const [trigger, setTrigger] = useState('')
  const [description, setDescription] = useState('')

  // 1. Fetch Workflows
  const { data, isLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => workflowService.list({ per_page: 100 }),
  })

  // 2. Toggle Status Mutation
  const toggleMutation = useMutation({
    mutationFn: (id: string) => workflowService.toggle(id),
    onSuccess: () => {
      toast.success('Workflow status updated')
      qc.invalidateQueries({ queryKey: ['workflows'] })
    },
    onError: () => toast.error('Failed to update workflow status'),
  })

  // 3. Create Workflow Mutation
  const createMutation = useMutation({
    mutationFn: (newWf: Partial<Workflow>) => workflowService.create(newWf),
    onSuccess: () => {
      toast.success('Workflow created successfully')
      setShowModal(false)
      setName('')
      setTrigger('')
      setDescription('')
      qc.invalidateQueries({ queryKey: ['workflows'] })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Failed to create workflow'
      toast.error(msg)
    },
  })

  // 4. Delete Workflow Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => workflowService.delete(id),
    onSuccess: () => {
      toast.success('Workflow deleted successfully')
      qc.invalidateQueries({ queryKey: ['workflows'] })
    },
    onError: () => toast.error('Failed to delete workflow'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !trigger) {
      toast.error('Name and Trigger are required')
      return
    }
    createMutation.mutate({
      name,
      trigger,
      description,
      steps: [], // default empty steps array
      is_active: true,
    })
  }

  const workflowsList = data?.data || []

  return (
    <PageWrapper>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Workflows</h4>
          <p className="text-muted mb-0 fs-sm">Automate multi-step processes and triggers</p>
        </div>
        <button className="btn btn-wa-primary" onClick={() => setShowModal(true)} aria-label="Create new workflow">
          <i className="bi bi-plus-lg me-1" /> New Workflow
        </button>
      </div>

      {isLoading ? (
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-success" role="status" />
        </div>
      ) : workflowsList.length === 0 ? (
        <div className="text-center py-5 text-muted">No workflows configured. Click "New Workflow" to get started.</div>
      ) : (
        <Row className="g-3 stagger-children">
          {workflowsList.map((w: any) => (
            <Col key={w.id} xl={4} md={6}>
              <div className="data-card h-100">
                <div className="data-card-body d-flex flex-column justify-content-between">
                  <div>
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <div>
                        <div className="fw-semibold mb-1" style={{ fontSize: '.95rem' }}>{w.name}</div>
                        <div className="text-muted fs-xs">
                          <i className="bi bi-lightning me-1" /> {w.trigger}
                        </div>
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <Form.Check
                          type="switch"
                          checked={w.is_active}
                          onChange={() => toggleMutation.mutate(w.id)}
                          id={`wf-${w.id}`}
                          aria-label={`Toggle active state for ${w.name}`}
                        />
                        <button
                          className="btn btn-sm btn-light text-danger border-0 p-1"
                          onClick={() => {
                            if (confirm(`Are you sure you want to delete workflow "${w.name}"?`)) {
                              deleteMutation.mutate(w.id)
                            }
                          }}
                          aria-label={`Delete workflow ${w.name}`}
                        >
                          <i className="bi bi-trash" />
                        </button>
                      </div>
                    </div>
                    {w.description && (
                      <p className="text-muted mb-3" style={{ fontSize: '.8rem' }}>
                        {w.description}
                      </p>
                    )}
                  </div>
                  <div className="d-flex gap-3 pt-2 align-items-center" style={{ borderTop: '1px solid var(--border-color)' }}>
                    <div>
                      <span className="fw-bold">{w.steps?.length || 0}</span> <span className="text-muted fs-xs">steps</span>
                    </div>
                    <div>
                      <span className="fw-bold">{w.run_count || 0}</span> <span className="text-muted fs-xs">executions</span>
                    </div>
                    <Badge bg={w.is_active ? 'success' : 'secondary'} className="badge-status ms-auto">
                      {w.is_active ? 'Active' : 'Paused'}
                    </Badge>
                  </div>
                </div>
              </div>
            </Col>
          ))}
        </Row>
      )}

      {/* Create Workflow Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Create New Workflow</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Workflow Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Appointment Booking"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Trigger Name / Event</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Keyword: 'book', Priority: urgent"
                value={trigger}
                onChange={(e) => setTrigger(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Describe what this workflow automates..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowModal(false)} style={{ borderRadius: '.75rem' }}>Cancel</Button>
            <Button type="submit" className="btn-wa-primary" disabled={createMutation.isPending}>{createMutation.isPending ? 'Saving...' : 'Create Workflow'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </PageWrapper>
  )
}
