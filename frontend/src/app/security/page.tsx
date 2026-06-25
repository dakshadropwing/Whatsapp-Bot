"use client"

import { TopBar } from "@/components/TopBar"
import { ShieldAlert, Smartphone, Key, MonitorSmartphone, LogOut, CheckCircle2 } from "lucide-react"

export default function SecurityPage() {
  return (
    <div className="flex flex-col h-full">
      <TopBar title="Security" subtitle="Protect your account and organization" />
      
      <div className="flex-1 overflow-y-auto p-8 pb-20">
        <div className="max-w-[1400px] mx-auto space-y-6">

          <div className="grid grid-cols-2 gap-6 opacity-0 animate-fade-in-up">
            
            {/* Password & MFA */}
            <div className="space-y-6">
              <div className="glass-card p-6">
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-wa-green/10 border border-wa-green/20 flex items-center justify-center flex-shrink-0">
                    <Key className="w-5 h-5 text-wa-green" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">Change Password</h3>
                    <p className="text-xs text-slate-500 mt-1">Ensure your account uses a long, random password.</p>
                  </div>
                </div>
                
                <form className="space-y-4">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1.5">Current Password</label>
                    <input type="password" placeholder="••••••••" className="w-full h-10 px-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all hover:bg-foreground/[0.05]" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1.5">New Password</label>
                    <input type="password" placeholder="••••••••" className="w-full h-10 px-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all hover:bg-foreground/[0.05]" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1.5">Confirm New Password</label>
                    <input type="password" placeholder="••••••••" className="w-full h-10 px-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-1 focus:ring-wa-green/30 transition-all hover:bg-foreground/[0.05]" />
                  </div>
                  <div className="pt-2">
                    <button type="button" className="h-9 px-4 rounded-xl bg-foreground/[0.04] border border-foreground/[0.08] text-sm text-foreground font-medium hover:bg-foreground/[0.08] transition-colors">
                      Update Password
                    </button>
                  </div>
                </form>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-wa-purple/10 border border-wa-purple/20 flex items-center justify-center flex-shrink-0">
                    <Smartphone className="w-5 h-5 text-wa-purple" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-foreground">Two-Factor Authentication</h3>
                      <span className="px-2 py-1 rounded text-[10px] font-bold bg-wa-green/10 text-wa-green flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Enabled
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">Add additional security to your account using an authenticator app.</p>
                  </div>
                </div>
                
                <div className="p-4 rounded-xl bg-foreground/[0.02] border border-foreground/[0.04]">
                  <p className="text-sm text-foreground font-medium mb-1">Authenticator App</p>
                  <p className="text-xs text-slate-500 mb-4">Configured via Google Authenticator.</p>
                  <button className="text-xs font-medium text-wa-amber hover:text-wa-amber/80 transition-colors">Disable 2FA</button>
                </div>
              </div>
            </div>

            {/* Active Sessions */}
            <div className="space-y-6">
              <div className="glass-card p-6 h-full">
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-wa-blue/10 border border-wa-blue/20 flex items-center justify-center flex-shrink-0">
                    <MonitorSmartphone className="w-5 h-5 text-wa-blue" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-foreground">Active Sessions</h3>
                      <button className="text-xs font-medium text-wa-amber hover:text-wa-amber/80 transition-colors">Revoke All</button>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">Manage devices currently logged into your account.</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {/* Current Session */}
                  <div className="p-4 rounded-xl bg-wa-blue/5 border border-wa-blue/20">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <MonitorSmartphone className="w-4 h-4 text-wa-blue" />
                          <h4 className="text-sm font-semibold text-foreground">Current Browser</h4>
                        </div>
                        <p className="text-xs text-slate-500">Active now</p>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-wa-blue/10 text-wa-blue">Current</span>
                    </div>
                  </div>

                  <div className="text-center py-10 space-y-3">
                    <div className="w-12 h-12 rounded-full bg-foreground/[0.03] flex items-center justify-center mx-auto text-slate-400">
                      <ShieldAlert className="w-5 h-5" />
                    </div>
                    <p className="text-sm text-slate-500">Advanced session management is coming in a future release.</p>
                  </div>
                </div>
                
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  )
}
