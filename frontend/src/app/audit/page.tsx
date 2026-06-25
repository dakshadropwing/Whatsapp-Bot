"use client"

import { TopBar } from "@/components/TopBar"
import { useAuditLogs } from "@/hooks/useQueries"
import { ShieldCheck, Search, Filter, Download, UserCircle, Key, Server, FileText } from "lucide-react"

export default function AuditPage() {
  const { data: logsData = [], isLoading } = useAuditLogs()
  const logs = Array.isArray(logsData) ? logsData : []
  return (
    <div className="flex flex-col h-full">
      <TopBar title="Audit Logs" subtitle="System-wide security and action trails" />
      
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">

          {/* Filters & Search */}
          <div className="glass-card p-5 opacity-0 animate-fade-in-up flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input type="text" placeholder="Search logs, IPs, or users..." className="w-80 h-9 pl-9 pr-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-purple/30 focus:ring-1 focus:ring-wa-purple/30 transition-all hover:bg-foreground/[0.05]" />
              </div>
              <button className="h-9 px-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground font-medium hover:bg-foreground/[0.08] transition-colors flex items-center gap-2">
                <Filter className="w-4 h-4 text-slate-400" /> Filter
              </button>
            </div>
            <button className="h-9 px-4 rounded-xl bg-wa-purple/10 border border-wa-purple/20 text-sm text-wa-purple font-medium hover:bg-wa-purple/20 transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" /> Export CSV
            </button>
          </div>

          {/* Audit Table */}
          <div className="glass-card overflow-hidden opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            <table className="w-full">
              <thead>
                <tr className="border-b border-foreground/[0.06] bg-foreground/[0.02]">
                  {["Timestamp", "Event Category", "Action", "Actor", "IP Address", "Status"].map((h) => (
                    <th key={h} className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4 first:pl-6 last:pr-6">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={6} className="py-8 text-center text-slate-500">Loading audit logs...</td></tr>
                ) : logs.length === 0 ? (
                  <tr><td colSpan={6} className="py-8 text-center text-slate-500">No audit logs found.</td></tr>
                ) : logs.map((log: any, i: number) => {
                  let icon = <Server className="w-3.5 h-3.5" />;
                  let color = "wa-blue";
                  if (log.resource_type === "Authentication") { icon = <Key className="w-3.5 h-3.5" />; color = "wa-purple"; }
                  else if (log.resource_type === "User Management") { icon = <UserCircle className="w-3.5 h-3.5" />; color = "wa-green"; }
                  else if (log.action && log.action.toLowerCase().includes("fail")) { color = "wa-amber"; }

                  return (
                    <tr key={log.id || i} className="border-b border-foreground/[0.03] hover:bg-foreground/[0.03] transition-colors group cursor-default">
                      <td className="py-4 pl-6 text-xs text-slate-400 font-mono">{new Date(log.created_at).toLocaleString()}</td>
                      <td className="py-4">
                        <div className={`flex items-center gap-2 text-xs font-medium text-${color}`}>
                          {icon} {log.resource_type || "System"}
                        </div>
                      </td>
                      <td className="py-4 text-sm font-medium text-foreground">{log.action}</td>
                      <td className="py-4 text-sm text-slate-400">{log.user_id || "System"}</td>
                      <td className="py-4 text-xs text-slate-500 font-mono">{log.ip_address || "—"}</td>
                      <td className="py-4 pr-6">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold ${!log.action?.toLowerCase().includes('fail') ? 'bg-wa-green/10 text-wa-green' : 'bg-wa-amber/10 text-wa-amber'}`}>
                          {!log.action?.toLowerCase().includes('fail') ? 'Success' : 'Failed'}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            
            <div className="p-4 border-t border-foreground/[0.06] flex items-center justify-between text-sm text-slate-500">
              <p>Showing {logs.length} logs</p>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 rounded-lg border border-foreground/[0.08] hover:bg-foreground/[0.04] transition-colors disabled:opacity-50">Previous</button>
                <button className="px-3 py-1.5 rounded-lg border border-foreground/[0.08] hover:bg-foreground/[0.04] transition-colors">Next</button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
