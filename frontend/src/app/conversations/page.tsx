"use client"

import { useState } from "react"
import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { cn, getInitials, timeAgo } from "@/lib/utils"
import { useConversations, useMessages } from "@/hooks/useQueries"
import {
  MessageSquare,
  Search,
  Filter,
  Bot,
  User,
  Phone,
  Send,
  Paperclip,
  Smile,
  MoreVertical,
  ArrowLeft,
  Tag,
  Clock,
  Hash,
  ChevronDown,
} from "lucide-react"

const FILTERS: { label: string; value: string | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Active", value: "active" },
  { label: "AI Handling", value: "bot_handling" },
  { label: "Human", value: "human_handling" },
  { label: "Escalated", value: "escalated" },
  { label: "Waiting", value: "waiting" },
  { label: "Resolved", value: "resolved" },
]

import { api } from "@/lib/api"

// Mock messages removed

export default function ConversationsPage() {
  const [activeFilter, setActiveFilter] = useState<string>("all")
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [messageText, setMessageText] = useState("")
  const [isSending, setIsSending] = useState(false)

  const { data: convsData = [], isLoading: isConvsLoading } = useConversations({
    status: activeFilter === "all" ? undefined : activeFilter,
    search: searchQuery || undefined,
  })
  
  const conversations = Array.isArray(convsData) ? convsData : []

  const { data: messagesData = [], isLoading: isMessagesLoading } = useMessages(selectedConvId)
  const messages = Array.isArray(messagesData) ? messagesData : []

  const selectedConversation = conversations.find((c: any) => c.id === selectedConvId) || conversations[0]

  // Default selection if none selected and data available
  if (!selectedConvId && conversations.length > 0) {
    setSelectedConvId(conversations[0].id)
  }

  const filteredConversations = conversations

  const handleSendMessage = async () => {
    if (!messageText.trim() || !selectedConversation || isSending) return
    setIsSending(true)
    try {
      await api.post("/whatsapp/send", {
        phone: selectedConversation.contact_phone || selectedConversation.contactPhone,
        message: messageText
      })
      setMessageText("")
    } catch (err) {
      console.error("Failed to send message", err)
    } finally {
      setIsSending(false)
    }
  }

  const handleResolve = async () => {
    if (!selectedConversation) return
    try {
      await api.post(`/conversations/${selectedConversation.id}/resolve`)
      // It will auto refetch due to useConversations
    } catch (err) {
      console.error("Failed to resolve", err)
    }
  }

  const handleEscalate = async () => {
    if (!selectedConversation) return
    try {
      await api.post(`/conversations/${selectedConversation.id}/escalate`)
    } catch (err) {
      console.error("Failed to escalate", err)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Conversations" subtitle={`${conversations.length} active threads`} />

      <div className="flex-1 flex overflow-hidden">
        {/* ── Conversation List ────────────────── */}
        <div className="w-[380px] flex-shrink-0 border-r border-foreground/[0.06] flex flex-col bg-card/40">
          {/* Search & Filter */}
          <div className="p-4 border-b border-foreground/[0.06] space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-9 pl-9 pr-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/30 transition-all"
              />
            </div>
            <div className="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
              {FILTERS.map((f) => (
                <button
                  key={f.value}
                  onClick={() => setActiveFilter(f.value)}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-[11px] font-medium whitespace-nowrap transition-all border",
                    activeFilter === f.value
                      ? "bg-wa-green/15 text-wa-green border-wa-green/20"
                      : "bg-foreground/[0.03] text-slate-400 border-transparent hover:bg-foreground/[0.06] hover:text-foreground"
                  )}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto no-scrollbar">
            {isConvsLoading ? (
              <div className="p-8 text-center text-slate-500 text-sm">Loading conversations...</div>
            ) : filteredConversations.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-sm">No conversations found.</div>
            ) : filteredConversations.map((conv: any) => (
              <div
                key={conv.id}
                onClick={() => setSelectedConvId(conv.id)}
                className={cn(
                  "flex items-start gap-3 px-4 py-4 cursor-pointer transition-all border-b border-foreground/[0.03] group",
                  selectedConvId === conv.id
                    ? "bg-wa-green/[0.06] border-l-2 border-l-wa-green"
                    : "hover:bg-foreground/[0.02] border-l-2 border-l-transparent"
                )}
              >
                <div className="relative flex-shrink-0">
                  <div className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold border",
                    conv.assigned_agent_id
                      ? "bg-gradient-to-br from-wa-purple/20 to-wa-blue/20 text-wa-purple border-wa-purple/15"
                      : "bg-gradient-to-br from-wa-green/20 to-wa-teal/20 text-wa-green border-wa-green/15"
                  )}>
                    {getInitials(conv.contact_name || conv.contactName || "?")}
                  </div>
                  {conv.assigned_agent_id && (
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-wa-purple rounded-full border-2 border-[#020617] flex items-center justify-center">
                      <Bot className="w-2.5 h-2.5 text-foreground" />
                    </div>
                  )}
                  {!conv.assigned_agent_id && conv.status !== "resolved" && (
                    <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-wa-green rounded-full border-2 border-[#020617]" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <p className={cn(
                      "text-sm font-medium truncate transition-colors",
                      selectedConvId === conv.id ? "text-wa-green" : "text-foreground group-hover:text-wa-green"
                    )}>
                      {conv.contact_name || conv.contactName}
                    </p>
                    <span className="text-[9px] text-slate-600 whitespace-nowrap">{timeAgo(conv.updated_at || conv.lastMessageAt || new Date())}</span>
                  </div>
                  <p className="text-xs text-slate-500 truncate mb-2">{conv.lastMessage || `${conv.message_count || 0} messages`}</p>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={conv.status} />
                    {conv.priority === "urgent" && <StatusBadge status="urgent" />}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Chat View ───────────────────────── */}
        {selectedConversation ? (
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="h-16 flex items-center justify-between px-6 border-b border-foreground/[0.06] bg-card/40">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-wa-green/20 to-wa-teal/20 flex items-center justify-center text-sm font-bold text-wa-green border border-wa-green/15">
                  {getInitials(selectedConversation.contact_name || selectedConversation.contactName)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-foreground">{selectedConversation.contact_name || selectedConversation.contactName}</h3>
                    <StatusBadge status={selectedConversation.status} />
                  </div>
                  <p className="text-[10px] text-slate-500 flex items-center gap-1.5">
                    <Phone className="w-3 h-3" />
                    {selectedConversation.contact_phone || selectedConversation.contactPhone}
                    {selectedConversation.assigned_agent_id && (
                      <>
                        <span className="text-slate-600">•</span>
                        <Bot className="w-3 h-3 text-wa-purple" />
                        <span className="text-wa-purple">AI Agent</span>
                      </>
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleEscalate}
                  className="px-3 h-8 rounded-lg bg-wa-rose/10 border border-wa-rose/20 flex items-center justify-center text-wa-rose hover:bg-wa-rose/20 transition-colors text-xs font-semibold"
                >
                  Escalate
                </button>
                <button
                  onClick={handleResolve}
                  className="px-3 h-8 rounded-lg bg-wa-green/10 border border-wa-green/20 flex items-center justify-center text-wa-green hover:bg-wa-green/20 transition-colors text-xs font-semibold"
                >
                  Resolve
                </button>
                <button className="w-8 h-8 rounded-lg bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground transition-colors ml-2">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 no-scrollbar">
              <div className="flex justify-center mb-4">
                <span className="text-[10px] text-slate-600 bg-slate-900/80 px-3 py-1 rounded-full border border-foreground/[0.06]">Today</span>
              </div>
              {messages.length === 0 && !isMessagesLoading && (
                <div className="text-center text-slate-500 text-sm mt-10">No messages in this conversation yet.</div>
              )}
              {messages.map((msg: any) => (
                <div
                  key={msg.id}
                  className={cn(
                    "flex",
                    msg.direction === "outbound" ? "justify-end" : "justify-start"
                  )}
                >
                  <div className={cn(
                    "max-w-[70%] px-4 py-3 rounded-2xl text-sm leading-relaxed",
                    msg.direction === "outbound"
                      ? "bg-gradient-to-br from-wa-green/20 to-wa-teal/15 text-foreground border border-wa-green/15 rounded-br-md"
                      : "bg-foreground/[0.06] text-slate-200 border border-foreground/[0.08] rounded-bl-md"
                  )}>
                    <p>{msg.content || msg.body}</p>
                    <div className={cn(
                      "flex items-center gap-1.5 mt-1.5",
                      msg.direction === "outbound" ? "justify-end" : "justify-start"
                    )}>
                      {msg.ai_generated && (
                        <span className="flex items-center gap-0.5 text-[9px] text-wa-purple">
                          <Bot className="w-2.5 h-2.5" /> AI
                        </span>
                      )}
                      <span className="text-[9px] text-slate-600">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-foreground/[0.06] bg-card/40">
              <div className="flex items-center gap-3">
                <button className="w-9 h-9 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground transition-colors flex-shrink-0">
                  <Paperclip className="w-4 h-4" />
                </button>
                <div className="flex-1 relative">
                  <input
                    type="text"
                    placeholder="Type a message..."
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="w-full h-10 px-4 pr-10 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/30 transition-all"
                  />
                  <button className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-foreground transition-colors">
                    <Smile className="w-5 h-5" />
                  </button>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={isSending || !messageText.trim()}
                  className="w-10 h-10 rounded-xl bg-wa-green hover:bg-wa-green-dark disabled:opacity-50 flex items-center justify-center text-slate-950 transition-colors shadow-[0_0_15px_rgba(37,211,102,0.2)] flex-shrink-0"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageSquare className="w-12 h-12 text-slate-700 mx-auto mb-3" />
              <p className="text-slate-500">Select a conversation to view</p>
            </div>
          </div>
        )}

        {/* ── Contact Details Sidebar ─────────── */}
        {selectedConversation && (
          <div className="w-[280px] flex-shrink-0 border-l border-foreground/[0.06] bg-card/40 p-5 overflow-y-auto no-scrollbar">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Contact Details</h4>

            <div className="text-center mb-6">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-wa-green/20 to-wa-teal/20 flex items-center justify-center text-lg font-bold text-wa-green border border-wa-green/15 mx-auto mb-3">
                {getInitials(selectedConversation.contact_name || selectedConversation.contactName)}
              </div>
              <p className="text-sm font-semibold text-foreground">{selectedConversation.contact_name || selectedConversation.contactName}</p>
              <p className="text-xs text-slate-500">{selectedConversation.contact_phone || selectedConversation.contactPhone}</p>
            </div>

            <div className="space-y-4">
              <div className="glass-card-sm p-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Status</p>
                <StatusBadge status={selectedConversation.status} size="md" />
              </div>
              <div className="glass-card-sm p-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Priority</p>
                <StatusBadge status={selectedConversation.priority} size="md" />
              </div>
              <div className="glass-card-sm p-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Messages</p>
                <p className="text-lg font-bold text-foreground">{selectedConversation.messageCount}</p>
              </div>
              <div className="glass-card-sm p-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Tags</p>
                <div className="flex flex-wrap gap-1.5">
                  {(selectedConversation.tags || []).map((tag: string) => (
                    <span key={tag} className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-foreground/[0.04] text-[10px] text-slate-400 border border-foreground/[0.06]">
                      <Hash className="w-2.5 h-2.5" />
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              <div className="glass-card-sm p-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Assigned To</p>
                <p className="text-sm text-foreground">
                  {selectedConversation.assigned_agent_id ? "AI Agent" : selectedConversation.assigned_user_id ? "Human User" : "Unassigned"}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
