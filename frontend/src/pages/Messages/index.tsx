import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Badge, Form, Spinner } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { conversationService } from '@services/conversationService'
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

export default function Messages() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [messageText, setMessageText] = useState('')

  // 1. Fetch Conversation Details
  const { data: convData, isLoading: isConvLoading } = useQuery({
    queryKey: ['conversations', id],
    queryFn: () => conversationService.get(id!),
    enabled: !!id,
  })

  const conv = convData?.conversation

  // 2. Fetch Messages
  const { data: messagesData, isLoading: isMessagesLoading } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => conversationService.getMessages(id!),
    enabled: !!id,
  })

  const messagesList = messagesData?.data || []

  // 3. Send Message Mutation
  const sendMessageMutation = useMutation({
    mutationFn: ({ phone, message }: { phone: string; message: string }) =>
      whatsappService.sendText({ phone, message }),
    onSuccess: () => {
      setMessageText('')
      toast.success('Message sent')
      qc.invalidateQueries({ queryKey: ['messages', id] })
    },
    onError: () => toast.error('Failed to send message'),
  })

  const handleSendMessage = () => {
    if (!messageText.trim() || !conv) return
    sendMessageMutation.mutate({
      phone: conv.contact_phone,
      message: messageText,
    })
  }

  return (
    <div style={{ margin: '-1.5rem', height: 'calc(100vh - var(--header-height))', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="d-flex align-items-center gap-3 p-3" style={{ background: '#fff', borderBottom: '1px solid var(--border-color)' }}>
        <button className="btn btn-sm btn-light" onClick={() => navigate('/conversations')} style={{ borderRadius: '50%', width: 36, height: 36 }}>
          <i className="bi bi-arrow-left" />
        </button>
        <div className="chat-avatar">
          {conv?.contact_name ? conv.contact_name.split(' ').map((n: string) => n[0]).join('') : 'U'}
        </div>
        <div>
          <div className="fw-semibold">
            {isConvLoading ? 'Loading conversation...' : (conv?.contact_name || 'Conversation Detail')}
          </div>
          {conv && (
            <div className="text-muted" style={{ fontSize: '.75rem' }}>
              <Badge bg={statusColors[conv.status] || 'secondary'} className="badge-status me-1">
                {conv.status.replace('_', ' ')}
              </Badge>
              {conv.contact_phone}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages" style={{ flex: 1 }}>
        {isMessagesLoading ? (
          <div className="d-flex justify-content-center py-5">
            <Spinner animation="border" variant="success" />
          </div>
        ) : messagesList.length === 0 ? (
          <div className="text-center my-5 text-muted fs-sm">No messages.</div>
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

      {/* Input */}
      <div className="chat-input-area">
        <button className="btn btn-sm btn-light" style={{ borderRadius: '50%', width: 36, height: 36 }}><i className="bi bi-paperclip" /></button>
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
          style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '50%', width: 36, height: 36 }}
        >
          {sendMessageMutation.isPending ? (
            <Spinner animation="border" size="sm" variant="light" />
          ) : (
            <i className="bi bi-send-fill" />
          )}
        </button>
      </div>
    </div>
  )
}

