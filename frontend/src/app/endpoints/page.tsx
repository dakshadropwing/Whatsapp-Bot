"use client"

import { TopBar } from "@/components/TopBar"
import { useEndpoints } from "@/hooks/useQueries"
import { Webhook, Activity, Key, CheckCircle2, XCircle, RefreshCw } from "lucide-react"

export default function EndpointsPage() {
  const { data: endpointsData = [], isLoading } = useEndpoints()
  const endpoints = Array.isArray(endpointsData) ? endpointsData : []

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Endpoints & Webhooks" subtitle="Manage API keys and webhook connections" />
      
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">
          
          {/* Top Status Cards */}
          <div className="grid grid-cols-3 gap-4 opacity-0 animate-fade-in-up">
            <div className="glass-card-sm p-5 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-green/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-green/10 border border-wa-green/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Webhook className="w-5 h-5 text-wa-green" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">Webhook Status</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-wa-green animate-pulse" />
                  <p className="text-lg font-bold text-foreground">{endpoints.length > 0 ? "Receiving" : "Offline"}</p>
                </div>
              </div>
            </div>

            <div className="glass-card-sm p-5 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-blue/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-blue/10 border border-wa-blue/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Activity className="w-5 h-5 text-wa-blue" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">Total Configured</p>
                <p className="text-xl font-bold text-foreground font-outfit mt-0.5">{endpoints.length}</p>
              </div>
            </div>

            <div className="glass-card-sm p-5 flex items-center gap-4 hover:-translate-y-1 transition-all hover:border-wa-amber/30 hover:shadow-lg cursor-default group">
              <div className="w-10 h-10 rounded-xl bg-wa-amber/10 border border-wa-amber/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <XCircle className="w-5 h-5 text-wa-amber" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">Failed Deliveries</p>
                <p className="text-xl font-bold text-foreground font-outfit mt-0.5">0</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
            
            {/* Active Webhooks */}
            <div className="col-span-2 glass-card overflow-hidden">
              <div className="p-5 border-b border-foreground/[0.06] flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Webhook className="w-4 h-4 text-wa-green" /> Configured Webhooks
                </h3>
                <button className="text-xs font-medium text-wa-green hover:text-wa-green-dark transition-colors">Add Endpoint</button>
              </div>
              <div className="p-5 space-y-4">
                {isLoading ? (
                  <div className="text-center py-8 text-slate-500 text-sm">Loading endpoints...</div>
                ) : endpoints.length === 0 ? (
                  <div className="text-center py-8 text-slate-500 text-sm">No endpoints configured yet.</div>
                ) : endpoints.map((ep: any) => (
                  <div key={ep.id} className="p-4 rounded-xl bg-foreground/[0.02] border border-foreground/[0.04] hover:border-wa-green/30 transition-all group">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-wa-green/10 text-wa-green">{ep.method || "POST"}</span>
                          <h4 className="text-sm font-semibold text-foreground group-hover:text-wa-green transition-colors">{ep.name}</h4>
                        </div>
                        <p className="text-xs text-slate-500 font-mono">{ep.url}</p>
                      </div>
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${ep.is_active ? 'bg-wa-green/10 border-wa-green/20' : 'bg-slate-500/10 border-slate-500/20'} border`}>
                        {ep.is_active ? <CheckCircle2 className="w-3 h-3 text-wa-green" /> : <XCircle className="w-3 h-3 text-slate-400" />}
                        <span className={`text-[10px] font-medium ${ep.is_active ? 'text-wa-green' : 'text-slate-400'}`}>{ep.is_active ? 'Healthy' : 'Disabled'}</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between pt-3 border-t border-foreground/[0.04]">
                      <p className="text-[10px] text-slate-500">Last updated: {new Date(ep.updated_at || ep.created_at).toLocaleDateString()}</p>
                      <button className="text-[10px] text-slate-400 hover:text-foreground transition-colors flex items-center gap-1">
                        <RefreshCw className="w-3 h-3" /> Test
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* API Keys */}
            <div className="glass-card overflow-hidden">
               <div className="p-5 border-b border-foreground/[0.06] flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Key className="w-4 h-4 text-wa-purple" /> API Keys
                </h3>
              </div>
              <div className="p-5 space-y-4">
                <div className="text-center py-10 space-y-3">
                  <div className="w-12 h-12 rounded-full bg-foreground/[0.03] flex items-center justify-center mx-auto text-slate-400">
                    <Key className="w-5 h-5" />
                  </div>
                  <p className="text-sm text-slate-500">API Key management will be available in the next release.</p>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  )
}
