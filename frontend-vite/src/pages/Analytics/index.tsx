import { Row, Col } from 'react-bootstrap'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { PageWrapper } from '@components/PageWrapper'
const dailyData = Array.from({ length: 30 }, (_, i) => ({ day: `${i + 1}`, messages: Math.floor(Math.random() * 200 + 80), conversations: Math.floor(Math.random() * 50 + 20) }))
const hourlyData = Array.from({ length: 24 }, (_, i) => ({ hour: `${i}:00`, messages: Math.floor(Math.random() * 80 + 10) }))
const agentPerf = [
  { agent: 'Support', resolved: 342, avgTime: 1.8 },
  { agent: 'Sales', resolved: 215, avgTime: 2.1 },
  { agent: 'Lead', resolved: 180, avgTime: 2.5 },
  { agent: 'Knowledge', resolved: 156, avgTime: 1.2 },
  { agent: 'Appointment', resolved: 89, avgTime: 3.1 },
]

const tt = { contentStyle: { borderRadius: '.75rem', border: '1px solid rgba(255,255,255,.08)', background: 'rgba(17,24,39,.95)', color: '#f1f5f9', fontSize: '.8rem', boxShadow: '0 8px 24px rgba(0,0,0,.4)' } }

export default function Analytics() {
  return (
    <PageWrapper>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div><h4 className="fw-bold mb-1">Analytics</h4><p className="text-muted mb-0 fs-sm">Platform performance metrics and insights</p></div>
        <select className="form-select form-select-sm" style={{ width: 140, borderRadius: '.75rem' }}>
          <option>Last 7 days</option><option>Last 30 days</option><option>Last 90 days</option>
        </select>
      </div>

      <Row className="g-3 mb-4 stagger-children">
        {[
          { label: 'Total Messages', value: '12,847', change: '+15.3%', icon: 'bi-send', color: '#25d366' },
          { label: 'Total Conversations', value: '3,241', change: '+8.7%', icon: 'bi-chat-dots', color: '#3b82f6' },
          { label: 'Avg Response Time', value: '1.9s', change: '-12.4%', icon: 'bi-clock', color: '#f59e0b' },
          { label: 'Satisfaction Score', value: '4.7/5', change: '+0.3', icon: 'bi-star', color: '#8b5cf6' },
        ].map((s) => (
          <Col key={s.label} md={3}>
            <div className="stat-card">
              <div className="d-flex justify-content-between">
                <div>
                  <div className="stat-label">{s.label}</div>
                  <div className="stat-value" style={{ fontSize: '1.5rem' }}>{s.value}</div>
                  <div className="stat-change text-success"><i className="bi bi-arrow-up-short me-1" />{s.change}</div>
                </div>
                <div className="stat-icon" style={{ background: `${s.color}15`, color: s.color }}><i className={`bi ${s.icon}`} /></div>
              </div>
            </div>
          </Col>
        ))}
      </Row>

      <Row className="g-3 mb-4">
        <Col md={8}>
          <div className="data-card">
            <div className="data-card-header"><h5>Messages Over Time</h5></div>
            <div className="data-card-body" style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={dailyData}>
                  <defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#25d366" stopOpacity={0.2} /><stop offset="95%" stopColor="#25d366" stopOpacity={0} /></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" />
                  <XAxis dataKey="day" axisLine={false} tick={{ fontSize: 11, fill: '#64748b' }} /><YAxis axisLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                  <Tooltip {...tt} /><Area type="monotone" dataKey="messages" stroke="#25d366" fill="url(#ag)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Col>
        <Col md={4}>
          <div className="data-card">
            <div className="data-card-header"><h5>Hourly Distribution</h5></div>
            <div className="data-card-body" style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" />
                  <XAxis dataKey="hour" axisLine={false} tick={{ fontSize: 10, fill: '#64748b' }} /><YAxis axisLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip {...tt} /><Bar dataKey="messages" fill="#25d366" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Col>
      </Row>

      <div className="data-card">
        <div className="data-card-header"><h5>Agent Performance</h5></div>
        <div className="table-responsive">
          <table className="table table-custom mb-0">
            <thead><tr><th>Agent</th><th>Resolved</th><th>Avg Response Time</th><th>Performance</th></tr></thead>
            <tbody>{agentPerf.map((a) => (
              <tr key={a.agent}><td className="fw-semibold">{a.agent}</td><td>{a.resolved}</td><td>{a.avgTime}s</td>
                <td><div className="progress" style={{ height: 6, width: 120, borderRadius: 3 }}><div className="progress-bar" style={{ width: `${(a.resolved / 342) * 100}%`, background: 'linear-gradient(90deg, #25d366, #128c7e)' }} /></div></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  )
}
