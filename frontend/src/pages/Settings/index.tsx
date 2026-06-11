import { Row, Col, Form } from 'react-bootstrap'
export default function Settings() {
  return (
    <div>
      <div className="mb-4"><h4 className="fw-bold mb-1">Settings</h4><p className="text-muted mb-0 fs-sm">Configure your platform settings</p></div>
      <Row className="g-4">
        <Col xl={6}>
          <div className="data-card"><div className="data-card-header"><h5><i className="bi bi-whatsapp me-2" />WhatsApp Configuration</h5></div>
            <div className="data-card-body">
              <Form><Form.Group className="mb-3"><Form.Label className="fw-semibold fs-xs">Phone Number ID</Form.Label><Form.Control defaultValue="123456789" style={{ borderRadius: '.5rem' }} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label className="fw-semibold fs-xs">Business Account ID</Form.Label><Form.Control defaultValue="987654321" style={{ borderRadius: '.5rem' }} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label className="fw-semibold fs-xs">Webhook Verify Token</Form.Label><Form.Control type="password" defaultValue="my-secret-token" style={{ borderRadius: '.5rem' }} /></Form.Group>
              <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.5rem' }}>Save Changes</button></Form>
            </div></div>
        </Col>
        <Col xl={6}>
          <div className="data-card"><div className="data-card-header"><h5><i className="bi bi-robot me-2" />AI Provider Settings</h5></div>
            <div className="data-card-body">
              <Form><Form.Group className="mb-3"><Form.Label className="fw-semibold fs-xs">Default Provider</Form.Label><Form.Select style={{ borderRadius: '.5rem' }}><option>Ollama (Local)</option><option>Google Gemini</option></Form.Select></Form.Group>
              <Form.Group className="mb-3"><Form.Label className="fw-semibold fs-xs">Ollama Base URL</Form.Label><Form.Control defaultValue="http://localhost:11434" style={{ borderRadius: '.5rem' }} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label className="fw-semibold fs-xs">Google AI API Key</Form.Label><Form.Control type="password" placeholder="Enter API key" style={{ borderRadius: '.5rem' }} /></Form.Group>
              <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.5rem' }}>Save Changes</button></Form>
            </div></div>
        </Col>
        <Col xl={6}>
          <div className="data-card"><div className="data-card-header"><h5><i className="bi bi-shield-lock me-2" />Security Settings</h5></div>
            <div className="data-card-body">
              <Form>
                <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Two-Factor Authentication</div><div className="text-muted fs-xs">Require 2FA for all users</div></div><Form.Check type="switch" id="2fa" /></div>
                <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Rate Limiting</div><div className="text-muted fs-xs">100 requests/minute per user</div></div><Form.Check type="switch" defaultChecked id="rate" /></div>
                <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">IP Allowlist</div><div className="text-muted fs-xs">Restrict access by IP</div></div><button className="btn btn-sm btn-outline-secondary">Configure</button></div>
              </Form>
            </div></div>
        </Col>
        <Col xl={6}>
          <div className="data-card"><div className="data-card-header"><h5><i className="bi bi-bell me-2" />Notification Settings</h5></div>
            <div className="data-card-body">
              <Form>
                <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Email Notifications</div><div className="text-muted fs-xs">Send email for critical events</div></div><Form.Check type="switch" defaultChecked /></div>
                <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Escalation Alerts</div><div className="text-muted fs-xs">Notify on ticket escalation</div></div><Form.Check type="switch" defaultChecked /></div>
                <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Daily Summary</div><div className="text-muted fs-xs">Send daily platform summary</div></div><Form.Check type="switch" /></div>
              </Form>
            </div></div>
        </Col>
      </Row>
    </div>
  )
}
