"use client"

import { TopBar } from "@/components/TopBar"
import { useWhatsAppAccounts } from "@/hooks/useQueries"
import { Smartphone, Send, MessageSquareText, BarChart3, Plus, Settings2, Globe } from "lucide-react"

export default function WhatsAppPage() {
  const { data: accountsData = [], isLoading } = useWhatsAppAccounts()
  const accounts = Array.isArray(accountsData) ? accountsData : []

  return (
    <div className="flex flex-col h-full">
      <TopBar 
        title="WhatsApp Platform" 
        subtitle="Manage campaigns, templates, and numbers" 
        actions={
          <button className="h-9 px-4 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm shadow-[0_0_20px_rgba(37,211,102,0.15)]">
            <Plus className="w-4 h-4" /> New Campaign
          </button>
        }
      />
      
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">
          
          <div className="grid grid-cols-4 gap-4 opacity-0 animate-fade-in-up">
            {[
              { label: "Active Campaigns", value: "0", icon: <Send className="w-5 h-5 text-wa-green" />, color: "wa-green" },
              { label: "Messages Sent", value: "0", icon: <MessageSquareText className="w-5 h-5 text-wa-blue" />, color: "wa-blue" },
              { label: "Delivery Rate", value: "0%", icon: <BarChart3 className="w-5 h-5 text-wa-purple" />, color: "wa-purple" },
              { label: "Connected Numbers", value: accounts.length.toString(), icon: <Smartphone className="w-5 h-5 text-wa-amber" />, color: "wa-amber" },
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

          <div className="grid grid-cols-3 gap-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            
            {/* Active Campaigns */}
            <div className="col-span-2 glass-card overflow-hidden">
              <div className="p-5 border-b border-foreground/[0.06] flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Send className="w-4 h-4 text-wa-green" /> Active Campaigns
                </h3>
                <button className="text-xs font-medium text-wa-green hover:text-wa-green-dark transition-colors">View All</button>
              </div>
              <div className="p-5 space-y-4">
                <div className="text-center py-10 space-y-3">
                  <div className="w-12 h-12 rounded-full bg-foreground/[0.03] flex items-center justify-center mx-auto text-slate-400">
                    <Send className="w-5 h-5" />
                  </div>
                  <p className="text-sm text-slate-500">No active campaigns. Campaigns feature is currently in beta.</p>
                </div>
              </div>
            </div>

            {/* Quick Settings */}
            <div className="glass-card overflow-hidden">
               <div className="p-5 border-b border-foreground/[0.06] flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Globe className="w-4 h-4 text-wa-blue" /> Phone Numbers
                </h3>
                <button className="p-1.5 rounded-lg bg-foreground/[0.04] hover:bg-foreground/[0.08] text-slate-400 hover:text-foreground transition-all">
                  <Settings2 className="w-4 h-4" />
                </button>
              </div>
              <div className="p-5 space-y-4">
                {isLoading ? (
                  <div className="text-center py-4 text-slate-500 text-sm">Loading accounts...</div>
                ) : accounts.length === 0 ? (
                  <div className="text-center py-4 text-slate-500 text-sm">No numbers connected.</div>
                ) : accounts.map((acc: any, i: number) => (
                  <div key={acc.id || i} className={`p-4 rounded-xl bg-foreground/[0.02] border relative overflow-hidden ${acc.is_active ? 'border-wa-green/20' : 'border-foreground/[0.04]'}`}>
                    {acc.is_active && <div className="absolute top-0 right-0 w-16 h-16 bg-wa-green/5 rounded-bl-full" />}
                    <div className="flex justify-between items-start mb-2">
                      <p className={`text-xs font-medium ${acc.is_active ? 'text-wa-green' : 'text-slate-400'}`}>{acc.is_active ? 'Active' : 'Inactive'}</p>
                      <div className={`w-2 h-2 rounded-full ${acc.is_active ? 'bg-wa-green animate-pulse' : 'bg-slate-500'}`} />
                    </div>
                    <p className="text-lg font-bold text-foreground font-outfit">{acc.phone_number_id}</p>
                    <p className="text-xs text-slate-500 mt-1">WABA ID: {acc.waba_id}</p>
                  </div>
                ))}

                <button className="w-full h-10 rounded-xl border border-dashed border-foreground/[0.1] text-xs font-medium text-slate-400 hover:text-foreground hover:bg-foreground/[0.02] transition-colors flex items-center justify-center gap-2">
                  <Plus className="w-3 h-3" /> Connect Number
                </button>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  )
}
