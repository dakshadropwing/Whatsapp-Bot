import { useState } from 'react'
import { Badge, Modal, Form, Button } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '@services/userService'
import toast from 'react-hot-toast'
import type { User } from '@/types'

const roleColors: Record<string, string> = {
  superadmin: 'danger',
  admin: 'primary',
  agent: 'success',
  user: 'secondary',
}

export default function Users() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)

  // Form states
  const [username, setUsername] = useState('')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [roleId, setRoleId] = useState('')

  // 1. Fetch Users
  const { data: usersData, isLoading: isUsersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.list({ per_page: 100 }),
  })

  // 2. Fetch Roles
  const { data: rolesData } = useQuery({
    queryKey: ['roles'],
    queryFn: () => userService.getRoles(),
  })

  // 3. Create User Mutation
  const createMutation = useMutation({
    mutationFn: (newUser: Record<string, any>) => userService.create(newUser),
    onSuccess: () => {
      toast.success('User invited successfully')
      setShowModal(false)
      setUsername('')
      setFullName('')
      setEmail('')
      setPassword('')
      setRoleId('')
      qc.invalidateQueries({ queryKey: ['users'] })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Failed to create user'
      toast.error(msg)
    },
  })

  // 4. Deactivate User Mutation
  const deactivateMutation = useMutation({
    mutationFn: (id: string) => userService.delete(id),
    onSuccess: () => {
      toast.success('User deactivated successfully')
      qc.invalidateQueries({ queryKey: ['users'] })
    },
    onError: () => toast.error('Failed to deactivate user'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !username || !fullName || !password) {
      toast.error('All fields except Role are required')
      return
    }
    createMutation.mutate({
      email,
      username,
      full_name: fullName,
      password,
      role_id: roleId || undefined,
    })
  }

  const usersList = usersData?.data || []
  const rolesList = rolesData?.roles || []

  // Helper to map role_id to role name
  const getRoleName = (u: User) => {
    if (u.id && u.email === 'admin@dev.local') return 'superadmin' // safety fallback
    const matched = rolesList.find((r) => r.id === u.role_id)
    return matched ? matched.name : 'user'
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1">Users</h4>
          <p className="text-muted mb-0 fs-sm">Manage platform users and roles</p>
        </div>
        <button
          className="btn btn-sm text-white"
          onClick={() => setShowModal(true)}
          style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}
          aria-label="Invite new platform user"
        >
          <i className="bi bi-plus-lg me-1" /> Invite User
        </button>
      </div>

      <div className="data-card">
        {isUsersLoading ? (
          <div className="d-flex justify-content-center py-5">
            <div className="spinner-border text-success" role="status" />
          </div>
        ) : usersList.length === 0 ? (
          <div className="text-center py-5 text-muted">No users found. Click "Invite User" to create one.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th aria-label="Actions"></th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u: any) => {
                  const roleName = getRoleName(u)
                  return (
                    <tr key={u.id}>
                      <td>
                        <div className="d-flex align-items-center gap-2">
                          <div className="chat-avatar" style={{ width: 34, height: 34, fontSize: '.7rem' }}>
                            {u.full_name ? u.full_name.split(' ').map((n: string) => n[0]).join('') : 'U'}
                          </div>
                          <div>
                            <div className="fw-semibold" style={{ fontSize: '.85rem' }}>{u.full_name}</div>
                            <div className="text-muted" style={{ fontSize: '.7rem' }}>{u.email} ({u.username})</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <Badge bg={roleColors[roleName] || 'secondary'} className="badge-status">
                          {roleName.toUpperCase()}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg={u.is_active ? 'success' : 'secondary'} className="badge-status">
                          {u.is_active ? 'active' : 'inactive'}
                        </Badge>
                      </td>
                      <td className="text-muted" style={{ fontSize: '.8rem' }}>
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td>
                        {u.is_active && u.email !== 'admin@dev.local' && (
                          <button
                            className="btn btn-sm btn-light text-danger"
                            onClick={() => {
                              if (confirm(`Are you sure you want to deactivate user ${u.full_name}?`)) {
                                deactivateMutation.mutate(u.id)
                              }
                            }}
                            aria-label={`Deactivate ${u.full_name}`}
                          >
                            <i className="bi bi-trash" />
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Invite User Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title className="fw-bold fs-5">Invite New User</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Full Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Username</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g. johndoe"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Email Address</Form.Label>
              <Form.Control
                type="email"
                placeholder="e.g. john@platform.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Password</Form.Label>
              <Form.Control
                type="password"
                placeholder="Set initial password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ borderRadius: '.5rem' }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold fs-sm">Role</Form.Label>
              <Form.Select
                value={roleId}
                onChange={(e) => setRoleId(e.target.value)}
                style={{ borderRadius: '.5rem' }}
              >
                <option value="">Select Role (Default: staff user)</option>
                {rolesList.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name.toUpperCase()} - {r.description}
                  </option>
                ))}
              </Form.Select>
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
              {createMutation.isPending ? 'Saving...' : 'Invite User'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  )
}
