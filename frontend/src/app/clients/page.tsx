"use client"

import { useState } from "react"
import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { cn, getInitials } from "@/lib/utils"
import { useClients } from "@/hooks/useQueries"
import { CreateClientModal } from "@/components/modals/CreateClientModal"
import {
  Plus,
  Search,
  Building2,
  Phone,
  Mail,
  MessageSquare,
  Hash,
  MoreHorizontal,
  ExternalLink,
  Calendar,
  Users,
} from "lucide-react"

export default function ClientsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [isModalOpen, setIsModalOpen] = useState(false)

  const { data: clientsData = [], isLoading } = useClients({
    search: searchQuery || undefined,
  })

  const clients = Array.isArray(clientsData) ? clientsData : []

  return (
    <div className="flex flex-col h-full">
      <TopBar
        title="Clients"
        subtitle={`${clients.length} registered contacts`}
        actions={
          <button 
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-4 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(37,211,102,0.15)]"
          >
            <Plus className="w-4 h-4" />
            Add Client
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">

          {/* ═══ Stats Row ═══ */}
          <div className="grid grid-cols-3 gap-4 opacity-0 animate-fade-in-up">
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-green/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-green/10 border border-wa-green/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Users className="w-5 h-5 text-wa-green" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{clients.length}</p>
                <p className="text-xs text-slate-500">Total Clients</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-purple/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-purple/10 border border-wa-purple/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Building2 className="w-5 h-5 text-wa-purple" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{clients.filter((c) => c.company).length}</p>
                <p className="text-xs text-slate-500">With Company</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-blue/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-blue/10 border border-wa-blue/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <MessageSquare className="w-5 h-5 text-wa-blue" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{clients.reduce((s: number, c: any) => s + (c.conversation_count || c.conversationCount || 0), 0)}</p>
                <p className="text-xs text-slate-500">Total Conversations</p>
              </div>
            </div>
          </div>

          {/* ═══ Search ═══ */}
          <div className="flex items-center justify-between opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            <h3 className="text-sm font-semibold text-foreground">All Clients</h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search clients..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-56 h-9 pl-9 pr-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/30 transition-all"
              />
            </div>
          </div>

          {/* ═══ Clients Grid ═══ */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {isLoading ? (
              <div className="col-span-full p-8 text-center text-slate-500">Loading clients...</div>
            ) : clients.length === 0 ? (
              <div className="col-span-full p-8 text-center text-slate-500">No clients found.</div>
            ) : clients.map((client: any, i: number) => (
              <div
                key={client.id}
                className="glass-card p-6 relative overflow-hidden group cursor-pointer opacity-0 animate-fade-in-up transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:border-wa-green/30"
                style={{ animationDelay: `${(i + 2) * 80}ms` }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-wa-green/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-wa-green/20 to-wa-teal/20 flex items-center justify-center text-sm font-bold text-wa-green border border-wa-green/15">
                        {getInitials(client.name)}
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-foreground group-hover:text-wa-green transition-colors">{client.name}</h3>
                        {client.company && (
                          <p className="text-xs text-slate-500 flex items-center gap-1">
                            <Building2 className="w-3 h-3" /> {client.company}
                          </p>
                        )}
                      </div>
                    </div>
                    <button className="w-7 h-7 rounded-lg bg-foreground/[0.04] flex items-center justify-center text-slate-500 hover:text-foreground transition-colors opacity-0 group-hover:opacity-100">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Phone className="w-3 h-3 text-slate-500" />
                      {client.phone}
                    </div>
                    {client.email && (
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <Mail className="w-3 h-3 text-slate-500" />
                        {client.email}
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <MessageSquare className="w-3 h-3 text-slate-500" />
                      {client.conversation_count || client.conversationCount || 0} conversations
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      Last: {client.last_contact_at || client.lastContactAt ? new Date(client.last_contact_at || client.lastContactAt).toLocaleDateString() : "Never"}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-3 border-t border-foreground/[0.06]">
                    {(client.tags || []).map((tag: string) => (
                      <span key={tag} className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-foreground/[0.04] text-[10px] text-slate-400 border border-foreground/[0.06]">
                        <Hash className="w-2.5 h-2.5" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <CreateClientModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
