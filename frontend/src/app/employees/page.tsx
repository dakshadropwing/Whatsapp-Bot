"use client"

import { TopBar } from "@/components/TopBar"
import { useEmployees } from "@/hooks/useQueries"
import { cn, getInitials } from "@/lib/utils"
import { Search, Phone, MessageSquare, Clock, Star, MoreHorizontal, Briefcase } from "lucide-react"
import { useState } from "react"

export default function EmployeesPage() {
  const [search, setSearch] = useState("")
  const { data: employeesData = [], isLoading } = useEmployees({ search })
  
  const employees = Array.isArray(employeesData) ? employeesData : []
  const activeEmployees = employees.filter((e: any) => e.status === "active" || e.is_active)

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Employees" subtitle="Manage human agents and shifts" />
      
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">
          
          <div className="grid grid-cols-4 gap-4 opacity-0 animate-fade-in-up">
            {[
              { label: "Total Agents", value: employees.length, icon: <Briefcase className="w-5 h-5 text-wa-blue" />, color: "wa-blue" },
              { label: "Currently Active", value: activeEmployees.length, icon: <Star className="w-5 h-5 text-wa-green" />, color: "wa-green" },
              { label: "Active Chats", value: "0", icon: <MessageSquare className="w-5 h-5 text-wa-purple" />, color: "wa-purple" },
              { label: "Avg Handle Time", value: "—", icon: <Clock className="w-5 h-5 text-wa-amber" />, color: "wa-amber" },
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

          <div className="flex items-center justify-between mb-4 mt-8 opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            <h2 className="text-lg font-semibold text-foreground">Agent Roster</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input 
                type="text" 
                placeholder="Search employees..." 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-64 h-9 pl-9 pr-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/30 focus:ring-1 focus:ring-wa-green/30 transition-all hover:bg-foreground/[0.05]" 
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
            {isLoading ? (
              <div className="col-span-full py-12 text-center text-slate-500">Loading roster...</div>
            ) : employees.length === 0 ? (
              <div className="col-span-full py-12 text-center text-slate-500">No employees found.</div>
            ) : employees.map((employee: any) => (
              <div key={employee.id} className="glass-card p-5 group hover:-translate-y-1 hover:shadow-xl transition-all hover:border-wa-blue/30 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-wa-blue/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex justify-between items-start mb-4">
                  <div className="flex gap-3 items-center">
                    <div className="relative">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-wa-blue/20 to-wa-purple/20 flex items-center justify-center text-lg font-bold text-wa-blue border border-wa-blue/15">
                        {getInitials(employee.name || employee.full_name || employee.fullName || "A")}
                      </div>
                      <div className={cn("absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-card", employee.status === "active" || employee.is_active ? "bg-wa-green" : "bg-slate-500")} />
                    </div>
                    <div>
                      <h3 className="text-foreground font-semibold group-hover:text-wa-blue transition-colors">{employee.name || employee.full_name || employee.fullName}</h3>
                      <p className="text-xs text-slate-500">{employee.email}</p>
                    </div>
                  </div>
                  <button className="w-8 h-8 rounded-lg bg-foreground/[0.03] flex items-center justify-center text-slate-500 hover:text-foreground hover:bg-foreground/[0.08] transition-colors">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="p-3 rounded-xl bg-foreground/[0.02] border border-foreground/[0.04]">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                      <MessageSquare className="w-3 h-3" /> Department
                    </div>
                    <p className="text-sm font-semibold text-foreground truncate">{employee.department || "—"}</p>
                  </div>
                  <div className="p-3 rounded-xl bg-foreground/[0.02] border border-foreground/[0.04]">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                      <Briefcase className="w-3 h-3" /> Role
                    </div>
                    <p className="text-sm font-semibold text-foreground truncate">{employee.role || "Agent"}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 h-9 rounded-xl bg-foreground/[0.04] hover:bg-foreground/[0.08] border border-foreground/[0.08] text-sm text-foreground font-medium transition-all flex items-center justify-center gap-2">
                    <MessageSquare className="w-4 h-4 text-slate-400" /> Message
                  </button>
                  <button className="flex-1 h-9 rounded-xl bg-wa-blue/10 hover:bg-wa-blue/20 border border-wa-blue/20 text-sm text-wa-blue font-medium transition-all flex items-center justify-center gap-2">
                    <Phone className="w-4 h-4" /> Call
                  </button>
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  )
}
