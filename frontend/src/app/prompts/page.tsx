"use client"

import { TopBar } from "@/components/TopBar"
import { cn } from "@/lib/utils"
import { usePrompts } from "@/hooks/useQueries"
import { CreatePromptModal } from "@/components/modals/CreatePromptModal"
import { useState } from "react"
import { Code2, Plus, Copy, Pencil, Trash2, Bot, Sparkles, FileText } from "lucide-react"

export default function PromptsPage() {
  const { data: promptsData = [], isLoading } = usePrompts()
  const promptTemplates = Array.isArray(promptsData) ? promptsData : []
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Prompt Templates" subtitle={`${promptTemplates.length} templates`}
        actions={
          <button 
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-4 bg-wa-purple hover:bg-wa-purple-dark text-foreground font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(139,92,246,0.15)]"
          >
            <Plus className="w-4 h-4" /> New Template
          </button>
        }
      />
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-5">
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Loading prompts...</div>
          ) : promptTemplates.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No prompts found.</div>
          ) : promptTemplates.map((pt: any, i: number) => (
            <div key={pt.id} className="glass-card p-6 relative overflow-hidden group cursor-pointer opacity-0 animate-fade-in-up transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:border-wa-purple/30" style={{ animationDelay: `${i * 100}ms` }}>
              <div className="absolute inset-0 bg-gradient-to-r from-wa-purple/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-xl bg-wa-purple/10 border border-wa-purple/20 flex items-center justify-center text-wa-purple">
                      <Code2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-foreground group-hover:text-wa-purple transition-colors">{pt.name}</h3>
                      <div className="flex items-center gap-3 mt-0.5">
                        <span className="flex items-center gap-1 text-[10px] text-slate-500"><Bot className="w-3 h-3" /> {pt.agent_id ? "Agent Bound" : "Shared"}</span>
                        <span className="flex items-center gap-1 text-[10px] text-slate-500"><Sparkles className="w-3 h-3" /> {pt.is_active || pt.isActive ? "Active" : "Inactive"}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="w-8 h-8 rounded-lg bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground transition-colors"><Copy className="w-3.5 h-3.5" /></button>
                    <button className="w-8 h-8 rounded-lg bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground transition-colors"><Pencil className="w-3.5 h-3.5" /></button>
                    <button className="w-8 h-8 rounded-lg bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-wa-rose transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
                  </div>
                </div>
                <div className="bg-foreground/[0.02] rounded-xl p-4 mb-4 border border-foreground/[0.04] font-mono text-xs text-slate-400 leading-relaxed max-h-[150px] overflow-y-auto">{pt.system_prompt || pt.systemPrompt || pt.content || pt.preview}</div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider mr-1">Variables:</span>
                    {(pt.variables || ["None"]).map((v: string) => (
                      <span key={v} className="px-2 py-0.5 rounded-md bg-wa-purple/10 text-[10px] text-wa-purple border border-wa-purple/15 font-mono">{`{{${v}}}`}</span>
                    ))}
                  </div>
                  <span className="text-[10px] text-slate-600">Modified: {new Date(pt.updated_at || pt.lastModified || new Date()).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <CreatePromptModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  )
}
