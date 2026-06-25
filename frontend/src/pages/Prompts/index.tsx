import { useState } from 'react'
import { Badge, Modal, Form, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { promptService } from '@services/promptService'
import toast from 'react-hot-toast'
import type { PromptTemplate } from '@/types'

const catColors: Record<string, string> = {
  agents: 'primary',
  templates: 'info',
  system: 'dark',
}

export default function Prompts() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)

  // Form states
  const [name, setName] = useState('')
  const [category, setCategory] = useState('agents')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [userPrompt, setUserPrompt] = useState('')
  const [variablesInput, setVariablesInput] = useState('')

  // 1. Fetch Prompts
  const { data, isLoading } = useQuery({
    queryKey: ['prompts'],
    queryFn: () => promptService.list({ per_page: 100 }),
  })

  // 2. Create Prompt Mutation
  const createMutation = useMutation({
    mutationFn: (newPrompt: Partial<PromptTemplate>) => promptService.create(newPrompt),
    onSuccess: () => {
      toast.success('Prompt template created successfully')
      setShowModal(false)
      setName('')
      setCategory('agents')
      setSystemPrompt('')
      setUserPrompt('')
      setVariablesInput('')
      qc.invalidateQueries({ queryKey: ['prompts'] })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Failed to create prompt template'
      toast.error(msg)
    },
  })

  // 3. Delete Prompt Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => promptService.delete(id),
    onSuccess: () => {
      toast.success('Prompt template deleted successfully')
      qc.invalidateQueries({ queryKey: ['prompts'] })
    },
    onError: () => toast.error('Failed to delete prompt template'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !systemPrompt) {
      toast.error('Name and System Prompt are required')
      return
    }
    const variables = variablesInput
      .split(',')
      .map((v) => v.trim())
      .filter((v) => v.length > 0)

    createMutation.mutate({
      name,
      category,
      system_prompt: systemPrompt,
      user_prompt: userPrompt || undefined,
      variables,
    })
  }

  const promptsList = data?.data || []

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Prompt Templates</h4>
          <p className="text-muted mb-0 fs-sm">Manage AI system prompts and message templates</p>
        </div>
        <button
          className="btn btn-sm text-white"
          onClick={() => setShowModal(true)}
          style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}
          aria-label="Create new prompt template"
        >
          <i className="bi bi-plus-lg me-1" /> New Prompt
        </button>
      </div>

      <div className="data-card">
        {isLoading ? (
          <div className="d-flex justify-content-center py-5">
            <div className="spinner-border text-success" role="status" />
          </div>
        ) : promptsList.length === 0 ? (
          <div className="text-center py-5 text-muted">No prompt templates found. Click "New Prompt" to get started.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Category</th>
                  <th>System Prompt</th>
                  <th>Variables</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {promptsList.map((p: any) => (
                  <tr key={p.id}>
                    <td className="fw-semibold" style={{ fontSize: '.85rem' }}>{p.name}</td>
                    <td>
                      <Badge bg={catColors[p.category] || 'secondary'} className="badge-status">
                        {p.category}
                      </Badge>
                    </td>
                    <td style={{ fontSize: '.8rem', maxWidth: 300 }} className="text-truncate">
                      {p.system_prompt}
                    </td>
                    <td>
                      <div className="d-flex gap-1 flex-wrap">
                        {p.variables && p.variables.length > 0 ? (
                          p.variables.map((v: string) => (
                            <code
                              key={v}
                              className="text-wa-green"
                              style={{ fontSize: '.7rem', background: '#f0fdf4', padding: '1px 6px', borderRadius: 4 }}
                            >
                              {v}
                            </code>
                          ))
                        ) : (
                          <span className="text-muted fs-xs">—</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-light text-danger"
                        onClick={() => {
                          if (confirm(`Are you sure you want to delete prompt template "${p.name}"?`)) {
                            deleteMutation.mutate(p.id)
                          }
                        }}
                        aria-label={`Delete prompt ${p.name}`}
                      >
                        <i className="bi bi-trash" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Prompt Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">New Prompt Template</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Prompt Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Lead Qualification"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Category</Form.Label>
              <Form.Select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              >
                <option value="agents">Agents</option>
                <option value="templates">Templates</option>
                <option value="system">System</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">System Prompt</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                placeholder="You are a helpful assistant..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">User Prompt (Optional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="Customer details: {{customer_name}}"
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Template Variables (comma separated)</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. customer_name, company, date"
                value={variablesInput}
                onChange={(e) => setVariablesInput(e.target.value)}
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
              {createMutation.isPending ? 'Saving...' : 'Create Prompt'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  )
}
