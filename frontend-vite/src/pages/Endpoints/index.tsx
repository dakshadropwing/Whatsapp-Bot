import { useState } from 'react'
import { Badge, Form, Modal, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { endpointService } from '@services/endpointService'
import toast from 'react-hot-toast'
import type { EndpointConfig } from '@/types'
import { PageWrapper } from '@components/PageWrapper'
const methodColors: Record<string, string> = {
  GET: 'success',
  POST: 'primary',
  PUT: 'warning',
  PATCH: 'info',
  DELETE: 'danger',
}

export default function Endpoints() {
  const qc = useQueryClient()
  const [showAddModal, setShowAddModal] = useState(false)
  const [showTestModal, setShowTestModal] = useState(false)
  const [testEndpointId, setTestEndpointId] = useState<string | null>(null)
  const [testPayload, setTestPayload] = useState('{\n  "test": true,\n  "event": "webhook_verification"\n}')
  const [testResult, setTestResult] = useState<any>(null)

  // Form states
  const [name, setName] = useState('')
  const [url, setUrl] = useState('')
  const [method, setMethod] = useState<'GET' | 'POST' | 'PUT' | 'PATCH'>('POST')
  const [description, setDescription] = useState('')
  const [headersInput, setHeadersInput] = useState('{\n  "Content-Type": "application/json"\n}')

  // 1. Fetch Endpoints
  const { data, isLoading } = useQuery({
    queryKey: ['endpoints'],
    queryFn: () => endpointService.list({ per_page: 100 }),
  })

  // 2. Create Endpoint Mutation
  const createMutation = useMutation({
    mutationFn: (newEp: Partial<EndpointConfig>) => endpointService.create(newEp),
    onSuccess: () => {
      toast.success('Endpoint integration added successfully')
      setShowAddModal(false)
      setName('')
      setUrl('')
      setMethod('POST')
      setDescription('')
      setHeadersInput('{\n  "Content-Type": "application/json"\n}')
      qc.invalidateQueries({ queryKey: ['endpoints'] })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Failed to add endpoint config'
      toast.error(msg)
    },
  })

  // 3. Toggle/Update Mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<EndpointConfig> }) =>
      endpointService.update(id, data),
    onSuccess: () => {
      toast.success('Endpoint config updated')
      qc.invalidateQueries({ queryKey: ['endpoints'] })
    },
    onError: () => toast.error('Failed to update endpoint config'),
  })

  // 4. Delete Endpoint Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => endpointService.delete(id),
    onSuccess: () => {
      toast.success('Endpoint configuration deleted')
      qc.invalidateQueries({ queryKey: ['endpoints'] })
    },
    onError: () => toast.error('Failed to delete endpoint config'),
  })

  // 5. Test Endpoint Mutation
  const testMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
      endpointService.test(id, payload),
    onSuccess: (data) => {
      setTestResult(data)
      toast.success(data.success ? 'Dispatch succeeded!' : 'Dispatch failed (check logs)')
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Test request failed'
      toast.error(msg)
    },
  })

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !url) {
      toast.error('Name and URL are required')
      return
    }

    let headers = {}
    try {
      if (headersInput.trim()) {
        headers = JSON.parse(headersInput)
      }
    } catch {
      toast.error('Invalid JSON in Headers input')
      return
    }

    createMutation.mutate({
      name,
      url,
      method,
      description: description || null,
      headers,
      is_active: true,
    })
  }

  const handleTestSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!testEndpointId) return

    let parsedPayload = {}
    try {
      if (testPayload.trim()) {
        parsedPayload = JSON.parse(testPayload)
      }
    } catch {
      toast.error('Invalid JSON in Test Payload')
      return
    }

    testMutation.mutate({
      id: testEndpointId,
      payload: parsedPayload,
    })
  }

  const openTestModal = (id: string) => {
    setTestEndpointId(id)
    setTestResult(null)
    setShowTestModal(true)
  }

  const endpointsList = data?.data || []

  return (
    <PageWrapper>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">External Endpoints</h4>
          <p className="text-muted mb-0 fs-sm">Configure webhook URLs for external integrations</p>
        </div>
        <button className="btn btn-wa-primary" onClick={() => setShowAddModal(true)} aria-label="Add integration webhook endpoint">
          <i className="bi bi-plus-lg me-1" /> Add Endpoint
        </button>
      </div>

      <div className="data-card">
        {isLoading ? (
          <div className="d-flex justify-content-center py-5">
            <div className="spinner-border text-success" role="status" />
          </div>
        ) : endpointsList.length === 0 ? (
          <div className="text-center py-5 text-muted">No integration endpoints configured. Click "Add Endpoint" to register one.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>URL</th>
                  <th>Method</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {endpointsList.map((e: any) => (
                  <tr key={e.id}>
                    <td>
                      <code className="fw-semibold" style={{ color: '#1e293b' }}>{e.name}</code>
                      {e.description && <div className="text-muted fs-xs mt-1">{e.description}</div>}
                    </td>
                    <td className="text-muted" style={{ fontSize: '.8rem', maxWidth: 300 }}>
                      <span className="text-truncate d-block">{e.url}</span>
                    </td>
                    <td>
                      <Badge bg={methodColors[e.method] || 'primary'} className="badge-status">
                        {e.method}
                      </Badge>
                    </td>
                    <td>
                      <Badge bg={e.is_active ? 'success' : 'secondary'} className="badge-status">
                        {e.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td>
                      <div className="d-flex align-items-center gap-2">
                        <Form.Check
                          type="switch"
                          checked={e.is_active}
                          onChange={() => updateMutation.mutate({ id: e.id, data: { is_active: !e.is_active } })}
                          id={`ep-${e.id}`}
                          aria-label={`Toggle active state for endpoint ${e.name}`}
                        />
                        <button
                          className="btn btn-sm btn-light"
                          onClick={() => openTestModal(e.id)}
                          title="Test dispatch"
                          aria-label={`Test endpoint ${e.name}`}
                        >
                          <i className="bi bi-play-fill" /> Test
                        </button>
                        <button
                          className="btn btn-sm btn-light text-danger"
                          onClick={() => {
                            if (confirm(`Are you sure you want to delete endpoint config "${e.name}"?`)) {
                              deleteMutation.mutate(e.id)
                            }
                          }}
                          aria-label={`Delete endpoint ${e.name}`}
                        >
                          <i className="bi bi-trash" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Endpoint Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Add Integration Endpoint</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreateSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Endpoint Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. crm_update"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">URL Target</Form.Label>
              <Form.Control
                type="url"
                placeholder="e.g. https://api.crm.com/v1/contacts"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">HTTP Method</Form.Label>
              <Form.Select
                value={method}
                onChange={(e) => setMethod(e.target.value as any)}
                style={{ borderRadius: '.5rem' }}
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="PATCH">PATCH</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Description (Optional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="Add custom notes..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Headers (JSON format)</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={headersInput}
                onChange={(e) => setHeadersInput(e.target.value)}
                style={{ borderRadius: '.5rem', fontFamily: 'monospace', fontSize: '.8rem' }}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowAddModal(false)} style={{ borderRadius: '.75rem' }}>Cancel</Button>
            <Button type="submit" className="btn-wa-primary" disabled={createMutation.isPending}>{createMutation.isPending ? 'Saving...' : 'Add Endpoint'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Test Endpoint Modal */}
      <Modal show={showTestModal} onHide={() => setShowTestModal(false)} centered size="lg">
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Test Webhook Endpoint Dispatch</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleTestSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Payload JSON</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={testPayload}
                onChange={(e) => setTestPayload(e.target.value)}
                style={{ borderRadius: '.5rem', fontFamily: 'monospace', fontSize: '.8rem' }}
              />
            </Form.Group>

            {testMutation.isPending && (
              <div className="text-center py-3">
                <div className="spinner-border text-success" role="status" />
                <div className="text-muted fs-xs mt-1">Dispatching webhook...</div>
              </div>
            )}

            {testResult && (
              <div className="mt-3">
                <h6 className="fw-semibold fs-sm">Dispatch Results:</h6>
                <div className="p-3 bg-light rounded" style={{ fontFamily: 'monospace', fontSize: '.8rem', maxHeight: 200, overflowY: 'auto' }}>
                  <div><strong>Success:</strong> {testResult.success ? '🟢 True' : '🔴 False'}</div>
                  <div><strong>Status Code:</strong> {testResult.status_code}</div>
                  <div className="mt-2"><strong>Response Body:</strong></div>
                  <pre className="mb-0 mt-1">{typeof testResult.response === 'object' ? JSON.stringify(testResult.response, null, 2) : testResult.response}</pre>
                </div>
              </div>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowTestModal(false)} style={{ borderRadius: '.75rem' }}>Close</Button>
            <Button type="submit" className="btn-wa-primary" disabled={testMutation.isPending}>Dispatch test</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </PageWrapper>
  )
}
