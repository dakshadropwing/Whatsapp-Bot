import { useParams, useNavigate } from 'react-router-dom'
import { Badge, Form } from 'react-bootstrap'

export default function Messages() {
  const { id } = useParams()
  const navigate = useNavigate()

  return (
    <div style={{ margin: '-1.5rem', height: 'calc(100vh - var(--header-height))', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="d-flex align-items-center gap-3 p-3" style={{ background: '#fff', borderBottom: '1px solid var(--border-color)' }}>
        <button className="btn btn-sm btn-light" onClick={() => navigate('/conversations')} style={{ borderRadius: '50%', width: 36, height: 36 }}>
          <i className="bi bi-arrow-left" />
        </button>
        <div className="chat-avatar">JS</div>
        <div>
          <div className="fw-semibold">Conversation #{id}</div>
          <div className="text-muted" style={{ fontSize: '.75rem' }}>
            <Badge bg="success" className="badge-status me-1">active</Badge>
            +1 555-0101
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages" style={{ flex: 1 }}>
        <div className="text-center my-3"><Badge bg="light" text="dark" style={{ fontSize: '.7rem' }}>June 11, 2026</Badge></div>
        {[
          { dir: 'inbound' as const, text: 'Hi, I need help with my order #12345', time: '10:24 AM' },
          { dir: 'outbound' as const, text: 'Of course! I can help you with that. Let me pull up your order details.', time: '10:25 AM' },
          { dir: 'outbound' as const, text: 'I found your order. It was shipped yesterday and should arrive by Thursday. Your tracking number is TRK-98765.', time: '10:25 AM' },
          { dir: 'inbound' as const, text: 'Great, thank you! Can I change the delivery address?', time: '10:28 AM' },
          { dir: 'outbound' as const, text: "I'm afraid address changes aren't possible once the order has shipped. However, I can set up a redirect with the carrier for a small fee. Would you like me to do that?", time: '10:29 AM' },
          { dir: 'inbound' as const, text: "Yes please, that would be great!", time: '10:31 AM' },
          { dir: 'outbound' as const, text: "Done! I've set up the redirect. You'll receive a confirmation email shortly with the new delivery details.", time: '10:32 AM' },
          { dir: 'inbound' as const, text: 'Amazing, thank you so much!', time: '10:33 AM' },
        ].map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.dir}`}>
            <div>{msg.text}</div>
            <div className="text-muted mt-1" style={{ fontSize: '.65rem' }}>
              {msg.time}
              {msg.dir === 'outbound' && <span> &middot; <i className="bi bi-check2-all text-primary" /></span>}
              {msg.dir === 'outbound' && <span className="ms-1"><i className="bi bi-robot" style={{ color: '#25d366' }} title="AI Generated" /></span>}
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <button className="btn btn-sm btn-light" style={{ borderRadius: '50%', width: 36, height: 36 }}><i className="bi bi-paperclip" /></button>
        <Form.Control placeholder="Type a message..." style={{ borderRadius: '1.5rem', fontSize: '.875rem' }} />
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '50%', width: 36, height: 36 }}>
          <i className="bi bi-send-fill" />
        </button>
      </div>
    </div>
  )
}
