"use client"

import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { cn, getInitials } from "@/lib/utils"
import { useUsers } from "@/hooks/useQueries"
import { InviteUserModal } from "@/components/modals/InviteUserModal"
import { useState } from "react"
import {
  Plus, Search, Users, MessageSquare, Ticket, MoreHorizontal, Clock, Activity,
} from "lucide-react"

export default function UsersPage() {
  const { data: usersData = [], isLoading } = useUsers()
  const platformUsers = Array.isArray(usersData) ? usersData : []
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Users" subtitle={`${platformUsers.length} platform users`}
        actions={
          <button 
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-4 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(37,211,102,0.15)]"
          >
            <Plus className="w-4 h-4" /> Invite User
          </button>
        }
      />
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">
          <div className="grid grid-cols-4 gap-4 opacity-0 animate-fade-in-up">
            {[
              { icon: <Users className="w-5 h-5 text-wa-green" />, value: platformUsers.length, label: "Total Users", color: "wa-green" },
              { icon: <Activity className="w-5 h-5 text-wa-blue" />, value: platformUsers.filter((u: any) => u.is_active || u.isActive).length, label: "Active", color: "wa-blue" },
              { icon: <MessageSquare className="w-5 h-5 text-wa-purple" />, value: platformUsers.reduce((s: number, u: any) => s + (u.conversationsAssigned || 0), 0), label: "Assigned Chats", color: "wa-purple" },
              { icon: <Ticket className="w-5 h-5 text-wa-amber" />, value: platformUsers.reduce((s: number, u: any) => s + (u.ticketsResolved || 0), 0), label: "Tickets Resolved", color: "wa-amber" },
            ].map((stat, i) => (
              <div key={i} className={`glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-${stat.color}/30 hover:shadow-lg cursor-default group`}>
                <div className={`w-10 h-10 rounded-xl bg-${stat.color}/10 border border-${stat.color}/20 flex items-center justify-center group-hover:scale-110 transition-transform`}>
                  {stat.icon}
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground font-outfit">{stat.value}</p>
                  <p className="text-xs text-slate-500">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="glass-card overflow-hidden opacity-0 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
            <div className="p-5 border-b border-foreground/[0.06] flex items-center justify-between">
              <h3 className="text-sm font-semibold text-foreground">All Users</h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type="text" placeholder="Search users..." className="w-56 h-9 pl-9 pr-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/30 focus:ring-1 focus:ring-wa-green/30 transition-all hover:bg-foreground/[0.05]" />
              </div>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-foreground/[0.06]">
                  {["User", "Role", "Status", "Assigned", "Resolved", "Last Login", ""].map((h) => (
                    <th key={h} className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4 first:pl-6 last:pr-6">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500">Loading users...</td>
                  </tr>
                ) : platformUsers.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500">No users found.</td>
                  </tr>
                ) : platformUsers.map((user: any) => (
                  <tr key={user.id} className="border-b border-foreground/[0.03] hover:bg-foreground/[0.03] transition-colors cursor-pointer group">
                    <td className="py-4 pl-6">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-wa-purple/20 to-wa-blue/20 flex items-center justify-center text-sm font-bold text-wa-purple border border-wa-purple/15">
                            {getInitials(user.full_name || user.fullName)}
                          </div>
                          <div className={cn("absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-[#020617]", user.is_active || user.isActive ? "bg-wa-green" : "bg-slate-500")} />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-foreground group-hover:text-wa-green transition-colors">{user.full_name || user.fullName}</p>
                          <p className="text-[10px] text-slate-500">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4"><StatusBadge status={user.role} /></td>
                    <td className="py-4">
                      <span className={cn("flex items-center gap-1.5 text-xs font-medium", user.is_active || user.isActive ? "text-wa-green" : "text-slate-500")}>
                        <div className={cn("w-1.5 h-1.5 rounded-full", user.is_active || user.isActive ? "bg-wa-green" : "bg-slate-500")} />
                        {user.is_active || user.isActive ? "Online" : "Offline"}
                      </span>
                    </td>
                    <td className="py-4"><span className="text-sm text-foreground font-medium">{user.conversationsAssigned || 0}</span></td>
                    <td className="py-4"><span className="text-sm text-foreground font-medium">{user.ticketsResolved || 0}</span></td>
                    <td className="py-4">
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Clock className="w-3 h-3" />
                        {user.last_login_at || user.lastLoginAt ? new Date(user.last_login_at || user.lastLoginAt).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "Never"}
                      </div>
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
        </div>
      </div>
      <InviteUserModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
