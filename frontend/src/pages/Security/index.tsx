import { Row, Col, Form } from 'react-bootstrap'
export default function Security() {
  return (
    <div>
      <div className="mb-4"><h4 className="fw-bold mb-1">Security</h4><p className="text-muted mb-0 fs-sm">Monitor and manage platform security settings</p></div>
      <Row className="g-3 mb-4">
        {[{ label: 'Encryption Status', value: 'AES-256-GCM', icon: 'bi-lock', status: 'Active' }, { label: 'SSL Certificate', value: 'Valid', icon: 'bi-shield-check', status: '90 days left' }, { label: 'Failed Logins (24h)', value: '3', icon: 'bi-exclamation-triangle', status: 'Normal' }, { label: 'API Keys Active', value: '4', icon: 'bi-key', status: '2 expiring' }].map((s) => (
          <Col key={s.label} md={3}><div className="stat-card"><div className="d-flex align-items-center gap-3"><div className="stat-icon" style={{ background: '#f0fdf4', color: '#25d366' }}><i className={`bi ${s.icon}`} /></div><div><div className="fw-bold" style={{ fontSize: '1.1rem' }}>{s.value}</div><div className="stat-label">{s.label}</div><div className="text-wa-green fs-xs">{s.status}</div></div></div></div></Col>
        ))}
      </Row>
      <Row className="g-3">
        <Col md={6}><div className="data-card"><div className="data-card-header"><h5><i className="bi bi-key me-2" />API Keys</h5><button className="btn btn-sm btn-outline-success"><i className="bi bi-plus me-1" />Generate</button></div>
          <div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Name</th><th>Prefix</th><th>Last Used</th><th>Status</th></tr></thead>
            <tbody><tr><td className="fw-semibold fs-sm">Production Key</td><td><code>wa_prod_...a3f</code></td><td className="text-muted fs-sm">2 min ago</td><td><span className="badge bg-success badge-status">Active</span></td></tr>
            <tr><td className="fw-semibold fs-sm">Staging Key</td><td><code>wa_stg_...b7e</code></td><td className="text-muted fs-sm">1 day ago</td><td><span className="badge bg-success badge-status">Active</span></td></tr>
            <tr><td className="fw-semibold fs-sm">CI/CD Key</td><td><code>wa_ci_...c1d</code></td><td className="text-muted fs-sm">3 days ago</td><td><span className="badge bg-warning badge-status">Expiring</span></td></tr></tbody>
          </table></div></div></Col>
        <Col md={6}><div className="data-card"><div className="data-card-header"><h5><i className="bi bi-shield-lock me-2" />Security Policies</h5></div>
          <div className="data-card-body">
            <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Password Policy</div><div className="text-muted fs-xs">Min 8 chars, uppercase, number, symbol</div></div><Form.Check type="switch" defaultChecked /></div>
            <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">Session Timeout</div><div className="text-muted fs-xs">Auto-logout after 60 minutes</div></div><Form.Check type="switch" defaultChecked /></div>
            <div className="d-flex justify-content-between align-items-center mb-3"><div><div className="fw-semibold fs-sm">IP Allowlist</div><div className="text-muted fs-xs">Restrict access to specific IP ranges</div></div><button className="btn btn-sm btn-outline-secondary">Configure</button></div>
            <div className="d-flex justify-content-between align-items-center"><div><div className="fw-semibold fs-sm">Webhook Signature Verification</div><div className="text-muted fs-xs">HMAC-SHA256 for all inbound webhooks</div></div><Form.Check type="switch" defaultChecked disabled /></div>
          </div></div></Col>
      </Row>
    </div>
  )
}
