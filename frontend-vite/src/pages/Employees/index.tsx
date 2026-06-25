import { useState } from 'react'
import { Modal, Form, Button, Row, Col } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employeeService } from '@services/employeeService'
import toast from 'react-hot-toast'
import type { Employee } from '@/types'
import { PageWrapper } from '@components/PageWrapper'
export default function Employees() {
  const qc = useQueryClient()
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null)

  // Form states
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [department, setDepartment] = useState('')
  const [role, setRole] = useState('agent')
  const [status, setStatus] = useState('online')

  // 1. Fetch Employees
  const { data, isLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: () => employeeService.list({ per_page: 100 }),
  })

  // 2. Create Employee Mutation
  const createMutation = useMutation({
    mutationFn: (newEmployee: Partial<Employee>) => employeeService.create(newEmployee),
    onSuccess: () => {
      toast.success('Employee created successfully')
      setShowAddModal(false)
      setName('')
      setEmail('')
      setPhone('')
      setDepartment('')
      setRole('agent')
      setStatus('online')
      qc.invalidateQueries({ queryKey: ['employees'] })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Failed to create employee'
      toast.error(msg)
    },
  })

  // 3. Update Employee Mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Employee> }) =>
      employeeService.update(id, data),
    onSuccess: () => {
      toast.success('Employee updated successfully')
      setShowEditModal(false)
      setSelectedEmployee(null)
      qc.invalidateQueries({ queryKey: ['employees'] })
    },
    onError: () => toast.error('Failed to update employee'),
  })

  // 4. Delete Employee Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => employeeService.delete(id),
    onSuccess: () => {
      toast.success('Employee deleted successfully')
      qc.invalidateQueries({ queryKey: ['employees'] })
    },
    onError: () => toast.error('Failed to delete employee'),
  })

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name || !email) {
      toast.error('Name and Email are required')
      return
    }
    createMutation.mutate({
      name,
      email,
      phone: phone || null,
      department: department || null,
      role,
      status,
    })
  }

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedEmployee) return
    updateMutation.mutate({
      id: selectedEmployee.id,
      data: {
        name,
        email,
        phone: phone || null,
        department: department || null,
        role,
        status,
      },
    })
  }

  const openEditModal = (emp: Employee) => {
    setSelectedEmployee(emp)
    setName(emp.name)
    setEmail(emp.email)
    setPhone(emp.phone || '')
    setDepartment(emp.department || '')
    setRole(emp.role)
    setStatus(emp.status)
    setShowEditModal(true)
  }

  const employeesList = data?.data || []

  return (
    <PageWrapper>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Employees</h4>
          <p className="text-muted mb-0 fs-sm">Manage your team members</p>
        </div>
        <button className="btn btn-wa-primary" onClick={() => setShowAddModal(true)} aria-label="Add new team member">
          <i className="bi bi-person-plus me-1" /> Add Employee
        </button>
      </div>

      <div className="data-card">
        {isLoading ? (
          <div className="d-flex justify-content-center py-5">
            <div className="spinner-border text-success" role="status" />
          </div>
        ) : employeesList.length === 0 ? (
          <div className="text-center py-5 text-muted">No employees found. Click "Add Employee" to register team members.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Department</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th aria-label="Actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {employeesList.map((e: any) => (
                  <tr key={e.id}>
                    <td>
                      <div className="d-flex align-items-center gap-2">
                        <div className="chat-avatar" style={{ width: 34, height: 34, fontSize: '.7rem' }}>
                          {e.name.split(' ').map((n: string) => n[0]).join('')}
                        </div>
                        <div>
                          <div className="fw-semibold" style={{ fontSize: '.85rem' }}>{e.name}</div>
                          <div className="text-muted" style={{ fontSize: '.7rem' }}>{e.email}</div>
                          {e.phone && <div className="text-muted fs-xs">{e.phone}</div>}
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: '.85rem' }}>{e.department || '—'}</td>
                    <td style={{ fontSize: '.85rem' }}>{e.role.toUpperCase()}</td>
                    <td>
                      <span className="d-inline-flex align-items-center gap-1">
                        <span
                          style={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            background: e.status === 'online' ? '#22c55e' : e.status === 'away' ? '#eab308' : '#94a3b8',
                          }}
                        />
                        <span className="fs-xs">{e.status}</span>
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-light me-1"
                        onClick={() => openEditModal(e)}
                        aria-label={`Edit ${e.name}`}
                      >
                        <i className="bi bi-pencil" />
                      </button>
                      <button
                        className="btn btn-sm btn-light text-danger"
                        onClick={() => {
                          if (confirm(`Are you sure you want to delete employee ${e.name}?`)) {
                            deleteMutation.mutate(e.id)
                          }
                        }}
                        aria-label={`Delete ${e.name}`}
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

      {/* Add Employee Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Add New Employee</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreateSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Full Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. Alex Morgan"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Email Address</Form.Label>
              <Form.Control
                type="email"
                placeholder="e.g. alex@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Phone Number</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. +1 555-0201"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Row className="mb-3">
              <Form.Group as={Col} md={6}>
                <Form.Label className="fw-semibold fs-sm">Department</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="e.g. Support, Sales"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  style={{ borderRadius: '.5rem' }}
                />
              </Form.Group>

              <Form.Group as={Col} md={6}>
                <Form.Label className="fw-semibold fs-sm">Role</Form.Label>
                <Form.Select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  style={{ borderRadius: '.5rem' }}
                >
                  <option value="agent">Agent</option>
                  <option value="manager">Manager</option>
                  <option value="lead">Lead</option>
                  <option value="admin">Admin</option>
                </Form.Select>
              </Form.Group>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Initial Status</Form.Label>
              <Form.Select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              >
                <option value="online">Online</option>
                <option value="away">Away</option>
                <option value="offline">Offline</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowAddModal(false)} style={{ borderRadius: '.75rem' }}>Cancel</Button>
            <Button type="submit" className="btn-wa-primary" disabled={createMutation.isPending}>{createMutation.isPending ? 'Saving...' : 'Add Employee'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Employee Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Edit Employee</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleEditSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Full Name</Form.Label>
              <Form.Control
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Email Address</Form.Label>
              <Form.Control
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Phone Number</Form.Label>
              <Form.Control
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Row className="mb-3">
              <Form.Group as={Col} md={6}>
                <Form.Label className="fw-semibold fs-sm">Department</Form.Label>
                <Form.Control
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  style={{ borderRadius: '.5rem' }}
                />
              </Form.Group>

              <Form.Group as={Col} md={6}>
                <Form.Label className="fw-semibold fs-sm">Role</Form.Label>
                <Form.Select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  style={{ borderRadius: '.5rem' }}
                >
                  <option value="agent">Agent</option>
                  <option value="manager">Manager</option>
                  <option value="lead">Lead</option>
                  <option value="admin">Admin</option>
                </Form.Select>
              </Form.Group>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Status</Form.Label>
              <Form.Select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              >
                <option value="online">Online</option>
                <option value="away">Away</option>
                <option value="offline">Offline</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowEditModal(false)} style={{ borderRadius: '.75rem' }}>Cancel</Button>
            <Button type="submit" className="btn-wa-primary" disabled={updateMutation.isPending}>{updateMutation.isPending ? 'Saving...' : 'Save Changes'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </PageWrapper>
  )
}
