import { useState, useEffect } from 'react'
import { Row, Col, Form } from 'react-bootstrap'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsService } from '@services/settingsService'
import toast from 'react-hot-toast'
import { PageWrapper } from '@components/PageWrapper'
export default function Settings() {
  const qc = useQueryClient()

  // 1. Fetch Settings
  const { data: settingsData, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsService.get(),
  })

  // 2. Update Settings Mutation
  const updateMutation = useMutation({
    mutationFn: (updatedSettings: Record<string, any>) => settingsService.update(updatedSettings),
    onSuccess: () => {
      toast.success('Settings saved successfully')
      qc.invalidateQueries({ queryKey: ['settings'] })
    },
    onError: () => {
      toast.error('Failed to save settings')
    },
  })

  // Form local states
  const [phoneNumberId, setPhoneNumberId] = useState('')
  const [wabaId, setWabaId] = useState('')
  const [verifyToken, setVerifyToken] = useState('')

  const [provider, setProvider] = useState('Google Gemini')
  const [ollamaUrl, setOllamaUrl] = useState('')
  const [apiKey, setApiKey] = useState('')

  const [require2FA, setRequire2FA] = useState(false)
  const [rateLimiting, setRateLimiting] = useState(true)

  const [emailAlerts, setEmailAlerts] = useState(true)
  const [escalationAlerts, setEscalationAlerts] = useState(true)
  const [dailySummary, setDailySummary] = useState(false)

  // Sync state with query response
  useEffect(() => {
    if (settingsData) {
      const wa = settingsData.whatsapp || {}
      setPhoneNumberId(wa.phone_number_id || '')
      setWabaId(wa.waba_id || '')
      setVerifyToken(wa.webhook_verify_token || '')

      const ai = settingsData.ai || {}
      setProvider(ai.default_provider || 'Google Gemini')
      setOllamaUrl(ai.ollama_base_url || 'http://localhost:11434')
      setApiKey(ai.google_api_key || '')

      const sec = settingsData.security || {}
      setRequire2FA(!!sec.require_2fa)
      setRateLimiting(sec.rate_limiting !== false)

      const notif = settingsData.notifications || {}
      setEmailAlerts(notif.email_alerts !== false)
      setEscalationAlerts(notif.escalation_alerts !== false)
      setDailySummary(!!notif.daily_summary)
    }
  }, [settingsData])

  const handleSaveWhatsApp = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({
      whatsapp: {
        phone_number_id: phoneNumberId,
        waba_id: wabaId,
        webhook_verify_token: verifyToken,
      },
    })
  }

  const handleSaveAI = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({
      ai: {
        default_provider: provider,
        ollama_base_url: ollamaUrl,
        google_api_key: apiKey,
      },
    })
  }

  const handleSaveSecurity = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({
      security: {
        require_2fa: require2FA,
        rate_limiting: rateLimiting,
      },
    })
  }

  const handleSaveNotifications = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({
      notifications: {
        email_alerts: emailAlerts,
        escalation_alerts: escalationAlerts,
        daily_summary: dailySummary,
      },
    })
  }

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center py-5">
        <div className="spinner-border text-success" role="status" />
      </div>
    )
  }

  return (
    <PageWrapper>
      <div className="mb-4">
        <h4 className="fw-bold mb-1">Settings</h4>
        <p className="text-muted mb-0 fs-sm">Configure your platform settings</p>
      </div>

      <Row className="g-4 stagger-children">
        {/* WhatsApp Card */}
        <Col xl={6}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>
                <i className="bi bi-whatsapp me-2" />WhatsApp Configuration
              </h5>
            </div>
            <div className="data-card-body">
              <Form onSubmit={handleSaveWhatsApp}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold fs-xs">Phone Number ID</Form.Label>
                  <Form.Control
                    value={phoneNumberId}
                    onChange={(e) => setPhoneNumberId(e.target.value)}
                    placeholder="Enter Phone Number ID"
                    style={{ borderRadius: '.5rem' }}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold fs-xs">Business Account ID (WABA ID)</Form.Label>
                  <Form.Control
                    value={wabaId}
                    onChange={(e) => setWabaId(e.target.value)}
                    placeholder="Enter WABA ID"
                    style={{ borderRadius: '.5rem' }}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold fs-xs">Webhook Verify Token</Form.Label>
                  <Form.Control
                    type="password"
                    value={verifyToken}
                    onChange={(e) => setVerifyToken(e.target.value)}
                    placeholder="Enter Webhook Verify Token"
                    style={{ borderRadius: '.5rem' }}
                  />
                </Form.Group>
                <button type="submit" className="btn btn-wa-primary" disabled={updateMutation.isPending}>
                  Save Changes
                </button>
              </Form>
            </div>
          </div>
        </Col>

        {/* AI Configuration Card */}
        <Col xl={6}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>
                <i className="bi bi-robot me-2" />AI Provider Settings
              </h5>
            </div>
            <div className="data-card-body">
              <Form onSubmit={handleSaveAI}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold fs-xs">Default Provider</Form.Label>
                  <Form.Select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    style={{ borderRadius: '.5rem' }}
                  >
                    <option value="Google Gemini">Google Gemini</option>
                    <option value="Ollama (Local)">Ollama (Local)</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold fs-xs">Ollama Base URL</Form.Label>
                  <Form.Control
                    value={ollamaUrl}
                    onChange={(e) => setOllamaUrl(e.target.value)}
                    placeholder="http://localhost:11434"
                    style={{ borderRadius: '.5rem' }}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold fs-xs">Google AI API Key</Form.Label>
                  <Form.Control
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter API key"
                    style={{ borderRadius: '.5rem' }}
                  />
                </Form.Group>
                <button type="submit" className="btn btn-wa-primary" disabled={updateMutation.isPending}>
                  Save Changes
                </button>
              </Form>
            </div>
          </div>
        </Col>

        {/* Security Settings Card */}
        <Col xl={6}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>
                <i className="bi bi-shield-lock me-2" />Security Settings
              </h5>
            </div>
            <div className="data-card-body">
              <Form onSubmit={handleSaveSecurity}>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <div className="fw-semibold fs-sm">Two-Factor Authentication</div>
                    <div className="text-muted fs-xs">Require 2FA for all users</div>
                  </div>
                  <Form.Check
                    type="switch"
                    id="2fa"
                    checked={require2FA}
                    onChange={(e) => setRequire2FA(e.target.checked)}
                  />
                </div>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <div className="fw-semibold fs-sm">Rate Limiting</div>
                    <div className="text-muted fs-xs">Enforce Nginx rate restricts per user IP</div>
                  </div>
                  <Form.Check
                    type="switch"
                    id="rate"
                    checked={rateLimiting}
                    onChange={(e) => setRateLimiting(e.target.checked)}
                  />
                </div>
                <button type="submit" className="btn btn-wa-primary" disabled={updateMutation.isPending}>
                  Save Security
                </button>
              </Form>
            </div>
          </div>
        </Col>

        {/* Notifications Card */}
        <Col xl={6}>
          <div className="data-card">
            <div className="data-card-header">
              <h5>
                <i className="bi bi-bell me-2" />Notification Settings
              </h5>
            </div>
            <div className="data-card-body">
              <Form onSubmit={handleSaveNotifications}>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <div className="fw-semibold fs-sm">Email Notifications</div>
                    <div className="text-muted fs-xs">Send email for critical events</div>
                  </div>
                  <Form.Check
                    type="switch"
                    checked={emailAlerts}
                    onChange={(e) => setEmailAlerts(e.target.checked)}
                    id="notif-email"
                  />
                </div>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <div className="fw-semibold fs-sm">Escalation Alerts</div>
                    <div className="text-muted fs-xs">Notify on ticket escalation</div>
                  </div>
                  <Form.Check
                    type="switch"
                    checked={escalationAlerts}
                    onChange={(e) => setEscalationAlerts(e.target.checked)}
                    id="notif-escalate"
                  />
                </div>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <div className="fw-semibold fs-sm">Daily Summary</div>
                    <div className="text-muted fs-xs">Send daily platform summary</div>
                  </div>
                  <Form.Check
                    type="switch"
                    checked={dailySummary}
                    onChange={(e) => setDailySummary(e.target.checked)}
                    id="notif-summary"
                  />
                </div>
                <button type="submit" className="btn btn-wa-primary" disabled={updateMutation.isPending}>
                  Save Notifications
                </button>
              </Form>
            </div>
          </div>
        </Col>
      </Row>
    </PageWrapper>
  )
}
