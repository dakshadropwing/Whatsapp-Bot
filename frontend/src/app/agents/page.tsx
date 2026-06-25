"use client"

import { useState } from "react"
import { TopBar } from "@/components/TopBar"
import { StatusBadge } from "@/components/StatusBadge"
import { cn } from "@/lib/utils"
import { useAgents } from "@/hooks/useQueries"
import { CreateAgentModal } from "@/components/modals/CreateAgentModal"
import { api } from "@/lib/api"
import { useQueryClient } from "@tanstack/react-query"
import {
  Bot,
  Plus,
  Settings2,
  Activity,
  MessageSquare,
  Clock,
  CheckCircle2,
  Zap,
  Eye,
  Pencil,
  ToggleLeft,
  ToggleRight,
  TrendingUp,
  Brain,
  Shield,
  ChevronRight,
  Sparkles,
} from "lucide-react"

const roleIcons: Record<string, React.ReactNode> = {
  supervisor: <Shield className="w-5 h-5" />,
  support: <MessageSquare className="w-5 h-5" />,
  sales: <TrendingUp className="w-5 h-5" />,
  lead: <Zap className="w-5 h-5" />,
  appointment: <Clock className="w-5 h-5" />,
  knowledge: <Brain className="w-5 h-5" />,
}

const roleGradients: Record<string, string> = {
  supervisor: "from-white/10 to-slate-400/10",
  support: "from-wa-green/15 to-wa-teal/10",
  sales: "from-wa-blue/15 to-wa-cyan/10",
  lead: "from-wa-amber/15 to-yellow-500/10",
  appointment: "from-wa-cyan/15 to-wa-blue/10",
  knowledge: "from-wa-purple/15 to-wa-blue/10",
}

export default function AgentsPage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const queryClient = useQueryClient()
  
  const { data: agentsData = [], isLoading } = useAgents()
  const aiAgents = Array.isArray(agentsData) ? agentsData : []

  const handleToggle = async (e: React.MouseEvent, agentId: string) => {
    e.stopPropagation()
    try {
      await api.post(`/agents/${agentId}/toggle`)
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    } catch (err) {
      console.error("Failed to toggle agent", err)
    }
  }

  const selectedAgent = aiAgents.find((a: any) => a.id === selectedAgentId)

  return (
    <div className="flex flex-col h-full">
      <TopBar
        title="AI Agents"
        subtitle={`${aiAgents.length} configured agents`}
        actions={
          <button 
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-4 bg-wa-purple hover:bg-wa-purple-dark text-foreground font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(139,92,246,0.15)]"
          >
            <Plus className="w-4 h-4" />
            Create Agent
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">

          {/* ═══ Overview Stats ═══ */}
          <div className="grid grid-cols-4 gap-4 opacity-0 animate-fade-in-up">
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-green/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-green/10 border border-wa-green/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Bot className="w-5 h-5 text-wa-green" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">{aiAgents.filter((a: any) => a.is_active || a.isActive).length}</p>
                <p className="text-xs text-slate-500">Active Agents</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-purple/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-purple/10 border border-wa-purple/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <MessageSquare className="w-5 h-5 text-wa-purple" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">
                  {aiAgents.reduce((acc: number, a: any) => acc + (a.conversationsHandled || 0), 0).toLocaleString()}
                </p>
                <p className="text-xs text-slate-500">Total Handled</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-blue/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-blue/10 border border-wa-blue/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Clock className="w-5 h-5 text-wa-blue" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">0m</p>
                <p className="text-xs text-slate-500">Avg Response</p>
              </div>
            </div>
            <div className="glass-card-sm p-4 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-cyan/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-cyan/10 border border-wa-cyan/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <CheckCircle2 className="w-5 h-5 text-wa-cyan" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground font-outfit">0%</p>
                <p className="text-xs text-slate-500">Resolution Rate</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {isLoading ? (
              <div className="col-span-full p-8 text-center text-slate-500">Loading agents...</div>
            ) : aiAgents.map((agent: any, i: number) => (
              <div
                key={agent.id}
                onClick={() => setSelectedAgentId(selectedAgentId === agent.id ? null : agent.id)}
                className={cn(
                  "glass-card p-6 relative overflow-hidden cursor-pointer group opacity-0 animate-fade-in-up transition-all duration-300 hover:-translate-y-1 hover:shadow-xl",
                  selectedAgentId === agent.id && "ring-2 ring-wa-purple/50 border-wa-purple/50 glow-purple"
                )}
                style={{ animationDelay: `${(i + 1) * 100}ms` }}
              >
                {/* Background gradient based on role */}
                <div className={cn(
                  "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none",
                  roleGradients[agent.role_type || agent.roleType || "support"] || roleGradients["support"]
                )} />

                <div className="relative z-10">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "w-12 h-12 rounded-2xl flex items-center justify-center border transition-transform group-hover:scale-105",
                        agent.is_active || agent.isActive
                          ? "bg-gradient-to-br from-wa-green/15 to-wa-teal/10 border-wa-green/20 text-wa-green"
                          : "bg-foreground/[0.04] border-foreground/[0.08] text-slate-500"
                      )}>
                        {roleIcons[agent.role_type || agent.roleType || "support"] || <Bot className="w-5 h-5" />}
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-foreground group-hover:text-wa-green transition-colors">{agent.name}</h3>
                        <div className="flex items-center gap-2 mt-0.5">
                          <StatusBadge status={agent.role_type || agent.roleType || "support"} />
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleToggle(e, agent.id)}
                      className={cn(
                        "flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px] font-semibold transition-all hover:opacity-80",
                        agent.is_active || agent.isActive
                          ? "bg-wa-green/10 text-wa-green border border-wa-green/15"
                          : "bg-slate-500/10 text-slate-500 border border-slate-500/15"
                      )}
                    >
                      <div className={cn(
                        "w-1.5 h-1.5 rounded-full",
                        agent.is_active || agent.isActive ? "bg-wa-green animate-pulse" : "bg-slate-500"
                      )} />
                      {agent.is_active || agent.isActive ? "Active" : "Inactive"}
                    </button>
                  </div>

                  {/* Prompt Preview */}
                  <p className="text-xs text-slate-500 mb-4 line-clamp-2 leading-relaxed">{agent.system_prompt || agent.systemPromptPreview}</p>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div className="text-center p-2 rounded-lg bg-foreground/[0.03]">
                      <p className="text-lg font-bold text-foreground font-outfit">{(agent.conversationsHandled || 0).toLocaleString()}</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider">Handled</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-foreground/[0.03]">
                      <p className="text-lg font-bold text-foreground font-outfit">{agent.avgResponseTime || 0}m</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider">Avg Time</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-foreground/[0.03]">
                      <p className="text-lg font-bold text-wa-green font-outfit">{agent.resolutionRate || 0}%</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider">Resolved</p>
                    </div>
                  </div>

                  {/* Model Info */}
                  <div className="flex items-center justify-between pt-3 border-t border-foreground/[0.06]">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-3 h-3 text-wa-purple" />
                      <span className="text-[10px] text-slate-500">
                        {agent.provider === "gemini" ? "Google Gemini" : agent.provider === "ollama" ? "Ollama" : "Model"} · {agent.model_name || agent.modelName}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <button className="w-6 h-6 rounded-md bg-foreground/[0.04] flex items-center justify-center text-slate-500 hover:text-foreground transition-colors opacity-0 group-hover:opacity-100">
                        <Eye className="w-3 h-3" />
                      </button>
                      <button className="w-6 h-6 rounded-md bg-foreground/[0.04] flex items-center justify-center text-slate-500 hover:text-foreground transition-colors opacity-0 group-hover:opacity-100">
                        <Pencil className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <CreateAgentModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
