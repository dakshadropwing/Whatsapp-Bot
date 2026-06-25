import { useState } from 'react'
import { Badge, Form, InputGroup, Dropdown, Spinner } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { conversationService } from '@services/conversationService'
import { agentService } from '@services/agentService'
import { whatsappService } from '@services/whatsappService'
import toast from 'react-hot-toast'

const statusColors: Record<string, string> = {
  active: 'success',
  waiting: 'warning',
  bot_handling: 'info',
  human_handling: 'primary',
  escalated: 'danger',
  resolved: 'secondary',
  closed: 'dark',
}

export default function Conversations() {
  const qc = useQueryClient()
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<string>('all')
  const [activeId, setActiveId] = useState<string | null>(null)
  const [messageText, setMessageText] = useState('')

  // 1. Fetch Conversations
  const { data: convsData, isLoading: isConvsLoading } = useQuery({
    queryKey: ['conversations', filter, search],
    queryFn: () =>
      conversationService.list({
        status: filter === 'all' ? undefined : filter,
        search: search || undefined,
        per_page: 50,
      }),
  })

  const conversationsList = convsData?.data || []

  // If no conversation is active but list has items, set first as active
  if (!activeId && conversationsList.length > 0) {
    setActiveId(conversationsList[0].id)
  }

  const active = conversationsList.find((c: any) => c.id === activeId)

  // 2. Fetch Messages for Active Conversation
  const { data: messagesData, isLoading: isMessagesLoading } = useQuery({
    queryKey: ['messages', activeId],
    queryFn: () => conversationService.getMessages(activeId!),
    enabled: !!activeId,
  })

  const messagesList = messagesData?.data || []

  // 3. Fetch AI Agents for Assignment Dropdown
  const { data: agentsData } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentService.list({ per_page: 50 }),
  })

  const agentsList = agentsData?.data || []

  // 4. Resolve Mutation
  const resolveMutation = useMutation({
    mutationFn: (id: string) => conversationService.resolve(id),
    onSuccess: () => {
      toast.success('Conversation resolved')
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => toast.error('Failed to resolve conversation'),
  })

  // 5. Escalate Mutation
  const escalateMutation = useMutation({
    mutationFn: (id: string) => conversationService.escalate(id),
    onSuccess: () => {
      toast.success('Conversation escalated')
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => toast.error('Failed to escalate conversation'),
  })

  // 6. Assign Agent Mutation
  const assignMutation = useMutation({
    mutationFn: ({ id, agentId }: { id: string; agentId: string }) =>
      conversationService.assign(id, { assigned_agent_id: agentId }),
    onSuccess: () => {
      toast.success('AI Agent assigned')
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => toast.error('Failed to assign agent'),
  })

  // 7. Send Message Mutation (simulated outbound reply)
  const sendMessageMutation = useMutation({
    mutationFn: ({ phone, message }: { phone: string; message: string }) =>
      whatsappService.sendText({ phone, message }),
    onSuccess: () => {
      setMessageText('')
      toast.success('Message sent')
      qc.invalidateQueries({ queryKey: ['messages', activeId] })
      qc.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => toast.error('Failed to send message'),
  })

  const handleSendMessage = () => {
    if (!messageText.trim() || !active) return
    sendMessageMutation.mutate({
      phone: active.contact_phone,
      message: messageText,
    })
  }

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
            {['all', 'active', 'waiting', 'bot_handling', 'human_handling', 'escalated', 'resolved'].map((f) => (
              <button
                key={f}
                className={`btn btn-sm ${filter === f ? 'btn-dark' : 'btn-light'}`}
                style={{ fontSize: '.7rem', padding: '.2rem .6rem', borderRadius: '1rem' }}
                onClick={() => setFilter(f)}
              >
                {f.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </button>
            ))}
          </div>
        </div>

        {isConvsLoading ? (
          <div className="d-flex justify-content-center py-5">
            <Spinner animation="border" variant="success" size="sm" />
          </div>
        ) : conversationsList.length === 0 ? (
          <div className="text-center py-5 text-muted fs-sm">No conversations found.</div>
        ) : (
          <div className="chat-list">
            {conversationsList.map((c: any) => (
              <div
                key={c.id}
                className={`chat-item ${c.id === activeId ? 'active' : ''}`}
                onClick={() => setActiveId(c.id)}
              >
                <div className="chat-avatar">
                  {c.contact_name ? c.contact_name.split(' ').map((n: string) => n[0]).join('') : 'U'}
                </div>
                <div className="chat-main">
                  <div className="d-flex justify-content-between align-items-center">
                    <span className="fw-semibold" style={{ fontSize: '.85rem' }}>
                      {c.contact_name || c.contact_phone}
                    </span>
                    <span className="text-muted" style={{ fontSize: '.7rem' }}>
                      {c.last_message_at ? new Date(c.last_message_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center mt-1">
                    <span className="text-muted text-truncate" style={{ fontSize: '.78rem', maxWidth: 180 }}>
                      {c.priority === 'high' ? '⚠️ High Priority' : 'Message thread'}
                    </span>
                    <Badge bg={statusColors[c.status] || 'secondary'} className="badge-status">
                      {c.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main chat area */}
      <div className="chat-main-area">
        {active ? (
          <>
            {/* Chat header */}
            <div className="d-flex justify-content-between align-items-center p-3" style={{ background: '#fff', borderBottom: '1px solid var(--border-color)' }}>
              <div className="d-flex align-items-center gap-3">
                <div className="chat-avatar">
                  {active.contact_name ? active.contact_name.split(' ').map((n: string) => n[0]).join('') : 'U'}
                </div>
                <div>
                  <div className="fw-semibold" style={{ fontSize: '.95rem' }}>{active.contact_name || 'WhatsApp User'}</div>
                  <div className="text-muted" style={{ fontSize: '.75rem' }}>
                    {active.contact_phone} &middot; {active.status.replace('_', ' ')}
                  </div>
                </div>
              </div>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-outline-success" onClick={() => navigate(`/conversations/${active.id}/messages`)}>
                  <i className="bi bi-chat-text me-1" /> View All
                </button>
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm" id="conv-actions" aria-label="Conversation actions">
                    <i className="bi bi-three-dots-vertical" />
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Header>Assign AI Specialist</Dropdown.Header>
                    {agentsList.filter((a: any) => a.is_active).map((agent: any) => (
                      <Dropdown.Item key={agent.id} onClick={() => assignMutation.mutate({ id: active.id, agentId: agent.id })}>
                        <i className="bi bi-robot me-2" /> {agent.name}
                      </Dropdown.Item>
                    ))}
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={() => escalateMutation.mutate(active.id)}>
                      <i className="bi bi-arrow-up-circle me-2 text-warning" /> Escalate to Human
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => resolveMutation.mutate(active.id)}>
                      <i className="bi bi-check-circle me-2 text-success" /> Resolve Thread
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </div>

            {/* Messages area */}
            <div className="chat-messages">
              {isMessagesLoading ? (
                <div className="d-flex justify-content-center py-5">
                  <Spinner animation="border" variant="success" size="sm" />
                </div>
              ) : messagesList.length === 0 ? (
                <div className="text-center text-muted py-5 fs-sm">No messages in this conversation.</div>
              ) : (
                messagesList
                  .slice()
                  .reverse()
                  .map((msg: any) => (
                    <div key={msg.id} className={`chat-bubble ${msg.direction}`}>
                      <div>{msg.body}</div>
                      <div className="text-muted mt-1" style={{ fontSize: '.65rem' }}>
                        {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        {msg.direction === 'outbound' && (
                          <span>
                            {' '}
                            &middot;{' '}
                            <i
                              className={`bi ${msg.status === 'read' ? 'bi-check2-all text-primary' : 'bi-check2'}`}
                              title={msg.status}
                            />
                          </span>
                        )}
                        {msg.ai_generated && (
                          <span className="ms-1" title="AI Generated">
                            <i className="bi bi-robot text-success" />
                          </span>
                        )}
                      </div>
                    </div>
                  ))
              )}
            </div>

            {/* Input area */}
            <div className="chat-input-area">
              <button className="btn btn-sm btn-light" style={{ borderRadius: '50%', width: 36, height: 36 }} aria-label="Attach file">
                <i className="bi bi-paperclip" />
              </button>
              <Form.Control
                placeholder="Type a message..."
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                style={{ borderRadius: '1.5rem', fontSize: '.875rem' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage()
                  }
                }}
              />
              <button
                className="btn btn-sm text-white"
                onClick={handleSendMessage}
                disabled={sendMessageMutation.isPending}
                aria-label="Send message"
                style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '50%', width: 36, height: 36 }}
              >
                {sendMessageMutation.isPending ? (
                  <Spinner animation="border" size="sm" variant="light" />
                ) : (
                  <i className="bi bi-send-fill" />
                )}
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

