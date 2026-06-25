"use client"

import { useState } from "react"
import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { cn, getInitials } from "@/lib/utils"
import { useTickets } from "@/hooks/useQueries"
import { CreateTicketModal } from "@/components/modals/CreateTicketModal"
import {
  Plus,
  Search,
  Filter,
  Clock,
  User,
  MessageSquare,
  MoreHorizontal,
  AlertCircle,
  CheckCircle2,
  Timer,
  Tag,
  ChevronRight,
} from "lucide-react"

const STATUS_FILTERS: { label: string; value: string | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Open", value: "open" },
  { label: "In Progress", value: "in_progress" },
  { label: "Awaiting Reply", value: "waiting_on_customer" },
  { label: "Resolved", value: "resolved" },
  { label: "Closed", value: "closed" },
]

export default function TicketsPage() {
  const [activeFilter, setActiveFilter] = useState<string>("all")
  const [selectedTicket, setSelectedTicket] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [isModalOpen, setIsModalOpen] = useState(false)

  const { data: ticketsData = [], isLoading } = useTickets({
    status: activeFilter === "all" ? undefined : activeFilter,
  })

  const tickets = Array.isArray(ticketsData) ? ticketsData : []

  const filteredTickets = tickets.filter((t: any) => {
    const matchesSearch = (t.title?.toLowerCase() || "").includes(searchQuery.toLowerCase()) || 
                          (t.contact_name?.toLowerCase() || t.contactName?.toLowerCase() || "").includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  // Count by status (using frontend filtering for the stats)
  const openCount = tickets.filter((t: any) => t.status === "open").length
  const progressCount = tickets.filter((t: any) => t.status === "in_progress").length
  const urgentCount = tickets.filter((t: any) => t.priority === "urgent").length

  return (
    <div className="flex flex-col h-full">
      <TopBar
        title="Tickets"
        subtitle={`${tickets.length} total tickets`}
        actions={
          <button 
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-4 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(37,211,102,0.15)]"
          >
            <Plus className="w-4 h-4" />
            New Ticket
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">

          {/* ═══ Quick Stats ═══ */}
          <div className="grid grid-cols-3 gap-4 opacity-0 animate-fade-in-up">
            <div className="glass-card-sm p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-wa-green/10 border border-wa-green/20 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-wa-green" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{openCount}</p>
                <p className="text-xs text-slate-500">Open Tickets</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-wa-blue/10 border border-wa-blue/20 flex items-center justify-center">
                <Timer className="w-5 h-5 text-wa-blue" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{progressCount}</p>
                <p className="text-xs text-slate-500">In Progress</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-wa-rose/10 border border-wa-rose/20 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-wa-rose" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{urgentCount}</p>
                <p className="text-xs text-slate-500">Urgent</p>
              </div>
            </div>
          </div>

          {/* ═══ Filters ═══ */}
          <div className="flex items-center justify-between opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            <div className="flex gap-1.5">
              {STATUS_FILTERS.map((f) => (
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
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-56 h-9 pl-9 pr-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/30 transition-all"
              />
            </div>
          </div>

          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Loading tickets...</div>
          ) : (
            <div className="glass-card overflow-hidden opacity-0 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
              <table className="w-full">
              <thead>
                <tr className="border-b border-foreground/[0.06]">
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4 pl-6">Ticket</th>
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4">Status</th>
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4">Priority</th>
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4">Contact</th>
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4">Assigned</th>
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4">Updated</th>
                  <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4 pr-6"></th>
                </tr>
              </thead>
              <tbody>
                {filteredTickets.map((ticket, i) => (
                  <tr
                    key={ticket.id}
                    onClick={() => setSelectedTicket(selectedTicket === ticket.id ? null : ticket.id)}
                    className={cn(
                      "border-b border-foreground/[0.03] cursor-pointer transition-all group",
                      selectedTicket === ticket.id ? "bg-wa-green/[0.04]" : "hover:bg-foreground/[0.02]"
                    )}
                  >
                    <td className="py-4 pl-6">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] text-slate-500 font-mono">{ticket.id.split("-")[0]}</span>
                          {ticket.conversation_id && (
                            <div title="Linked to conversation">
                              <MessageSquare className="w-3 h-3 text-wa-teal" />
                            </div>
                          )}
                        </div>
                        <p className="text-sm font-medium text-foreground group-hover:text-wa-green transition-colors">{ticket.title}</p>
                        {selectedTicket === ticket.id && (
                          <p className="text-xs text-slate-500 mt-1 max-w-[300px] animate-fade-in">{ticket.description}</p>
                        )}
                      </div>
                    </td>
                    <td className="py-4"><StatusBadge status={ticket.status} /></td>
                    <td className="py-4"><StatusBadge status={ticket.priority} /></td>
                    <td className="py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-wa-green/20 to-wa-teal/20 flex items-center justify-center text-[10px] font-bold text-wa-green border border-wa-green/10">
                          {getInitials(ticket.contact_name || ticket.contactName || "?")}
                        </div>
                        <div>
                          <p className="text-xs text-foreground">{ticket.contact_name || ticket.contactName}</p>
                          <p className="text-[10px] text-slate-500">{ticket.contact_phone || ticket.contactPhone}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4">
                      {ticket.assigned_user_id || ticket.assignedUser ? (
                        <div className="flex items-center gap-1.5">
                          <User className="w-3 h-3 text-slate-500" />
                          <span className="text-xs text-slate-300">Human Agent</span>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-600 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-4">
                      <span className="text-[10px] text-slate-500">{new Date(ticket.updated_at || ticket.updatedAt || new Date()).toLocaleDateString()}</span>
                    </td>
                    <td className="py-4 pr-6">
                      <button className="w-7 h-7 rounded-lg bg-foreground/[0.04] flex items-center justify-center text-slate-500 hover:text-foreground hover:bg-foreground/[0.08] transition-colors opacity-0 group-hover:opacity-100">
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          )}
        </div>
      </div>
      <CreateTicketModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
