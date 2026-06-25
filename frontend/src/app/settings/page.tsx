"use client"

import { TopBar } from "@/components/TopBar"
import { cn } from "@/lib/utils"
import {
  Settings2, Key, Bell, Shield, Palette, Globe, Database, Server,
  ChevronRight, ToggleLeft, ToggleRight, Save, ExternalLink,
} from "lucide-react"
import { useState } from "react"
import { useSettings } from "@/hooks/useQueries"
import { Loader2 } from "lucide-react"

const settingSections = [
  {
    id: "general",
    icon: <Settings2 className="w-5 h-5" />,
    title: "General",
    description: "Organization name, timezone, and default settings",
  },
  {
    id: "whatsapp",
    icon: <Globe className="w-5 h-5" />,
    title: "WhatsApp Configuration",
    description: "Meta Business API credentials and webhook settings",
  },
  {
    id: "ai",
    icon: <Database className="w-5 h-5" />,
    title: "AI & LLM Settings",
    description: "Gemini API keys, model selection, and token limits",
  },
  {
    id: "security",
    icon: <Shield className="w-5 h-5" />,
    title: "Security",
    description: "JWT settings, encryption keys, and MFA configuration",
  },
  {
    id: "notifications",
    icon: <Bell className="w-5 h-5" />,
    title: "Notifications",
    description: "Email alerts, webhook notifications, and escalation rules",
  },
  {
    id: "api",
    icon: <Key className="w-5 h-5" />,
    title: "API Keys",
    description: "Manage API keys for external integrations",
  },
]

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState("general")
  const { data: settings, isLoading } = useSettings()

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Settings" subtitle="Platform configuration" />

      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto">
          <div className="flex gap-6">
            {/* Sidebar Nav */}
            <div className="w-[280px] flex-shrink-0 space-y-1.5">
              {settingSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all group",
                    activeSection === section.id
                      ? "bg-wa-green/10 border border-wa-green/20 text-foreground"
                      : "text-slate-400 hover:text-foreground hover:bg-foreground/[0.04] border border-transparent"
                  )}
                >
                  <div className={cn(
                    "w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0",
                    activeSection === section.id ? "bg-wa-green/15 text-wa-green" : "bg-foreground/[0.04] text-slate-500 group-hover:text-foreground"
                  )}>
                    {section.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{section.title}</p>
                    <p className="text-[10px] text-slate-500 truncate">{section.description}</p>
                  </div>
                  <ChevronRight className={cn("w-4 h-4 text-slate-600 transition-transform", activeSection === section.id && "text-wa-green rotate-90")} />
                </button>
              ))}
            </div>

            {/* Content Area */}
            <div className="flex-1">
              {isLoading ? (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="w-8 h-8 text-wa-green animate-spin" />
                </div>
              ) : activeSection === "general" && (
                <div className="glass-card p-6 space-y-6 opacity-0 animate-fade-in">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground mb-1">General Settings</h3>
                    <p className="text-xs text-slate-500">Configure your organization defaults</p>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Organization Name</label>
                      <input type="text" defaultValue={settings?.organization_name || "Neural Center"} className="w-full h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Default Timezone</label>
                      <input type="text" defaultValue={settings?.timezone || "Asia/Kolkata (IST)"} className="w-full h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Default Language</label>
                      <input type="text" defaultValue={settings?.language || "English (en)"} className="w-full h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]" />
                    </div>
                    <div className="flex items-center justify-between p-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.06]">
                      <div>
                        <p className="text-sm text-foreground font-medium">Auto-assign conversations</p>
                        <p className="text-xs text-slate-500">Automatically assign new conversations to available agents</p>
                      </div>
                      <button className="text-wa-green"><ToggleRight className="w-8 h-8" /></button>
                    </div>
                    <div className="flex items-center justify-between p-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.06]">
                      <div>
                        <p className="text-sm text-foreground font-medium">AI Auto-respond</p>
                        <p className="text-xs text-slate-500">Allow AI agents to respond without human approval</p>
                      </div>
                      <button className="text-wa-green"><ToggleRight className="w-8 h-8" /></button>
                    </div>
                  </div>
                  <div className="flex justify-end pt-4 border-t border-foreground/[0.06]">
                    <button className="h-9 px-5 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm">
                      <Save className="w-4 h-4" /> Save Changes
                    </button>
                  </div>
                </div>
              )}

              {activeSection === "whatsapp" && (
                <div className="glass-card p-6 space-y-6 opacity-0 animate-fade-in">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground mb-1">WhatsApp Configuration</h3>
                    <p className="text-xs text-slate-500">Meta Business API settings</p>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Phone Number ID</label>
                      <input type="text" defaultValue={settings?.whatsapp?.phone_number_id || ""} placeholder="•••••••••1234" className="w-full h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Access Token</label>
                      <input type="password" defaultValue={settings?.whatsapp?.access_token || ""} placeholder="EAAxxxxxxxx" className="w-full h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Webhook Verify Token</label>
                      <input type="text" defaultValue="•••••••••" className="w-full h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1.5">Webhook URL</label>
                      <div className="flex gap-2">
                        <input type="text" defaultValue="https://api.neural.io/api/v1/webhooks/whatsapp" className="flex-1 h-10 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all hover:bg-foreground/[0.05]" readOnly />
                        <button className="w-10 h-10 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground transition-colors">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-end pt-4 border-t border-foreground/[0.06]">
                    <button className="h-9 px-5 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-semibold rounded-xl flex items-center gap-2 transition-all text-sm">
                      <Save className="w-4 h-4" /> Save Changes
                    </button>
                  </div>
                </div>
              )}

              {activeSection !== "general" && activeSection !== "whatsapp" && (
                <div className="glass-card p-6 opacity-0 animate-fade-in">
                  <div className="text-center py-12">
                    <Settings2 className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                    <h3 className="text-sm font-semibold text-foreground mb-1">{settingSections.find((s) => s.id === activeSection)?.title}</h3>
                    <p className="text-xs text-slate-500 max-w-sm mx-auto">
                      {settingSections.find((s) => s.id === activeSection)?.description}. Configuration panel coming soon.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
