"use client"

import { TopBar } from "@/components/TopBar"
import { MiniBarChart } from "@/components/Charts"
import { Activity, Clock, Users, MessageSquare, TrendingUp, ArrowUpRight, ArrowDownRight, ChevronDown } from "lucide-react"
import { useAnalyticsStats, useAnalyticsOverview, useAuditLogs } from "@/hooks/useQueries"
import { useState } from "react"

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("7d")
  const { data: stats, isLoading: statsLoading } = useAnalyticsStats()
  const { data: overview, isLoading: overviewLoading } = useAnalyticsOverview(period)
  
  // Need recent audit logs for the bottom table, or we can just use the audit hook
  const { data: recentLogsData = [] } = useAuditLogs({ per_page: 5 })
  const recentLogs = Array.isArray(recentLogsData) ? recentLogsData : []

  const volData = overview?.messages_by_day?.map((d: any) => ({
    label: d.label ? d.label.split("-").slice(1).join("/") : "", // MM/DD
    inbound: d.value || 0,
    outbound: 0
  })) || []

  const resData = overview?.agent_usage?.map((a: any) => ({
    label: a.agent || "Agent",
    inbound: a.resolved || 0,
    outbound: 0
  })) || []

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Analytics" subtitle="Real-time platform performance and insights" />
      
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">
          
          <div className="grid grid-cols-4 gap-4 opacity-0 animate-fade-in-up">
            {[
              { label: "Total Conversations", value: stats?.total_conversations || 0, change: "+0%", isPositive: true, icon: <MessageSquare className="w-5 h-5 text-wa-blue" />, color: "wa-blue" },
              { label: "AI Resolution Rate", value: `${stats?.ai_resolution_rate || 0}%`, change: "+0%", isPositive: true, icon: <Activity className="w-5 h-5 text-wa-green" />, color: "wa-green" },
              { label: "Avg Response Time", value: `${stats?.avg_response_time_ms || 0}ms`, change: "-0ms", isPositive: true, icon: <Clock className="w-5 h-5 text-wa-purple" />, color: "wa-purple" },
              { label: "Open Tickets", value: stats?.tickets_open || 0, change: "-0", isPositive: false, icon: <Users className="w-5 h-5 text-wa-amber" />, color: "wa-amber" },
            ].map((stat, i) => (
              <div key={i} className={`glass-card-sm p-4 hover:-translate-y-1 transition-all hover:border-${stat.color}/30 hover:shadow-lg cursor-default group`}>
                <div className="flex justify-between items-start mb-4">
                  <div className={`w-10 h-10 rounded-xl bg-${stat.color}/10 border border-${stat.color}/20 flex items-center justify-center group-hover:scale-110 transition-transform`}>
                    {stat.icon}
                  </div>
                  <div className={`flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-full ${stat.isPositive ? 'text-wa-green bg-wa-green/10' : 'text-wa-amber bg-wa-amber/10'}`}>
                    {stat.isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {stat.change}
                  </div>
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground font-outfit">{statsLoading ? "..." : stat.value}</p>
                  <p className="text-xs text-slate-500">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            
            <div className="col-span-2 glass-card p-6 flex flex-col h-[400px]">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-wa-blue" /> Conversation Volume
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">Daily inbound and outbound messages</p>
                </div>
                <div className="relative">
                  <select 
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="bg-foreground/[0.04] border border-foreground/[0.08] text-xs text-foreground rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:border-wa-blue/30 transition-all appearance-none cursor-pointer"
                  >
                    <option value="7d" className="bg-slate-900 text-white">Last 7 Days</option>
                    <option value="30d" className="bg-slate-900 text-white">Last 30 Days</option>
                    <option value="365d" className="bg-slate-900 text-white">This Year</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500 pointer-events-none" />
                </div>
              </div>
              <div className="flex-1 flex items-end w-full">
                {overviewLoading ? (
                  <div className="w-full text-center text-slate-500 text-sm">Loading charts...</div>
                ) : volData.length > 0 ? (
                  <MiniBarChart data={volData} />
                ) : (
                  <div className="w-full text-center text-slate-500 text-sm">No volume data available</div>
                )}
              </div>
            </div>

            <div className="glass-card p-6 flex flex-col h-[400px]">
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Activity className="w-4 h-4 text-wa-green" /> Resolution by Agent
                </h3>
                <p className="text-xs text-slate-500 mt-1">Top performing AI and Human agents</p>
              </div>
              <div className="flex-1 flex flex-col justify-end w-full pb-4">
                {overviewLoading ? (
                  <div className="w-full text-center text-slate-500 text-sm">Loading charts...</div>
                ) : resData.length > 0 ? (
                  <MiniBarChart data={resData} />
                ) : (
                  <div className="w-full text-center text-slate-500 text-sm">No agent usage data</div>
                )}
              </div>
            </div>

          </div>

          {/* Detailed Reports Table */}
          <div className="glass-card overflow-hidden opacity-0 animate-fade-in-up" style={{ animationDelay: "150ms" }}>
            <div className="p-5 border-b border-foreground/[0.06] flex items-center justify-between">
              <h3 className="text-sm font-semibold text-foreground">Recent Audit Logs</h3>
              <button className="text-xs font-medium text-wa-blue hover:text-wa-blue-dark transition-colors">Download CSV</button>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-foreground/[0.06]">
                  {["Date", "Resource", "Action", "Status", ""].map((h) => (
                    <th key={h} className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold py-4 first:pl-6 last:pr-6">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {recentLogs.length === 0 ? (
                  <tr><td colSpan={5} className="py-8 text-center text-slate-500">No recent audit logs available</td></tr>
                ) : recentLogs.map((row: any, i: number) => (
                  <tr key={i} className="border-b border-foreground/[0.03] hover:bg-foreground/[0.03] transition-colors group">
                    <td className="py-4 pl-6 text-sm text-foreground">{new Date(row.created_at).toLocaleDateString()}</td>
                    <td className="py-4 text-sm font-medium text-foreground">{row.resource_type || "System"}</td>
                    <td className="py-4 text-sm text-slate-400">{row.action}</td>
                    <td className="py-4">
                      <span className={`px-2 py-1 rounded-md text-[10px] font-bold ${!row.action?.toLowerCase().includes('fail') ? 'bg-wa-green/10 text-wa-green' : 'bg-wa-amber/10 text-wa-amber'}`}>
                        {!row.action?.toLowerCase().includes('fail') ? 'Success' : 'Failed'}
                      </span>
                    </td>
                    <td className="py-4 pr-6 text-right">
                      <button className="text-xs text-wa-blue hover:text-wa-blue-dark transition-colors opacity-0 group-hover:opacity-100">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </div>
  )
}
