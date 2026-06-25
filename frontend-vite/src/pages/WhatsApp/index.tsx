import { Row, Col, Badge } from 'react-bootstrap'
import { PageWrapper } from '@components/PageWrapper'
export default function WhatsApp() {
  return (
    <PageWrapper>
      <div className="mb-4"><h4 className="fw-bold mb-1">WhatsApp Integration</h4><p className="text-muted mb-0 fs-sm">Manage your WhatsApp Business accounts and templates</p></div>
      <Row className="g-3 mb-4 stagger-children">
        {[{ label: 'Connected Accounts', value: '2', icon: 'bi-link-45deg', color: '#25d366' }, { label: 'Templates Approved', value: '15', icon: 'bi-file-earmark-check', color: '#3b82f6' }, { label: 'Messages Sent Today', value: '1,234', icon: 'bi-send', color: '#f59e0b' }, { label: 'Delivery Rate', value: '99.2%', icon: 'bi-check2-all', color: '#8b5cf6' }].map((s) => (
          <Col key={s.label} md={3}>
            <div className="stat-card">
              <div className="d-flex align-items-center gap-3">
                <div className="stat-icon" style={{ background: `${s.color}15`, color: s.color }}><i className={`bi ${s.icon}`} /></div>
                <div><div className="stat-value" style={{ fontSize: '1.4rem' }}>{s.value}</div><div className="stat-label">{s.label}</div></div>
              </div>
            </div>
          </Col>
        ))}
      </Row>
      <div className="data-card">
        <div className="data-card-header"><h5>WhatsApp Business Accounts</h5><button className="btn btn-sm btn-outline-success"><i className="bi bi-plus me-1" />Connect</button></div>
        <div className="table-responsive"><table className="table table-custom mb-0"><thead><tr><th>Account</th><th>Phone Number</th><th>Status</th><th>Messages Today</th></tr></thead>
          <tbody>
            <tr><td className="fw-semibold">Main Business</td><td>+1 555-0100</td><td><Badge bg="success" className="badge-status">Connected</Badge></td><td>1,234</td></tr>
            <tr><td className="fw-semibold">Support Line</td><td>+1 555-0200</td><td><Badge bg="success" className="badge-status">Connected</Badge></td><td>456</td></tr>
          </tbody>
        </table></div>
      </div>
    </PageWrapper>
  )
}
