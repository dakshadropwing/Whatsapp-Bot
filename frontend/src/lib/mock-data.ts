/**
 * Mock data simulating real backend API responses.
 * Replace with actual API calls when backend is connected.
 */

// ── Dashboard Stats ─────────────────────────────────
export const dashboardStats = {
  totalConversations: 2847,
  activeTickets: 156,
  aiResolutionRate: 87.3,
  avgResponseTime: 1.2,
  totalMessages: 18429,
  activeAgents: 6,
  trends: {
    conversations: +12.5,
    tickets: -2.4,
    resolution: +5.1,
    responseTime: -10.5,
    messages: +8.7,
    agents: 0,
  },
}

// ── Message Traffic Chart Data ──────────────────────
export const messageTrafficData = [
  { hour: "00:00", inbound: 12, outbound: 8 },
  { hour: "02:00", inbound: 5, outbound: 3 },
  { hour: "04:00", inbound: 3, outbound: 2 },
  { hour: "06:00", inbound: 18, outbound: 15 },
  { hour: "08:00", inbound: 45, outbound: 38 },
  { hour: "09:00", inbound: 72, outbound: 65 },
  { hour: "10:00", inbound: 98, outbound: 89 },
  { hour: "11:00", inbound: 115, outbound: 102 },
  { hour: "12:00", inbound: 88, outbound: 78 },
  { hour: "13:00", inbound: 95, outbound: 84 },
  { hour: "14:00", inbound: 108, outbound: 96 },
  { hour: "15:00", inbound: 120, outbound: 110 },
  { hour: "16:00", inbound: 85, outbound: 72 },
  { hour: "17:00", inbound: 62, outbound: 54 },
  { hour: "18:00", inbound: 48, outbound: 40 },
  { hour: "20:00", inbound: 32, outbound: 25 },
  { hour: "22:00", inbound: 18, outbound: 12 },
]

// ── Weekly Stats for mini sparklines ─────────────────
export const weeklyStats = [
  { day: "Mon", value: 420 },
  { day: "Tue", value: 380 },
  { day: "Wed", value: 510 },
  { day: "Thu", value: 460 },
  { day: "Fri", value: 590 },
  { day: "Sat", value: 340 },
  { day: "Sun", value: 280 },
]

// ── Conversations ───────────────────────────────────
export type ConversationStatus = "active" | "waiting" | "bot_handling" | "human_handling" | "escalated" | "resolved" | "closed"

export interface Conversation {
  id: string
  contactName: string
  contactPhone: string
  status: ConversationStatus
  lastMessage: string
  lastMessageAt: number // minutes ago
  assignedAgent: string | null
  assignedUser: string | null
  priority: "low" | "normal" | "high" | "urgent"
  messageCount: number
  tags: string[]
  isAiHandled: boolean
  channel: "whatsapp" | "whatsapp_business"
}

export const conversations: Conversation[] = [
  {
    id: "conv-001",
    contactName: "Priya Sharma",
    contactPhone: "+91 98765 43210",
    status: "active",
    lastMessage: "I need help tracking my order #WH-4521",
    lastMessageAt: 2,
    assignedAgent: "Support Agent",
    assignedUser: null,
    priority: "high",
    messageCount: 12,
    tags: ["order-tracking", "priority"],
    isAiHandled: true,
    channel: "whatsapp_business",
  },
  {
    id: "conv-002",
    contactName: "Rahul Patel",
    contactPhone: "+91 87654 32109",
    status: "bot_handling",
    lastMessage: "What are your business hours?",
    lastMessageAt: 5,
    assignedAgent: "Knowledge Agent",
    assignedUser: null,
    priority: "normal",
    messageCount: 4,
    tags: ["faq"],
    isAiHandled: true,
    channel: "whatsapp",
  },
  {
    id: "conv-003",
    contactName: "Sneha Gupta",
    contactPhone: "+91 76543 21098",
    status: "human_handling",
    lastMessage: "I want to speak to a manager regarding my refund",
    lastMessageAt: 8,
    assignedAgent: null,
    assignedUser: "Amit Kumar",
    priority: "urgent",
    messageCount: 23,
    tags: ["refund", "escalated", "vip"],
    isAiHandled: false,
    channel: "whatsapp_business",
  },
  {
    id: "conv-004",
    contactName: "Vikram Singh",
    contactPhone: "+91 65432 10987",
    status: "waiting",
    lastMessage: "Thanks, I'll check and get back to you.",
    lastMessageAt: 35,
    assignedAgent: "Sales Agent",
    assignedUser: null,
    priority: "normal",
    messageCount: 8,
    tags: ["sales", "follow-up"],
    isAiHandled: true,
    channel: "whatsapp",
  },
  {
    id: "conv-005",
    contactName: "Ananya Reddy",
    contactPhone: "+91 54321 09876",
    status: "escalated",
    lastMessage: "The product I received is damaged. This is unacceptable!",
    lastMessageAt: 12,
    assignedAgent: null,
    assignedUser: "Priya Mehta",
    priority: "urgent",
    messageCount: 18,
    tags: ["complaint", "damaged-product", "urgent"],
    isAiHandled: false,
    channel: "whatsapp_business",
  },
  {
    id: "conv-006",
    contactName: "Arjun Nair",
    contactPhone: "+91 43210 98765",
    status: "active",
    lastMessage: "Can you recommend something similar to product XZ-100?",
    lastMessageAt: 1,
    assignedAgent: "Sales Agent",
    assignedUser: null,
    priority: "normal",
    messageCount: 6,
    tags: ["recommendation", "sales"],
    isAiHandled: true,
    channel: "whatsapp",
  },
  {
    id: "conv-007",
    contactName: "Meera Joshi",
    contactPhone: "+91 32109 87654",
    status: "resolved",
    lastMessage: "Thank you so much! That resolved my issue.",
    lastMessageAt: 120,
    assignedAgent: "Support Agent",
    assignedUser: null,
    priority: "low",
    messageCount: 9,
    tags: ["resolved", "positive-feedback"],
    isAiHandled: true,
    channel: "whatsapp_business",
  },
  {
    id: "conv-008",
    contactName: "Karan Malhotra",
    contactPhone: "+91 21098 76543",
    status: "bot_handling",
    lastMessage: "I want to schedule an appointment for next Tuesday",
    lastMessageAt: 3,
    assignedAgent: "Appointment Agent",
    assignedUser: null,
    priority: "normal",
    messageCount: 5,
    tags: ["appointment", "scheduling"],
    isAiHandled: true,
    channel: "whatsapp",
  },
]

// ── Tickets ─────────────────────────────────────────
export type TicketStatus = "open" | "in_progress" | "waiting_on_customer" | "resolved" | "closed"
export type TicketPriority = "low" | "medium" | "high" | "urgent"

export interface Ticket {
  id: string
  title: string
  description: string
  status: TicketStatus
  priority: TicketPriority
  contactName: string
  contactPhone: string
  assignedUser: string | null
  conversationId: string | null
  createdAt: string
  updatedAt: string
}

export const tickets: Ticket[] = [
  {
    id: "TKT-001",
    title: "Order #WH-4521 not delivered",
    description: "Customer reports order placed 5 days ago still showing 'processing' status.",
    status: "open",
    priority: "high",
    contactName: "Priya Sharma",
    contactPhone: "+91 98765 43210",
    assignedUser: null,
    conversationId: "conv-001",
    createdAt: "2026-06-21T04:30:00Z",
    updatedAt: "2026-06-21T05:15:00Z",
  },
  {
    id: "TKT-002",
    title: "Refund request — wrong item shipped",
    description: "Customer received incorrect product. Requesting full refund and return pickup.",
    status: "in_progress",
    priority: "urgent",
    contactName: "Sneha Gupta",
    contactPhone: "+91 76543 21098",
    assignedUser: "Amit Kumar",
    conversationId: "conv-003",
    createdAt: "2026-06-21T02:00:00Z",
    updatedAt: "2026-06-21T05:45:00Z",
  },
  {
    id: "TKT-003",
    title: "Product quality complaint",
    description: "Damaged product received. Customer is very upset and requesting immediate replacement.",
    status: "in_progress",
    priority: "urgent",
    contactName: "Ananya Reddy",
    contactPhone: "+91 54321 09876",
    assignedUser: "Priya Mehta",
    conversationId: "conv-005",
    createdAt: "2026-06-21T03:20:00Z",
    updatedAt: "2026-06-21T05:50:00Z",
  },
  {
    id: "TKT-004",
    title: "Account login issue",
    description: "Customer unable to log into their account after password reset.",
    status: "waiting_on_customer",
    priority: "medium",
    contactName: "Rohit Kapoor",
    contactPhone: "+91 91234 56789",
    assignedUser: "Neha Agarwal",
    conversationId: null,
    createdAt: "2026-06-20T18:00:00Z",
    updatedAt: "2026-06-21T04:00:00Z",
  },
  {
    id: "TKT-005",
    title: "Billing discrepancy on invoice #INV-789",
    description: "Customer was charged twice for subscription renewal.",
    status: "open",
    priority: "high",
    contactName: "Deepa Menon",
    contactPhone: "+91 82345 67890",
    assignedUser: null,
    conversationId: null,
    createdAt: "2026-06-21T05:00:00Z",
    updatedAt: "2026-06-21T05:00:00Z",
  },
  {
    id: "TKT-006",
    title: "Feature request — multi-language support",
    description: "Customer requesting Hindi and Tamil language options in chat interface.",
    status: "open",
    priority: "low",
    contactName: "Sanjay Verma",
    contactPhone: "+91 73456 78901",
    assignedUser: null,
    conversationId: null,
    createdAt: "2026-06-20T12:00:00Z",
    updatedAt: "2026-06-20T12:00:00Z",
  },
  {
    id: "TKT-007",
    title: "Integration setup — Shopify webhook",
    description: "Client needs assistance configuring Shopify order notifications via WhatsApp.",
    status: "resolved",
    priority: "medium",
    contactName: "Lakshmi Iyer",
    contactPhone: "+91 64567 89012",
    assignedUser: "Amit Kumar",
    conversationId: null,
    createdAt: "2026-06-19T10:00:00Z",
    updatedAt: "2026-06-21T03:00:00Z",
  },
]

// ── AI Agents ───────────────────────────────────────
export interface AIAgent {
  id: string
  name: string
  roleType: "support" | "sales" | "lead" | "appointment" | "knowledge" | "supervisor"
  provider: "gemini" | "ollama"
  modelName: string
  isActive: boolean
  systemPromptPreview: string
  conversationsHandled: number
  avgResponseTime: number
  resolutionRate: number
}

export const aiAgents: AIAgent[] = [
  {
    id: "agent-001",
    name: "Supervisor",
    roleType: "supervisor",
    provider: "gemini",
    modelName: "gemini-2.5-flash",
    isActive: true,
    systemPromptPreview: "You are the supervisor orchestrator. Classify incoming messages and route to the appropriate specialist agent...",
    conversationsHandled: 2847,
    avgResponseTime: 0.3,
    resolutionRate: 100,
  },
  {
    id: "agent-002",
    name: "Support Agent",
    roleType: "support",
    provider: "gemini",
    modelName: "gemini-2.5-flash",
    isActive: true,
    systemPromptPreview: "You are a helpful customer support agent. Resolve issues efficiently and create tickets when needed...",
    conversationsHandled: 1245,
    avgResponseTime: 1.8,
    resolutionRate: 89.2,
  },
  {
    id: "agent-003",
    name: "Sales Agent",
    roleType: "sales",
    provider: "gemini",
    modelName: "gemini-2.5-flash",
    isActive: true,
    systemPromptPreview: "You are a product recommendation specialist. Help customers find the perfect product from our catalog...",
    conversationsHandled: 632,
    avgResponseTime: 2.1,
    resolutionRate: 76.5,
  },
  {
    id: "agent-004",
    name: "Lead Capture",
    roleType: "lead",
    provider: "gemini",
    modelName: "gemini-2.5-flash",
    isActive: true,
    systemPromptPreview: "You are a lead qualification agent. Capture contact details, understand requirements, and score leads...",
    conversationsHandled: 418,
    avgResponseTime: 1.5,
    resolutionRate: 92.1,
  },
  {
    id: "agent-005",
    name: "Appointment Bot",
    roleType: "appointment",
    provider: "gemini",
    modelName: "gemini-2.5-flash",
    isActive: true,
    systemPromptPreview: "You are an appointment scheduling assistant. Help customers book, reschedule, or cancel appointments...",
    conversationsHandled: 287,
    avgResponseTime: 1.2,
    resolutionRate: 95.8,
  },
  {
    id: "agent-006",
    name: "Knowledge Base",
    roleType: "knowledge",
    provider: "gemini",
    modelName: "gemini-2.5-flash",
    isActive: false,
    systemPromptPreview: "You are a deep search specialist. Use RAG to find accurate answers from the knowledge base...",
    conversationsHandled: 265,
    avgResponseTime: 3.2,
    resolutionRate: 82.4,
  },
]

// ── Workflows ───────────────────────────────────────
export interface Workflow {
  id: string
  name: string
  description: string
  trigger: "message_received" | "ticket_created" | "conversation_closed" | "manual" | "scheduled"
  isActive: boolean
  stepsCount: number
  runCount: number
  lastRunAt: string | null
  successRate: number
}

export const workflows: Workflow[] = [
  {
    id: "wf-001",
    name: "Welcome Message Flow",
    description: "Send personalized welcome message to first-time contacts",
    trigger: "message_received",
    isActive: true,
    stepsCount: 3,
    runCount: 1834,
    lastRunAt: "2026-06-21T05:45:00Z",
    successRate: 99.2,
  },
  {
    id: "wf-002",
    name: "Ticket Escalation",
    description: "Auto-escalate tickets unresolved for over 24 hours",
    trigger: "scheduled",
    isActive: true,
    stepsCount: 5,
    runCount: 342,
    lastRunAt: "2026-06-21T06:00:00Z",
    successRate: 97.8,
  },
  {
    id: "wf-003",
    name: "CSAT Survey",
    description: "Send customer satisfaction survey after conversation resolution",
    trigger: "conversation_closed",
    isActive: true,
    stepsCount: 4,
    runCount: 1120,
    lastRunAt: "2026-06-21T04:30:00Z",
    successRate: 95.4,
  },
  {
    id: "wf-004",
    name: "Lead Nurture Sequence",
    description: "Follow-up sequence for qualified leads over 7 days",
    trigger: "manual",
    isActive: false,
    stepsCount: 8,
    runCount: 156,
    lastRunAt: "2026-06-20T18:00:00Z",
    successRate: 88.5,
  },
  {
    id: "wf-005",
    name: "Order Status Notifier",
    description: "Notify customers when their order status changes",
    trigger: "ticket_created",
    isActive: true,
    stepsCount: 3,
    runCount: 2456,
    lastRunAt: "2026-06-21T05:50:00Z",
    successRate: 99.8,
  },
]

// ── Users ───────────────────────────────────────────
export interface PlatformUser {
  id: string
  fullName: string
  email: string
  role: "admin" | "manager" | "agent" | "viewer"
  isActive: boolean
  lastLoginAt: string | null
  conversationsAssigned: number
  ticketsResolved: number
  avatarUrl: string | null
}

export const platformUsers: PlatformUser[] = [
  {
    id: "user-001",
    fullName: "Ashwin Admin",
    email: "ashwin@neural.io",
    role: "admin",
    isActive: true,
    lastLoginAt: "2026-06-21T06:00:00Z",
    conversationsAssigned: 0,
    ticketsResolved: 0,
    avatarUrl: null,
  },
  {
    id: "user-002",
    fullName: "Amit Kumar",
    email: "amit@neural.io",
    role: "agent",
    isActive: true,
    lastLoginAt: "2026-06-21T05:30:00Z",
    conversationsAssigned: 8,
    ticketsResolved: 45,
    avatarUrl: null,
  },
  {
    id: "user-003",
    fullName: "Priya Mehta",
    email: "priya@neural.io",
    role: "agent",
    isActive: true,
    lastLoginAt: "2026-06-21T05:45:00Z",
    conversationsAssigned: 5,
    ticketsResolved: 32,
    avatarUrl: null,
  },
  {
    id: "user-004",
    fullName: "Neha Agarwal",
    email: "neha@neural.io",
    role: "agent",
    isActive: true,
    lastLoginAt: "2026-06-21T04:00:00Z",
    conversationsAssigned: 3,
    ticketsResolved: 28,
    avatarUrl: null,
  },
  {
    id: "user-005",
    fullName: "Raj Operations",
    email: "raj@neural.io",
    role: "manager",
    isActive: false,
    lastLoginAt: "2026-06-20T10:00:00Z",
    conversationsAssigned: 0,
    ticketsResolved: 12,
    avatarUrl: null,
  },
]

// ── Live Operations Feed ────────────────────────────
export interface LiveEvent {
  id: string
  type: "message" | "ticket" | "escalation" | "resolution" | "agent_switch"
  title: string
  description: string
  timeAgo: number // in minutes
  severity: "info" | "warning" | "success" | "danger"
  contactName: string
}

export const liveEvents: LiveEvent[] = [
  {
    id: "evt-001",
    type: "message",
    title: "New inbound message",
    description: "Priya Sharma: I need help tracking my order #WH-4521",
    timeAgo: 2,
    severity: "info",
    contactName: "Priya Sharma",
  },
  {
    id: "evt-002",
    type: "escalation",
    title: "Conversation escalated",
    description: "Sneha Gupta's conversation escalated to human agent",
    timeAgo: 8,
    severity: "warning",
    contactName: "Sneha Gupta",
  },
  {
    id: "evt-003",
    type: "ticket",
    title: "Ticket created",
    description: "TKT-005: Billing discrepancy on invoice #INV-789",
    timeAgo: 15,
    severity: "danger",
    contactName: "Deepa Menon",
  },
  {
    id: "evt-004",
    type: "resolution",
    title: "AI resolved conversation",
    description: "Support Agent resolved Meera Joshi's issue automatically",
    timeAgo: 45,
    severity: "success",
    contactName: "Meera Joshi",
  },
  {
    id: "evt-005",
    type: "agent_switch",
    title: "Agent reassigned",
    description: "Ananya Reddy's conversation moved to Priya Mehta",
    timeAgo: 12,
    severity: "warning",
    contactName: "Ananya Reddy",
  },
  {
    id: "evt-006",
    type: "message",
    title: "New inbound message",
    description: "Arjun Nair: Can you recommend something similar?",
    timeAgo: 1,
    severity: "info",
    contactName: "Arjun Nair",
  },
  {
    id: "evt-007",
    type: "resolution",
    title: "Ticket resolved",
    description: "TKT-007: Shopify webhook integration completed",
    timeAgo: 180,
    severity: "success",
    contactName: "Lakshmi Iyer",
  },
]

// ── Agent Performance Breakdown ─────────────────────
export const agentPerformanceData = [
  { agent: "Support", handled: 1245, resolved: 1110, pending: 135 },
  { agent: "Sales", handled: 632, resolved: 484, pending: 148 },
  { agent: "Lead", handled: 418, resolved: 385, pending: 33 },
  { agent: "Appt.", handled: 287, resolved: 275, pending: 12 },
  { agent: "Knowledge", handled: 265, resolved: 218, pending: 47 },
]

// ── Clients ─────────────────────────────────────────
export interface Client {
  id: string
  name: string
  email: string | null
  phone: string
  company: string | null
  tags: string[]
  conversationCount: number
  lastContactAt: string
}

export const clients: Client[] = [
  {
    id: "cli-001",
    name: "Priya Sharma",
    email: "priya.sharma@gmail.com",
    phone: "+91 98765 43210",
    company: "TechCorp India",
    tags: ["vip", "enterprise"],
    conversationCount: 12,
    lastContactAt: "2026-06-21T05:15:00Z",
  },
  {
    id: "cli-002",
    name: "Rahul Patel",
    email: "rahul.p@outlook.com",
    phone: "+91 87654 32109",
    company: null,
    tags: ["new"],
    conversationCount: 1,
    lastContactAt: "2026-06-21T05:55:00Z",
  },
  {
    id: "cli-003",
    name: "Sneha Gupta",
    email: "sneha.g@yahoo.com",
    phone: "+91 76543 21098",
    company: "RetailMax",
    tags: ["escalated", "high-value"],
    conversationCount: 8,
    lastContactAt: "2026-06-21T05:50:00Z",
  },
  {
    id: "cli-004",
    name: "Vikram Singh",
    email: null,
    phone: "+91 65432 10987",
    company: "AutoParts Ltd",
    tags: ["lead"],
    conversationCount: 3,
    lastContactAt: "2026-06-21T04:30:00Z",
  },
  {
    id: "cli-005",
    name: "Ananya Reddy",
    email: "ananya.r@gmail.com",
    phone: "+91 54321 09876",
    company: "DesignHub",
    tags: ["complaint", "urgent"],
    conversationCount: 5,
    lastContactAt: "2026-06-21T05:48:00Z",
  },
]
