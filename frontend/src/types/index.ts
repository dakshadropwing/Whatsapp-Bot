/* ── User & Auth Types ─────────────────────────────── */
export interface User {
  id: string
  email: string
  username: string
  full_name: string
  role: string
  organization_id: string
  avatar_url?: string
  last_login_at?: string
  preferences?: Record<string, unknown>
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
}

/* ── Conversation Types ────────────────────────────── */
export type ConversationStatus =
  | 'active' | 'waiting' | 'bot_handling'
  | 'human_handling' | 'escalated' | 'resolved' | 'closed'

export interface Conversation {
  id: string
  organization_id: string
  contact_phone: string
  contact_name: string | null
  contact_wa_id: string
  status: ConversationStatus
  channel: 'whatsapp' | 'whatsapp_business'
  assigned_agent_id: string | null
  assigned_user_id: string | null
  context: Record<string, unknown>
  tags: string[]
  priority: 'low' | 'normal' | 'high' | 'urgent'
  message_count: number
  last_message_at: string | null
  created_at: string
  updated_at: string
}

/* ── Message Types ─────────────────────────────────── */
export type MessageDirection = 'inbound' | 'outbound'
export type MessageType = 'text' | 'image' | 'audio' | 'video' | 'document' | 'location' | 'template'
export type MessageStatus = 'pending' | 'sent' | 'delivered' | 'read' | 'failed'

export interface Message {
  id: string
  organization_id: string
  conversation_id: string
  wa_message_id: string | null
  direction: MessageDirection
  message_type: MessageType
  status: MessageStatus
  body: string | null
  media_url: string | null
  ai_generated: boolean
  tokens_used: number | null
  processing_time_ms: number | null
  created_at: string
}

/* ── Ticket Types ──────────────────────────────────── */
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent'
export type TicketStatus = 'open' | 'in_progress' | 'waiting_on_customer' | 'resolved' | 'closed'

export interface Ticket {
  id: string
  organization_id: string
  conversation_id: string | null
  title: string
  description: string | null
  priority: TicketPriority
  status: TicketStatus
  assigned_user_id: string | null
  contact_phone: string | null
  contact_name: string | null
  created_at: string
  updated_at: string
}

/* ── Agent Types ───────────────────────────────────── */
export type AgentType = 'lead' | 'support' | 'sales' | 'project' | 'hr' | 'knowledge' | 'appointment'

export interface Agent {
  id: string
  name: string
  type: AgentType
  description: string
  is_active: boolean
  config: Record<string, unknown>
  organization_id: string
  created_at: string
  updated_at: string
}

/* ── Client Types ──────────────────────────────────── */
export interface Client {
  id: string
  organization_id: string
  name: string
  email: string | null
  phone: string
  company: string | null
  tags: string[]
  created_at: string
  updated_at: string
}

/* ── Analytics Types ───────────────────────────────── */
export interface DashboardStats {
  total_conversations: number
  active_conversations: number
  messages_today: number
  avg_response_time_ms: number
  tickets_open: number
  tickets_resolved_today: number
  ai_resolution_rate: number
  customer_satisfaction: number
}

export interface ChartDataPoint {
  label: string
  value: number
}

export interface AnalyticsOverview {
  messages_by_day: ChartDataPoint[]
  conversations_by_status: ChartDataPoint[]
  agent_usage: ChartDataPoint[]
  response_times: ChartDataPoint[]
}

/* ── Pagination ────────────────────────────────────── */
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

/* ── API Error ─────────────────────────────────────── */
export interface ApiError {
  error: string
  detail?: string
  status?: number
}

/* ── Workflow Types ────────────────────────────────── */
export interface Workflow {
  id: string
  name: string
  description: string
  trigger: string
  steps: Record<string, unknown>[]
  is_active: boolean
  organization_id: string
  created_at: string
}

/* ── Endpoint Config Types ─────────────────────────── */
export interface EndpointConfig {
  id: string
  organization_id: string
  name: string
  description: string | null
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH'
  headers: Record<string, string>
  is_active: boolean
  created_at: string
}

/* ── Knowledge Base Types ──────────────────────────── */
export interface KnowledgeBase {
  id: string
  organization_id: string
  name: string
  description: string | null
  document_count: number
  created_at: string
}

export interface Document {
  id: string
  knowledge_base_id: string
  filename: string
  file_type: string
  file_size: number
  chunk_count: number
  status: 'processing' | 'indexed' | 'failed'
  created_at: string
}

/* ── Prompt Template Types ─────────────────────────── */
export interface PromptTemplate {
  id: string
  name: string
  category: string
  system_prompt: string
  user_prompt: string
  variables: string[]
  organization_id: string
  created_at: string
}

/* ── Audit Log Types ───────────────────────────────── */
export interface AuditLog {
  id: string
  organization_id: string
  user_id: string | null
  action: string
  resource_type: string
  resource_id: string | null
  details: Record<string, unknown>
  ip_address: string | null
  created_at: string
}
