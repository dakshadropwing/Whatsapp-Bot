import { useState } from 'react'
import { Badge, Form, InputGroup, Dropdown } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'

const statusColors: Record<string, string> = {
  active: 'success', waiting: 'warning', bot_handling: 'info',
  human_handling: 'primary', escalated: 'danger', resolved: 'secondary', closed: 'dark',
}

// Mock conversations (will come from API)
const mockConversations = [
  { id: '1', name: 'John Smith', phone: '+1 555-0101', status: 'active', lastMessage: 'Hi, I need help with my order', time: '2 min', unread: 2 },
  { id: '2', name: 'Sarah Johnson', phone: '+1 555-0102', status: 'waiting', lastMessage: 'Thanks! That worked perfectly.', time: '5 min', unread: 0 },
  { id: '3', name: 'Mike Wilson', phone: '+1 555-0103', status: 'bot_handling', lastMessage: 'What are your pricing plans?', time: '8 min', unread: 1 },
  { id: '4', name: 'Emily Davis', phone: '+1 555-0104', status: 'escalated', lastMessage: 'This is unacceptable, I want a manager', time: '12 min', unread: 3 },
  { id: '5', name: 'Chris Brown', phone: '+1 555-0105', status: 'resolved', lastMessage: 'All good now, thank you!', time: '15 min', unread: 0 },
  { id: '6', name: 'Anna Lee', phone: '+1 555-0106', status: 'active', lastMessage: 'Can you schedule a meeting for tomorrow?', time: '18 min', unread: 1 },
  { id: '7', name: 'David Kim', phone: '+1 555-0107', status: 'bot_handling', lastMessage: 'I want to know about your HR policies', time: '22 min', unread: 0 },
  { id: '8', name: 'Lisa Wang', phone: '+1 555-0108', status: 'waiting', lastMessage: 'Please send me the invoice', time: '30 min', unread: 0 },
]

export default function Conversations() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<string>('all')
  const [activeId, setActiveId] = useState('1')
  const navigate = useNavigate()

  const filtered = mockConversations.filter((c) => {
    const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) || c.phone.includes(search)
    const matchFilter = filter === 'all' || c.status === filter
    return matchSearch && matchFilter
  })

  const active = mockConversations.find((c) => c.id === activeId)

  return (
    <div className="chat-container" style={{ margin: '-1.5rem', height: 'calc(100vh - var(--header-height))' }}>
      {/* Sidebar — conversation list */}
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <h5 className="fw-bold mb-3" style={{ fontSize: '1.1rem' }}>Conversations</h5>
          <InputGroup size="sm">
            <Form.Control
              placeholder="Search by name or phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ borderRadius: '.5rem', fontSize: '.85rem' }}
            />
            <i className="bi bi-search position-absolute" style={{ right: 12, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', zIndex: 5, fontSize: '.8rem' }} />
          </InputGroup>
          <div className="d-flex gap-1 mt-2 flex-wrap">
            {['all', 'active', 'waiting', 'escalated', 'resolved'].map((f) => (
              <button
                key={f}
                className={`btn btn-sm ${filter === f ? 'btn-dark' : 'btn-light'}`}
                style={{ fontSize: '.7rem', padding: '.2rem .6rem', borderRadius: '1rem' }}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="chat-list">
          {filtered.map((c) => (
            <div
              key={c.id}
              className={`chat-item ${c.id === activeId ? 'active' : ''}`}
              onClick={() => setActiveId(c.id)}
            >
              <div className="chat-avatar">{c.name.split(' ').map(n => n[0]).join('')}</div>
              <div className="chat-main">
                <div className="d-flex justify-content-between align-items-center">
                  <span className="fw-semibold" style={{ fontSize: '.85rem' }}>{c.name}</span>
                  <span className="text-muted" style={{ fontSize: '.7rem' }}>{c.time}</span>
                </div>
                <div className="d-flex justify-content-between align-items-center mt-1">
                  <span className="text-muted text-truncate" style={{ fontSize: '.78rem', maxWidth: 180 }}>
                    {c.lastMessage}
                  </span>
                  <div className="d-flex align-items-center gap-1">
                    {c.unread > 0 && (
                      <Badge bg="success" style={{ fontSize: '.6rem', padding: '.2em .5em' }}>{c.unread}</Badge>
                    )}
                  </div>
                </div>
                <Badge bg={statusColors[c.status] || 'secondary'} className="badge-status mt-1">
                  {c.status.replace('_', ' ')}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="chat-main-area">
        {active ? (
          <>
            {/* Chat header */}
            <div className="d-flex justify-content-between align-items-center p-3" style={{ background: '#fff', borderBottom: '1px solid var(--border-color)' }}>
              <div className="d-flex align-items-center gap-3">
                <div className="chat-avatar">{active.name.split(' ').map(n => n[0]).join('')}</div>
                <div>
                  <div className="fw-semibold" style={{ fontSize: '.95rem' }}>{active.name}</div>
                  <div className="text-muted" style={{ fontSize: '.75rem' }}>{active.phone} &middot; {active.status.replace('_', ' ')}</div>
                </div>
              </div>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-outline-success" onClick={() => navigate(`/conversations/${active.id}/messages`)}>
                  <i className="bi bi-chat-text me-1" /> View All
                </button>
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm" id="conv-actions">
                    <i className="bi bi-three-dots-vertical" />
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item><i className="bi bi-person-plus me-2" /> Assign Agent</Dropdown.Item>
                    <Dropdown.Item><i className="bi bi-arrow-up-circle me-2" /> Escalate</Dropdown.Item>
                    <Dropdown.Item><i className="bi bi-check-circle me-2" /> Resolve</Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item className="text-danger"><i className="bi bi-x-circle me-2" /> Close</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </div>

            {/* Messages area */}
            <div className="chat-messages">
              {/* Sample messages */}
              <div className="text-center text-muted my-3" style={{ fontSize: '.75rem' }}>
                <Badge bg="light" text="dark" style={{ fontSize: '.7rem' }}>Today</Badge>
              </div>
              <div className="chat-bubble inbound">
                <div>{active.lastMessage}</div>
                <div className="text-muted mt-1" style={{ fontSize: '.65rem' }}>10:24 AM</div>
              </div>
              <div className="chat-bubble outbound">
                <div>Thank you for reaching out! I'm here to help you with that. Let me look into it right away.</div>
                <div className="text-muted mt-1" style={{ fontSize: '.65rem' }}>10:25 AM &middot; <i className="bi bi-check2-all text-primary" /></div>
              </div>
              <div className="chat-bubble inbound">
                <div>Great, I appreciate the quick response!</div>
                <div className="text-muted mt-1" style={{ fontSize: '.65rem' }}>10:26 AM</div>
              </div>
              <div className="chat-bubble outbound">
                <div>I've found the information you need. Here are the details for your request. Please let me know if you have any other questions!</div>
                <div className="text-muted mt-1" style={{ fontSize: '.65rem' }}>10:27 AM &middot; <i className="bi bi-check2-all text-primary" /></div>
              </div>
            </div>

            {/* Input area */}
            <div className="chat-input-area">
              <button className="btn btn-sm btn-light" style={{ borderRadius: '50%', width: 36, height: 36 }}>
                <i className="bi bi-paperclip" />
              </button>
              <Form.Control
                placeholder="Type a message..."
                style={{ borderRadius: '1.5rem', fontSize: '.875rem' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    /* send message */
                  }
                }}
              />
              <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '50%', width: 36, height: 36 }}>
                <i className="bi bi-send-fill" />
              </button>
            </div>
          </>
        ) : (
          <div className="d-flex flex-column align-items-center justify-content-center h-100">
            <div className="empty-state">
              <i className="bi bi-chat-dots d-block" />
              <h6>Select a conversation</h6>
              <p className="fs-sm text-muted">Choose a conversation from the sidebar to start chatting</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
