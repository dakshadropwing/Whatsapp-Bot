import { Row, Col, Badge } from 'react-bootstrap'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { useAuthStore } from '@store/auth'

// ── Mock Data (will be replaced by API) ──────────────────
const messagesByDay = [
  { day: 'Mon', inbound: 120, outbound: 95 },
  { day: 'Tue', inbound: 145, outbound: 110 },
  { day: 'Wed', inbound: 132, outbound: 128 },
  { day: 'Thu', inbound: 168, outbound: 140 },
  { day: 'Fri', inbound: 155, outbound: 135 },
  { day: 'Sat', inbound: 89, outbound: 72 },
  { day: 'Sun', inbound: 64, outbound: 58 },
]

const agentUsage = [
  { name: 'Support', value: 340, color: '#25d366' },
  { name: 'Sales', value: 215, color: '#128c7e' },
  { name: 'Lead', value: 180, color: '#075e54' },
  { name: 'Appointment', value: 95, color: '#34b7f1' },
  { name: 'Knowledge', value: 72, color: '#64748b' },
]

const recentConversations = [
  { id: '1', name: 'John Smith', phone: '+1 555-0101', status: 'active', agent: 'Support', messages: 12, time: '2 min ago' },
  { id: '2', name: 'Sarah Johnson', phone: '+1 555-0102', status: 'waiting', agent: 'Sales', messages: 8, time: '5 min ago' },
  { id: '3', name: 'Mike Wilson', phone: '+1 555-0103', status: 'bot_handling', agent: 'Lead', messages: 15, time: '8 min ago' },
  { id: '4', name: 'Emily Davis', phone: '+1 555-0104', status: 'escalated', agent: 'Support', messages: 22, time: '12 min ago' },
  { id: '5', name: 'Chris Brown', phone: '+1 555-0105', status: 'resolved', agent: 'Knowledge', messages: 6, time: '15 min ago' },
]

const statusColors: Record<string, string> = {
  active: 'success',
  waiting: 'warning',
  bot_handling: 'info',
  human_handling: 'primary',
  escalated: 'danger',
  resolved: 'secondary',
  closed: 'dark',
}

export default function Dashboard() {
  const user = useAuthStore((s) => s.user)

  return (
    <div>
      {/* Page Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-1" style={{ letterSpacing: '-0.02em' }}>
            Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}, {user?.full_name?.split(' ')[0] || 'there'}!
          </h4>
          <p className="text-muted mb-0" style={{ fontSize: '.875rem' }}>
            Here's what's happening with your WhatsApp platform today.
          </p>
        </div>
        <button className="btn btn-sm text-white" style={{ background: 'linear-gradient(135deg, #25d366, #128c7e)', borderRadius: '.5rem', padding: '.5rem 1.25rem' }}>
          <i className="bi bi-plus-lg me-1" /> New Conversation
        </button>
      </div>

      {/* Stats Cards */}
      <Row className="g-3 mb-4">
        {[
          { label: 'Total Conversations', value: '2,847', icon: 'bi-chat-dots-fill', bg: '#f0fdf4', color: '#25d366', change: '+12.5%', up: true },
          { label: 'Messages Today', value: '1,234', icon: 'bi-send-fill', bg: '#eff6ff', color: '#3b82f6', change: '+8.2%', up: true },
          { label: 'Active Tickets', value: '23', icon: 'bi-ticket-detailed', bg: '#fefce8', color: '#eab308', change: '-3.1%', up: false },
          { label: 'AI Resolution Rate', value: '87.3%', icon: 'bi-robot', bg: '#f5f3ff', color: '#8b5cf6', change: '+2.4%', up: true },
        ].map((stat) => (
          <Col key={stat.label} xl={3} md={6}>
            <div className="stat-card">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <div className="stat-label">{stat.label}</div>
                  <div className="stat-value">{stat.value}</div>
                  <div className={`stat-change ${stat.up ? 'text-success' : 'text-danger'}`}>
                    <i className={`bi bi-arrow-${stat.up ? 'up' : 'down'}-short me-1`} />
                    {stat.change} vs last week
                  </div>
                </div>
                <div className="stat-icon" style={{ background: stat.bg, color: stat.color }}>
                  <i className={`bi ${stat.icon}`} />
                </div>
              </div>
            </div>
          </Col>
        ))}
      </Row>

      {/* Charts Row */}
      <Row className="g-3 mb-4">
        {/* Messages Over Time */}
        <Col xl={8}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>Messages Overview</h5>
              <div className="d-flex gap-2">
                <span className="d-inline-flex align-items-center gap-1 fs-xs text-muted">
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#25d366' }} /> Inbound
                </span>
                <span className="d-inline-flex align-items-center gap-1 fs-xs text-muted">
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#128c7e' }} /> Outbound
                </span>
              </div>
            </div>
            <div className="data-card-body" style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={messagesByDay}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip contentStyle={{ borderRadius: '0.5rem', border: '1px solid #e2e8f0', fontSize: '.85rem' }} />
                  <Area type="monotone" dataKey="inbound" stroke="#25d366" fill="#25d366" fillOpacity={0.1} strokeWidth={2} />
                  <Area type="monotone" dataKey="outbound" stroke="#128c7e" fill="#128c7e" fillOpacity={0.1} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Col>

        {/* Agent Distribution */}
        <Col xl={4}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>Agent Distribution</h5>
            </div>
            <div className="data-card-body d-flex flex-column align-items-center" style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="70%">
                <PieChart>
                  <Pie data={agentUsage} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" strokeWidth={0}>
                    {agentUsage.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '0.5rem', border: '1px solid #e2e8f0', fontSize: '.85rem' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="d-flex flex-wrap justify-content-center gap-2 mt-2">
                {agentUsage.map((a) => (
                  <span key={a.name} className="d-inline-flex align-items-center gap-1 fs-xs text-muted">
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: a.color }} />
                    {a.name}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Col>
      </Row>

      {/* Response Times + Recent Conversations */}
      <Row className="g-3">
        {/* Response Times */}
        <Col xl={4}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>Avg Response Time</h5>
            </div>
            <div className="data-card-body" style={{ height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { day: 'Mon', time: 2.4 },
                  { day: 'Tue', time: 1.8 },
                  { day: 'Wed', time: 2.1 },
                  { day: 'Thu', time: 1.5 },
                  { day: 'Fri', time: 1.9 },
                  { day: 'Sat', time: 3.2 },
                  { day: 'Sun', time: 4.1 },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} unit="s" />
                  <Tooltip contentStyle={{ borderRadius: '0.5rem', border: '1px solid #e2e8f0', fontSize: '.85rem' }} />
                  <Bar dataKey="time" fill="#25d366" radius={[4, 4, 0, 0]} barSize={28} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Col>

        {/* Recent Conversations Table */}
        <Col xl={8}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>Recent Conversations</h5>
              <a href="/conversations" className="text-decoration-none fs-sm text-wa-green">View all</a>
            </div>
            <div className="table-responsive">
              <table className="table table-custom mb-0">
                <thead>
                  <tr>
                    <th>Contact</th>
                    <th>Status</th>
                    <th>Agent</th>
                    <th>Messages</th>
                    <th>Last Activity</th>
                  </tr>
                </thead>
                <tbody>
                  {recentConversations.map((c) => (
                    <tr key={c.id}>
                      <td>
                        <div className="d-flex align-items-center gap-2">
                          <div className="chat-avatar" style={{ width: 32, height: 32, fontSize: '.7rem' }}>
                            {c.name.split(' ').map(n => n[0]).join('')}
                          </div>
                          <div>
                            <div className="fw-semibold" style={{ fontSize: '.85rem' }}>{c.name}</div>
                            <div className="text-muted" style={{ fontSize: '.7rem' }}>{c.phone}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <Badge bg={statusColors[c.status] || 'secondary'} className="badge-status">
                          {c.status.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td style={{ fontSize: '.85rem' }}>{c.agent}</td>
                      <td style={{ fontSize: '.85rem' }}>{c.messages}</td>
                      <td className="text-muted" style={{ fontSize: '.8rem' }}>{c.time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Col>
      </Row>
    </div>
  )
}
