import { useState } from 'react'
import { Badge, Dropdown, Modal, Form, Button, Row, Col } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ticketService } from '@services/ticketService'
import toast from 'react-hot-toast'
import { PageWrapper } from '@components/PageWrapper'
import type { Ticket, TicketStatus, TicketPriority } from '@/types'

const priorityColors: Record<string, string> = { low: 'secondary', medium: 'info', high: 'warning', urgent: 'danger' }
const statusColors: Record<string, string> = { open: 'success', in_progress: 'primary', waiting_on_customer: 'warning', resolved: 'secondary', closed: 'dark' }

export default function Tickets() {
  const qc = useQueryClient()
  const [filter, setFilter] = useState('all')
  const [showModal, setShowModal] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<TicketPriority>('medium')
  const [contactName, setContactName] = useState('')
  const [contactPhone, setContactPhone] = useState('')

  const { data, isLoading } = useQuery({ queryKey: ['tickets', filter], queryFn: () => ticketService.list({ status: filter === 'all' ? undefined : filter, per_page: 100 }) })

  const createMutation = useMutation({
    mutationFn: (t: Partial<Ticket>) => ticketService.create(t),
    onSuccess: () => { toast.success('Ticket created'); setShowModal(false); setTitle(''); setDescription(''); setPriority('medium'); setContactName(''); setContactPhone(''); qc.invalidateQueries({ queryKey: ['tickets'] }) },
    onError: (err: any) => toast.error(err?.response?.data?.error || 'Failed to create ticket'),
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: TicketStatus }) => ticketService.updateStatus(id, status),
    onSuccess: () => { toast.success('Status updated'); qc.invalidateQueries({ queryKey: ['tickets'] }) },
    onError: () => toast.error('Failed to update status'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => ticketService.delete(id),
    onSuccess: () => { toast.success('Ticket deleted'); qc.invalidateQueries({ queryKey: ['tickets'] }) },
    onError: () => toast.error('Failed to delete ticket'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title) { toast.error('Title is required'); return }
    createMutation.mutate({ title, description: description || undefined, priority, contact_name: contactName || undefined, contact_phone: contactPhone || undefined })
  }

  const ticketsList = data?.data || []

  return (
    <PageWrapper>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Support Tickets</h4><p className="text-muted mb-0 fs-sm">Track and manage customer support tickets</p></div>
        <button className="btn btn-wa-primary" onClick={() => setShowModal(true)} aria-label="Create new support ticket"><i className="bi bi-plus-lg me-1" /> New Ticket</button>
      </div>

      <div className="d-flex gap-2 mb-3 flex-wrap">
        {['all', 'open', 'in_progress', 'waiting_on_customer', 'resolved', 'closed'].map((f) => (
          <button key={f} className="btn btn-sm" style={{
            fontSize: '.78rem', borderRadius: '1rem', padding: '.3rem .9rem',
            background: filter === f ? 'linear-gradient(135deg, #25d366, #128c7e)' : 'rgba(255,255,255,.05)',
            color: filter === f ? '#fff' : 'var(--text-muted)', border: filter === f ? 'none' : '1px solid var(--border-color)',
          }} onClick={() => setFilter(f)} aria-label={`Filter by ${f}`}>
            {f === 'all' ? 'All' : f.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </button>
        ))}
      </div>

      <div className="data-card">
        {isLoading ? (
          <div className="d-flex justify-content-center py-5"><div className="spinner-border text-success" role="status" /></div>
        ) : ticketsList.length === 0 ? (
          <div className="text-center py-5" style={{ color: 'var(--text-muted)' }}>No tickets found.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead><tr><th>Ticket</th><th>Contact</th><th>Priority</th><th>Status</th><th>Created</th><th aria-label="Actions"></th></tr></thead>
              <tbody>
                {ticketsList.map((t: any) => (
                  <tr key={t.id}>
                    <td>
                      <div className="fw-semibold" style={{ fontSize: '.85rem' }}>#{t.id.substring(0, 8)} {t.title}</div>
                      {t.description && <div className="text-truncate" style={{ fontSize: '.72rem', maxWidth: 300, color: 'var(--text-muted)' }}>{t.description}</div>}
                    </td>
                    <td>
                      <div style={{ fontSize: '.85rem' }}>{t.contact_name || '—'}</div>
                      <div style={{ fontSize: '.7rem', color: 'var(--text-muted)' }}>{t.contact_phone || '—'}</div>
                    </td>
                    <td><Badge bg={priorityColors[t.priority] || 'secondary'} className="badge-status">{t.priority}</Badge></td>
                    <td><Badge bg={statusColors[t.status] || 'secondary'} className="badge-status">{t.status.replace(/_/g, ' ')}</Badge></td>
                    <td style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>{t.created_at ? new Date(t.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '—'}</td>
                    <td>
                      <Dropdown align="end">
                        <Dropdown.Toggle as="button" className="btn btn-sm btn-light border-0" aria-label={`Actions for ${t.id.substring(0, 8)}`}><i className="bi bi-three-dots" /></Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Header>Change Status</Dropdown.Header>
                          {['open', 'in_progress', 'waiting_on_customer', 'resolved', 'closed'].map((st) => (
                            <Dropdown.Item key={st} active={t.status === st} onClick={() => updateStatusMutation.mutate({ id: t.id, status: st as TicketStatus })}>
                              {st.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                            </Dropdown.Item>
                          ))}
                          <Dropdown.Divider />
                          <Dropdown.Item className="text-danger" onClick={() => { if (confirm(`Delete "${t.title}"?`)) deleteMutation.mutate(t.id) }}>
                            <i className="bi bi-trash me-2" /> Delete
                          </Dropdown.Item>
                        </Dropdown.Menu>
                      </Dropdown>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton><Modal.Title className="fw-bold fs-5">New Support Ticket</Modal.Title></Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3"><Form.Label className="fw-semibold fs-sm">Ticket Title</Form.Label><Form.Control type="text" placeholder="e.g. Cannot process payment" value={title} onChange={(e) => setTitle(e.target.value)} required style={{ borderRadius: '.75rem' }} /></Form.Group>
            <Form.Group className="mb-3"><Form.Label className="fw-semibold fs-sm">Description</Form.Label><Form.Control as="textarea" rows={3} placeholder="Details..." value={description} onChange={(e) => setDescription(e.target.value)} style={{ borderRadius: '.75rem' }} /></Form.Group>
            <Row className="mb-3"><Form.Group as={Col} md={6}><Form.Label className="fw-semibold fs-sm">Priority</Form.Label><Form.Select value={priority} onChange={(e) => setPriority(e.target.value as TicketPriority)} style={{ borderRadius: '.75rem' }}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="urgent">Urgent</option></Form.Select></Form.Group></Row>
            <hr style={{ borderColor: 'var(--border-color)' }} />
            <h6 className="fw-bold mb-3 fs-xs text-uppercase" style={{ letterSpacing: '.04em', color: 'var(--text-muted)' }}>Customer Contact</h6>
            <Row>
              <Form.Group as={Col} md={6} className="mb-3"><Form.Label className="fw-semibold fs-sm">Name</Form.Label><Form.Control type="text" placeholder="John Doe" value={contactName} onChange={(e) => setContactName(e.target.value)} style={{ borderRadius: '.75rem' }} /></Form.Group>
              <Form.Group as={Col} md={6} className="mb-3"><Form.Label className="fw-semibold fs-sm">Phone</Form.Label><Form.Control type="text" placeholder="+12345678900" value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} style={{ borderRadius: '.75rem' }} /></Form.Group>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowModal(false)} style={{ borderRadius: '.75rem' }}>Cancel</Button>
            <Button type="submit" className="btn-wa-primary" disabled={createMutation.isPending}>{createMutation.isPending ? 'Saving...' : 'Create Ticket'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </PageWrapper>
  )
}
