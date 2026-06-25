"use client"

import { useAnalyticsStats, useAnalyticsOverview, useConversations } from "@/hooks/useQueries"
import { Loader2 } from "lucide-react"

import {
  MessageSquare,
  Ticket,
  Bot,
  Activity,
  Plus,
  Zap,
  TrendingUp,
  Users,
  Clock,
  ArrowRight,
  CheckCircle2,
  CheckCircle,
  AlertTriangle,
  MessageCircle,
  Shuffle,
} from "lucide-react"
import { StatCard } from "@/components/StatCard"
import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { MiniBarChart, DonutChart } from "@/components/Charts"
import { cn, getGreeting, getInitials, timeAgo } from "@/lib/utils"
import Link from "next/link"

export default function DashboardPage() {
  const { data: stats, isLoading: isStatsLoading } = useAnalyticsStats()
  const { data: convs, isLoading: isConvsLoading } = useConversations()
  const { data: overview, isLoading: isOverviewLoading } = useAnalyticsOverview()

  if (isStatsLoading || isConvsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 text-wa-green animate-spin" />
      </div>
    )
  }

  const chartData = overview?.messages_by_day?.length > 0
    ? overview.messages_by_day.map((d: any) => ({
        label: new Date(d.label).toLocaleDateString(undefined, { weekday: 'short' }),
        inbound: d.value,
        outbound: Math.floor(d.value * 0.5), // Estimate outbound since backend doesn't separate yet
      }))
    : []

  const donutSegments = [
    { label: "AI Resolved", value: stats?.ai_resolution_rate || 0, color: "#25d366" },
    { label: "Human Resolved", value: 100 - (stats?.ai_resolution_rate || 0), color: "#3b82f6" },
  ]

  const recentConversations = Array.isArray(convs) ? convs.slice(0, 5) : []
  const sparkline = overview?.messages_by_day?.map((d: any) => d.value) || []
  const agentPerformanceData = overview?.agent_usage || []
  const liveEvents = overview?.recent_events || []

  return (
    <div className="flex flex-col h-full">
      <TopBar
        title={`${getGreeting()}, Admin`}
        subtitle="Here's what's happening across your platform today."
        actions={
          <Link href="/workflows" className="h-9 px-4 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(37,211,102,0.15)] hover:shadow-[0_0_30px_rgba(37,211,102,0.25)]">
            <Plus className="w-4 h-4" />
            New Campaign
          </Link>
        }
      />

      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-8">

          {/* ═══ Stats Grid ═══ */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Conversations"
              value={stats?.total_conversations?.toLocaleString() || "0"}
              trend="+12.5%"
              icon={<MessageSquare className="w-5 h-5" />}
              color="green"
              sparkline={sparkline}
              delay={0}
            />
            <StatCard
              title="Active Tickets"
              value={stats?.tickets_open?.toString() || "0"}
              trend="-2.4%"
              trendDown
              icon={<Ticket className="w-5 h-5" />}
              color="amber"
              sparkline={[32, 28, 35, 30, 24, 18, 22]}
              delay={100}
            />
            <StatCard
              title="AI Resolution Rate"
              value={`${stats?.ai_resolution_rate || 0}%`}
              trend="+5.1%"
              icon={<Bot className="w-5 h-5" />}
              color="purple"
              sparkline={[72, 78, 80, 83, 85, 84, 87]}
              delay={200}
            />
            <StatCard
              title="Avg. Response Time"
              value={`${(stats?.avg_response_time_ms / 60000).toFixed(1)}m`}
              trend="-10.5%"
              trendDown
              icon={<Clock className="w-5 h-5" />}
              color="cyan"
              sparkline={[2.8, 2.4, 2.1, 1.8, 1.5, 1.3, 1.2]}
              delay={300}
            />
          </div>

          {/* ═══ Main Content ═══ */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* ── Message Traffic Chart ─────────────── */}
            <div className="lg:col-span-2 glass-card p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "400ms" }}>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="font-semibold text-foreground text-sm">Message Traffic</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Today&apos;s inbound vs outbound volume</p>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="flex items-center gap-2 text-slate-400">
                    <div className="w-2 h-2 rounded-full bg-wa-green" /> Inbound
                  </span>
                  <span className="flex items-center gap-2 text-slate-400">
                    <div className="w-2 h-2 rounded-full bg-wa-teal" /> Outbound
                  </span>
                </div>
              </div>
              <MiniBarChart data={chartData} />
            </div>

            {/* ── AI Performance Donut ─────────────── */}
            <div className="glass-card p-6 flex flex-col items-center justify-center opacity-0 animate-fade-in-up" style={{ animationDelay: "500ms" }}>
              <h3 className="font-semibold text-foreground text-sm mb-1 self-start">AI Performance</h3>
              <p className="text-xs text-slate-500 mb-6 self-start">Resolution breakdown</p>

              <DonutChart
                segments={donutSegments}
                centerLabel="Resolved"
                centerValue={`${stats?.ai_resolution_rate || 0}%`}
              />

              <div className="flex flex-col gap-2 mt-6 w-full">
                {donutSegments.map((seg) => (
                  <div key={seg.label} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: seg.color }} />
                      <span className="text-slate-400">{seg.label}</span>
                    </div>
                    <span className="text-foreground font-semibold">{seg.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ═══ Second Row ═══ */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* ── Agent Performance ────────────────── */}
            <div className="lg:col-span-2 glass-card p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "600ms" }}>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="font-semibold text-foreground text-sm">Agent Performance</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Conversations handled by each AI agent</p>
                </div>
                <Link href="/agents" className="text-xs text-wa-green hover:text-foreground transition-colors flex items-center gap-1">
                  View All <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              <div className="space-y-4">
                {agentPerformanceData.map((agent: any, i: number) => {
                  const total = agent.handled || 0
                  const resolvedPct = total > 0 ? ((agent.resolved || 0) / total) * 100 : 0
                  return (
                    <div key={agent.agent || i} className="group">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-foreground/[0.04] flex items-center justify-center border border-foreground/[0.06]">
                            <Bot className="w-4 h-4 text-slate-400" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-foreground">{agent.agent} Agent</p>
                            <p className="text-[10px] text-slate-500">{agent.handled} conversations</p>
                          </div>
                        </div>
                        <span className="text-sm font-bold text-wa-green">{resolvedPct.toFixed(1)}%</span>
                      </div>
                      <div className="h-2 bg-foreground/[0.04] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-wa-green to-wa-teal rounded-full transition-all duration-1000"
                          style={{
                            width: `${resolvedPct}%`,
                            transitionDelay: `${600 + i * 150}ms`,
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* ── Live Operations Feed ─────────────── */}
            <div className="glass-card p-6 flex flex-col opacity-0 animate-fade-in-up" style={{ animationDelay: "700ms" }}>
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="font-semibold text-foreground text-sm">Live Operations</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Real-time activity feed</p>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-wa-green animate-pulse" />
                  <span className="text-[10px] text-wa-green font-semibold">LIVE</span>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2 no-scrollbar">
                {liveEvents.map((event: any) => {
                  const iconMap = {
                    message: <MessageCircle className="w-3.5 h-3.5" />,
                    ticket: <Ticket className="w-3.5 h-3.5" />,
                    escalation: <AlertTriangle className="w-3.5 h-3.5" />,
                    resolution: <CheckCircle className="w-3.5 h-3.5" />,
                    agent_switch: <Shuffle className="w-3.5 h-3.5" />,
                  }
                  const severityColors = {
                    info: "text-wa-blue bg-wa-blue/10",
                    warning: "text-wa-amber bg-wa-amber/10",
                    success: "text-wa-green bg-wa-green/10",
                    danger: "text-wa-rose bg-wa-rose/10",
                  }

                  return (
                    <div key={event.id} className="flex items-start gap-3 p-3 rounded-xl hover:bg-foreground/[0.03] transition-colors cursor-pointer group">
                      <div className={cn("w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5", severityColors[event.severity as keyof typeof severityColors])}>
                        {iconMap[event.type as keyof typeof iconMap] || <MessageCircle className="w-3.5 h-3.5" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <p className="text-xs font-medium text-foreground truncate group-hover:text-wa-green transition-colors">{event.title}</p>
                          <span className="text-[9px] text-slate-600 whitespace-nowrap">{timeAgo(event.timeAgo)}</span>
                        </div>
                        <p className="text-[11px] text-slate-500 truncate mt-0.5">{event.description}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* ═══ Recent Conversations Preview ═══ */}
          <div className="glass-card p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "800ms" }}>
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="font-semibold text-foreground text-sm">Recent Conversations</h3>
                <p className="text-xs text-slate-500 mt-0.5">Latest WhatsApp threads</p>
              </div>
              <Link href="/conversations" className="text-xs text-wa-green hover:text-foreground transition-colors flex items-center gap-1">
                View All <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-foreground/[0.06]">
                    <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold pb-3 pl-3">Contact</th>
                    <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold pb-3">Status</th>
                    <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold pb-3">Last Message</th>
                    <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold pb-3">Agent</th>
                    <th className="text-left text-[10px] text-slate-500 uppercase tracking-wider font-semibold pb-3">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentConversations.map((conv: any) => (
                    <tr key={conv.id} className="border-b border-foreground/[0.03] hover:bg-foreground/[0.02] transition-colors cursor-pointer group">
                      <td className="py-3 pl-3">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-wa-green/20 to-wa-teal/20 flex items-center justify-center text-xs font-bold text-wa-green border border-wa-green/15">
                            {getInitials(conv.contact_name || conv.contactName || "?")}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-foreground group-hover:text-wa-green transition-colors">{conv.contact_name || conv.contactName}</p>
                            <p className="text-[10px] text-slate-500">{conv.contact_phone || conv.contactPhone}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3"><StatusBadge status={conv.status} /></td>
                      <td className="py-3">
                        <p className="text-xs text-slate-400 truncate max-w-[250px]">{conv.lastMessage || `${conv.message_count || 0} messages`}</p>
                      </td>
                      <td className="py-3">
                        <span className="text-xs text-slate-400">{conv.assigned_agent_id ? "AI Agent" : conv.assigned_user_id ? "User" : "—"}</span>
                      </td>
                      <td className="py-3">
                        <span className="text-[10px] text-slate-500">{timeAgo(conv.updated_at || conv.lastMessageAt || new Date())}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
