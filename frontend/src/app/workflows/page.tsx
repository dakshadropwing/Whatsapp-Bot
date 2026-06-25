"use client"

import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { cn } from "@/lib/utils"
import { useWorkflows } from "@/hooks/useQueries"
import { CreateWorkflowModal } from "@/components/modals/CreateWorkflowModal"
import { useState } from "react"
import { api } from "@/lib/api"
import { useQueryClient } from "@tanstack/react-query"
import {
  Plus,
  Workflow,
  Play,
  Pause,
  MoreHorizontal,
  ArrowRight,
  Clock,
  CheckCircle2,
  Activity,
  Zap,
  GitBranch,
  Timer,
  TrendingUp,
  BarChart3,
} from "lucide-react"

const triggerIcons: Record<string, React.ReactNode> = {
  message_received: <Zap className="w-4 h-4" />,
  ticket_created: <Activity className="w-4 h-4" />,
  conversation_closed: <CheckCircle2 className="w-4 h-4" />,
  manual: <Play className="w-4 h-4" />,
  scheduled: <Timer className="w-4 h-4" />,
}

export default function WorkflowsPage() {
  const queryClient = useQueryClient()
  const { data: workflowsData = [], isLoading } = useWorkflows()
  const workflows = Array.isArray(workflowsData) ? workflowsData : []
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleToggle = async (e: React.MouseEvent, wfId: string) => {
    e.stopPropagation()
    try {
      await api.post(`/workflows/${wfId}/toggle`)
      queryClient.invalidateQueries({ queryKey: ["workflows"] })
    } catch (err) {
      console.error("Failed to toggle workflow", err)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <TopBar
        title="Workflows"
        subtitle={`${workflows.length} automation flows`}
        actions={
          <button 
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-4 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(37,211,102,0.15)]"
          >
            <Plus className="w-4 h-4" />
            Create Workflow
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">

          {/* ═══ Overview Stats ═══ */}
          <div className="grid grid-cols-4 gap-4 opacity-0 animate-fade-in-up">
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-green/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-green/10 border border-wa-green/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Workflow className="w-5 h-5 text-wa-green" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{workflows.filter((w: any) => w.is_active || w.isActive).length}</p>
                <p className="text-xs text-slate-500">Active Flows</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-purple/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-purple/10 border border-wa-purple/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <BarChart3 className="w-5 h-5 text-wa-purple" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{workflows.reduce((s: number, w: any) => s + (w.run_count || w.runCount || 0), 0).toLocaleString()}</p>
                <p className="text-xs text-slate-500">Total Runs</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-blue/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-blue/10 border border-wa-blue/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <TrendingUp className="w-5 h-5 text-wa-blue" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">
                  {workflows.length > 0 ? (workflows.reduce((s: number, w: any) => s + (w.success_rate || w.successRate || 0), 0) / workflows.length).toFixed(1) : "0"}%
                </p>
                <p className="text-xs text-slate-500">Avg Success Rate</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-amber/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-amber/10 border border-wa-amber/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <GitBranch className="w-5 h-5 text-wa-amber" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{workflows.reduce((s: number, w: any) => s + (w.steps_count || w.stepsCount || 0), 0)}</p>
                <p className="text-xs text-slate-500">Total Steps</p>
              </div>
            </div>
          </div>

          {/* ═══ Workflows List ═══ */}
          <div className="space-y-4">
            {isLoading ? (
              <div className="p-8 text-center text-slate-500">Loading workflows...</div>
            ) : workflows.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No workflows found.</div>
            ) : workflows.map((wf: any, i: number) => (
              <div
                key={wf.id}
                className="glass-card p-6 relative overflow-hidden group cursor-pointer opacity-0 animate-fade-in-up transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:border-wa-green/30"
                style={{ animationDelay: `${(i + 1) * 100}ms` }}
              >
                {/* Hover gradient */}
                <div className="absolute inset-0 bg-gradient-to-r from-wa-green/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                <div className="relative z-10 flex items-center gap-6">
                  {/* Icon */}
                  <div className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center border flex-shrink-0 transition-transform group-hover:scale-105",
                    wf.is_active || wf.isActive
                      ? "bg-gradient-to-br from-wa-green/15 to-wa-teal/10 border-wa-green/20 text-wa-green"
                      : "bg-foreground/[0.04] border-foreground/[0.08] text-slate-500"
                  )}>
                    <Workflow className="w-6 h-6" />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-sm font-semibold text-foreground group-hover:text-wa-green transition-colors">{wf.name}</h3>
                      <StatusBadge status={wf.trigger} />
                      <div className={cn(
                        "flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold",
                        wf.is_active || wf.isActive ? "bg-wa-green/10 text-wa-green" : "bg-slate-500/10 text-slate-500"
                      )}>
                        <div className={cn("w-1.5 h-1.5 rounded-full", wf.is_active || wf.isActive ? "bg-wa-green" : "bg-slate-500")} />
                        {wf.is_active || wf.isActive ? "Active" : "Paused"}
                      </div>
                    </div>
                    <p className="text-xs text-slate-500">{wf.description}</p>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-8 flex-shrink-0">
                    <div className="text-center">
                      <p className="text-lg font-bold text-foreground font-outfit">{wf.steps_count || wf.stepsCount || 0}</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider">Steps</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-foreground font-outfit">{(wf.run_count || wf.runCount || 0).toLocaleString()}</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider">Runs</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-wa-green font-outfit">{wf.success_rate || wf.successRate || 0}%</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider">Success</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button 
                      onClick={(e) => handleToggle(e, wf.id)}
                      className={cn(
                      "w-9 h-9 rounded-xl flex items-center justify-center border transition-all hover:scale-105 active:scale-95",
                      wf.is_active || wf.isActive
                        ? "bg-wa-amber/10 border-wa-amber/20 text-wa-amber hover:bg-wa-amber/20 shadow-[0_0_15px_rgba(245,158,11,0.1)]"
                        : "bg-wa-green/10 border-wa-green/20 text-wa-green hover:bg-wa-green/20 shadow-[0_0_15px_rgba(37,211,102,0.1)]"
                    )}>
                      {wf.is_active || wf.isActive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>
                    <button className="w-9 h-9 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground hover:bg-foreground/[0.08] transition-all hover:scale-105 active:scale-95">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="relative z-10 mt-4 pt-4 border-t border-foreground/[0.04]">
                  <div className="flex items-center gap-2">
                    {Array.from({ length: wf.steps_count || wf.stepsCount || 0 }).map((_, si) => (
                      <div key={si} className="flex items-center gap-2">
                        <div className={cn(
                          "w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-bold border",
                          si === 0
                            ? "bg-wa-green/15 border-wa-green/20 text-wa-green"
                            : si === ((wf.steps_count || wf.stepsCount || 1) - 1)
                            ? "bg-wa-purple/15 border-wa-purple/20 text-wa-purple"
                            : "bg-foreground/[0.04] border-foreground/[0.06] text-slate-400"
                        )}>
                          {si + 1}
                        </div>
                        {si < ((wf.steps_count || wf.stepsCount || 1) - 1) && (
                          <ArrowRight className="w-3 h-3 text-slate-600" />
                        )}
                      </div>
                    ))}
                    <span className="text-[10px] text-slate-600 ml-2">
                      Last run: {wf.last_run_at || wf.lastRunAt ? new Date(wf.last_run_at || wf.lastRunAt).toLocaleTimeString() : "Never"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <CreateWorkflowModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
