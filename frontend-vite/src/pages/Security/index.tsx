import { Row, Col, Form } from 'react-bootstrap'
import { PageWrapper } from '@components/PageWrapper'
export default function Security() {
  return (
    <PageWrapper>
      <div className="mb-4"><h4 className="fw-bold mb-1">Security</h4><p className="text-muted mb-0 fs-sm">Monitor and manage platform security settings</p></div>
      <Row className="g-3 mb-4 stagger-children">
        {[
          { label: 'Encryption Status', value: 'AES-256-GCM', icon: 'bi-lock', status: 'Active', color: '#25d366' },
          { label: 'SSL Certificate', value: 'Valid', icon: 'bi-shield-check', status: '90 days left', color: '#3b82f6' },
          { label: 'Failed Logins (24h)', value: '3', icon: 'bi-exclamation-triangle', status: 'Normal', color: '#f59e0b' },
          { label: 'API Keys Active', value: '4', icon: 'bi-key', status: '2 expiring', color: '#8b5cf6' },
        ].map((s) => (
          <Col key={s.label} md={3}>
            <div className="stat-card">
              <div className="d-flex align-items-center gap-3">
                <div className="stat-icon" style={{ background: `${s.color}15`, color: s.color }}><i className={`bi ${s.icon}`} /></div>
                <div>
                  <div className="fw-bold" style={{ fontSize: '1.1rem' }}>{s.value}</div>
                  <div className="stat-label">{s.label}</div>
                  <div className="text-wa-green fs-xs">{s.status}</div>
                </div>
              </div>
            </div>
          </Col>
        ))}
      </Row>
      <Row className="g-3">
        <Col md={6}>
          <div className="data-card">
            <div className="data-card-header"><h5><i className="bi bi-key me-2" />API Keys</h5><button className="btn btn-sm btn-outline-success"><i className="bi bi-plus me-1" />Generate</button></div>
            <div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Name</th><th>Prefix</th><th>Last Used</th><th>Status</th></tr></thead>
              <tbody>
                <tr><td className="fw-semibold fs-sm">Production Key</td><td><code style={{ color: '#25d366' }}>wa_prod_...a3f</code></td><td className="fs-sm" style={{ color: 'var(--text-muted)' }}>2 min ago</td><td><span className="badge bg-success badge-status">Active</span></td></tr>
                <tr><td className="fw-semibold fs-sm">Staging Key</td><td><code style={{ color: '#25d366' }}>wa_stg_...b7e</code></td><td className="fs-sm" style={{ color: 'var(--text-muted)' }}>1 day ago</td><td><span className="badge bg-success badge-status">Active</span></td></tr>
                <tr><td className="fw-semibold fs-sm">CI/CD Key</td><td><code style={{ color: '#f59e0b' }}>wa_ci_...c1d</code></td><td className="fs-sm" style={{ color: 'var(--text-muted)' }}>3 days ago</td><td><span className="badge bg-warning badge-status">Expiring</span></td></tr>
              </tbody>
            </table></div>
          </div>
        </Col>
        <Col md={6}>
          <div className="data-card">
            <div className="data-card-header"><h5><i className="bi bi-shield-lock me-2" />Security Policies</h5></div>
            <div className="data-card-body">
              {[
                { title: 'Password Policy', desc: 'Min 8 chars, uppercase, number, symbol', checked: true, disabled: false },
                { title: 'Session Timeout', desc: 'Auto-logout after 60 minutes', checked: true, disabled: false },
                { title: 'IP Allowlist', desc: 'Restrict access to specific IP ranges', btn: true },
                { title: 'Webhook Signature Verification', desc: 'HMAC-SHA256 for all inbound webhooks', checked: true, disabled: true },
              ].map((p, i) => (
                <div key={i} className="d-flex justify-content-between align-items-center" style={{ padding: '.75rem 0', borderBottom: i < 3 ? '1px solid var(--border-color)' : 'none' }}>
                  <div><div className="fw-semibold fs-sm">{p.title}</div><div className="fs-xs" style={{ color: 'var(--text-muted)' }}>{p.desc}</div></div>
                  {p.btn ? <button className="btn btn-sm btn-outline-secondary">Configure</button> : <Form.Check type="switch" defaultChecked={p.checked} disabled={p.disabled} />}
                </div>
              ))}
            </div>
          </div>
        </Col>
      </Row>
    </PageWrapper>
  )
}
