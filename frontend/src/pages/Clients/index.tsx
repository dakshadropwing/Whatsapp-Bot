import { useState } from 'react'
import { Badge, Form, Row, Col, Modal, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { clientService } from '@services/clientService'
import toast from 'react-hot-toast'
import type { Client } from '@/types'

const tagColors: Record<string, string> = {
  enterprise: 'primary',
  startup: 'info',
  vip: 'warning',
  active: 'success',
  food: 'danger',
  health: 'success',
  ai: 'dark',
}

export default function Clients() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [company, setCompany] = useState('')
  const [tagsInput, setTagsInput] = useState('')

  // 1. Fetch Clients (dynamic query with search param)
  const { data, isLoading } = useQuery({
    queryKey: ['clients', search],
    queryFn: () => clientService.list({ search, per_page: 50 }),
  })

  // 2. Create Client Mutation
  const createMutation = useMutation({
    mutationFn: (newClient: Partial<Client>) => clientService.create(newClient),
    onSuccess: () => {
      toast.success('Client added successfully')
      setShowModal(false)
      setName('')
      setEmail('')
      setPhone('')
      setCompany('')
      setTagsInput('')
      qc.invalidateQueries({ queryKey: ['clients'] })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Failed to add client'
      toast.error(msg)
    },
  })

  // 3. Delete Client Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => clientService.delete(id),
    onSuccess: () => {
      toast.success('Client deleted successfully')
      qc.invalidateQueries({ queryKey: ['clients'] })
    },
    onError: () => toast.error('Failed to delete client'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name) {
      toast.error('Name is required')
      return
    }
    const tags = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0)

    createMutation.mutate({
      name,
      email: email || undefined,
      phone,
      company: company || undefined,
      tags,
    })
  }

  const clientsList = data?.data || []
  const totalClients = data?.total || 0

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Clients</h4>
          <p className="text-muted mb-0 fs-sm">Manage your customer database</p>
        </div>
        <div className="d-flex gap-2">
          <Form.Control
            size="sm"
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 220, borderRadius: '.5rem' }}
          />
          <button
            className="btn btn-sm text-white"
            onClick={() => setShowModal(true)}
            style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}
          >
            <i className="bi bi-plus-lg me-1" /> Add Client
          </button>
        </div>
      </div>

      {/* Stats Header (Dynamic counts based on query results) */}
      <Row className="g-3 mb-4">
        {[
          { label: 'Total Clients', value: totalClients, icon: 'bi-people', color: '#25d366' },
          { label: 'Enterprise Tagged', value: clientsList.filter((c: any) => c.tags?.includes('enterprise')).length, icon: 'bi-building', color: '#8b5cf6' },
          { label: 'VIP Tagged', value: clientsList.filter((c: any) => c.tags?.includes('vip')).length, icon: 'bi-gem', color: '#eab308' },
          { label: 'Active Status Tagged', value: clientsList.filter((c: any) => c.tags?.includes('active')).length, icon: 'bi-person-check', color: '#3b82f6' },
        ].map((s) => (
          <Col key={s.label} md={3}>
            <div className="stat-card">
              <div className="d-flex align-items-center gap-3">
                <div className="stat-icon" style={{ background: '#f0fdf4', color: s.color }}><i className={`bi ${s.icon}`} /></div>
                <div><div className="stat-value" style={{ fontSize: '1.4rem' }}>{s.value}</div><div className="stat-label">{s.label}</div></div>
              </div>
            </div>
          </Col>
        ))}
      </Row>

      {/* Table */}
      <div className="data-card">
        {isLoading ? (
          <div className="d-flex justify-content-center py-5">
            <div className="spinner-border text-success" role="status" />
          </div>
        ) : clientsList.length === 0 ? (
          <div className="text-center py-5 text-muted">No clients found. Click "Add Client" to create one.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead>
                <tr>
                  <th>Client Name</th>
                  <th>Contact Info</th>
                  <th>Company</th>
                  <th>Tags</th>
                  <th>Joined Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {clientsList.map((c: any) => (
                  <tr key={c.id}>
                    <td><div className="fw-semibold" style={{ fontSize: '.85rem' }}>{c.name}</div></td>
                    <td>
                      <div style={{ fontSize: '.85rem' }}>{c.phone}</div>
                      {c.email && <div className="text-muted" style={{ fontSize: '.7rem' }}>{c.email}</div>}
                    </td>
                    <td style={{ fontSize: '.85rem' }}>{c.company || '—'}</td>
                    <td>
                      <div className="d-flex gap-1 flex-wrap">
                        {c.tags && c.tags.length > 0 ? (
                          c.tags.map((tag: string) => (
                            <Badge key={tag} bg={tagColors[tag] || 'secondary'} className="badge-status">
                              {tag}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-muted fs-xs">—</span>
                        )}
                      </div>
                    </td>
                    <td className="text-muted" style={{ fontSize: '.8rem' }}>
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-light text-danger border-0 p-1"
                        title="Delete Client"
                        aria-label={`Delete client ${c.name}`}
                        onClick={() => {
                          if (confirm(`Are you sure you want to delete ${c.name}?`)) {
                            deleteMutation.mutate(c.id)
                          }
                        }}
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

      {/* Add Client Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Add New Client</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Client Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Acme Corporation"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Phone Number</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. +1 555-0100"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Email Address</Form.Label>
              <Form.Control
                type="email"
                placeholder="e.g. contact@acme.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Company Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Acme Corp"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Tags (comma separated)</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. enterprise, active, vip"
                value={tagsInput}
                onChange={(e) => setTagsInput(e.target.value)}
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
              {createMutation.isPending ? 'Saving...' : 'Add Client'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  )
}

