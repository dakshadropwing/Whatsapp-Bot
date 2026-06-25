"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import {
  MessageSquare,
  LayoutDashboard,
  Ticket,
  Bot,
  Workflow,
  Code2,
  Settings2,
  Users,
  Building2,
  ChevronLeft,
  ChevronRight,
  Zap,
  LogOut,
  Bell,
  BarChart2,
  Webhook,
  Briefcase,
  Smartphone,
  ShieldCheck,
  FileText
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"
import { useTickets } from "@/hooks/useQueries"

const NAV_ITEMS = [
  {
    title: "Main",
    items: [
      { icon: LayoutDashboard, label: "Dashboard", href: "/", badge: null },
      { icon: MessageSquare, label: "Conversations", href: "/conversations", badge: null },
      { icon: Ticket, label: "Tickets", href: "/tickets", badge: "DYNAMIC_TICKETS" },
      { icon: BarChart2, label: "Analytics", href: "/analytics", badge: null },
    ],
  },
  {
    title: "AI & Automation",
    items: [
      { icon: Bot, label: "Agents", href: "/agents", badge: null },
      { icon: Workflow, label: "Workflows", href: "/workflows", badge: null },
      { icon: Code2, label: "Prompts", href: "/prompts", badge: null },
      { icon: Webhook, label: "Endpoints", href: "/endpoints", badge: null },
    ],
  },
  {
    title: "Platform",
    items: [
      { icon: Smartphone, label: "WhatsApp", href: "/whatsapp", badge: null },
      { icon: Building2, label: "Clients", href: "/clients", badge: null },
      { icon: Users, label: "Users", href: "/users", badge: null },
      { icon: Briefcase, label: "Employees", href: "/employees", badge: null },
    ],
  },
  {
    title: "Administration",
    items: [
      { icon: ShieldCheck, label: "Security", href: "/security", badge: null },
      { icon: FileText, label: "Audit Logs", href: "/audit", badge: null },
      { icon: Settings2, label: "Settings", href: "/settings", badge: null },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuthStore()
  
  // Fetch real alerts data
  const { data: ticketsResponse } = useTickets({ status: "open" }, { enabled: pathname !== "/login" })
  const openTicketsCount = ticketsResponse?.total || ticketsResponse?.data?.length || 0;

  if (pathname === "/login") return null;

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  return (
    <aside
      className={cn(
        "flex-shrink-0 flex flex-col bg-transparent h-screen sticky top-0 transition-all duration-300 ease-out z-50",
        collapsed ? "w-[72px]" : "w-[260px]"
      )}
    >
      {/* ── Brand ─────────────────────────────────── */}
      <div className="h-16 flex items-center px-4 relative">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-wa-green to-wa-teal flex items-center justify-center shadow-[0_0_20px_rgba(37,211,102,0.25)] flex-shrink-0 relative">
            <Zap className="w-5 h-5 text-foreground" />
            <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-wa-green rounded-full border-2 border-card animate-pulse-glow" />
          </div>
          {!collapsed && (
            <div className="animate-fade-in min-w-0">
              <h1 className="font-bold text-foreground tracking-tight text-sm leading-tight">Persynix Bot</h1>
              <p className="text-[10px] text-wa-green font-semibold uppercase tracking-[0.2em]">Enterprise</p>
            </div>
          )}
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-background border border-foreground/10 flex items-center justify-center text-slate-500 hover:text-foreground hover:bg-foreground/[0.04] transition-all z-10 shadow-lg",
          )}
        >
          {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
        </button>
      </div>

      {/* ── Navigation ────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto py-5 px-3 space-y-6 no-scrollbar">
        {NAV_ITEMS.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <h2 className="px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-[0.15em] mb-2.5">
                {section.title}
              </h2>
            )}
            {collapsed && <div className="w-6 h-px bg-foreground/[0.06] mx-auto mb-3" />}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
                const displayBadge = item.badge === "DYNAMIC_TICKETS" ? (openTicketsCount > 0 ? openTicketsCount : null) : item.badge;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 group relative",
                      collapsed ? "justify-center px-0 py-2.5 mx-auto w-11 h-11" : "px-3 py-2.5",
                      isActive
                        ? "text-foreground bg-gradient-to-r from-wa-green/20 to-transparent border border-wa-green/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]"
                        : "text-slate-400 hover:text-foreground hover:bg-foreground/[0.04] border border-transparent"
                    )}
                    title={collapsed ? item.label : undefined}
                  >
                    {/* Active indicator bar */}
                    {isActive && (
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-wa-green shadow-[0_0_8px_rgba(37,211,102,0.5)]" />
                    )}

                    <item.icon
                      className={cn(
                        "w-[18px] h-[18px] flex-shrink-0 transition-colors duration-200",
                        isActive ? "text-wa-green" : "text-slate-500 group-hover:text-wa-green"
                      )}
                    />

                    {!collapsed && (
                      <>
                        <span className="flex-1">{item.label}</span>
                        {displayBadge && (
                          <span className={cn(
                            "min-w-[20px] h-5 px-1.5 rounded-md text-[10px] font-bold flex items-center justify-center transition-colors",
                            isActive
                              ? "bg-wa-green/20 text-wa-green border border-wa-green/30"
                              : "bg-foreground/[0.06] text-slate-500 border border-transparent group-hover:border-foreground/[0.1]"
                          )}>
                            {displayBadge}
                          </span>
                        )}
                      </>
                    )}

                    {/* Tooltip for collapsed mode */}
                    {collapsed && (
                      <div className="absolute left-full ml-2 px-2.5 py-1 rounded-lg bg-background text-foreground text-xs font-medium whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity shadow-xl border border-foreground/10 z-50">
                        {item.label}
                        {displayBadge && (
                          <span className="ml-1.5 text-wa-green font-bold">({displayBadge})</span>
                        )}
                      </div>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* ── Quick Actions ─────────────────────────── */}
      {!collapsed && (
        <div className="px-3 pb-4">
          <div className="p-3.5 rounded-xl bg-gradient-to-br from-wa-purple/10 to-wa-blue/5 border border-wa-purple/20 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-wa-purple/10 rounded-full blur-2xl group-hover:bg-wa-purple/20 transition-colors" />
            <div className="flex items-center gap-2 mb-2 relative z-10">
              <div className="w-6 h-6 rounded-md bg-wa-purple/20 flex items-center justify-center border border-wa-purple/30">
                <Bell className="w-3.5 h-3.5 text-wa-purple" />
              </div>
              <span className="text-xs font-semibold text-foreground tracking-tight">{openTicketsCount} System Alerts</span>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed relative z-10">
              {openTicketsCount} tickets need attention <br /> 0 agents offline
            </p>
          </div>
        </div>
      )}

      {/* ── User Profile ──────────────────────────── */}
      <div className="p-3">
        <div className={cn(
          "flex items-center gap-3 rounded-xl hover:bg-foreground/[0.06] transition-all cursor-pointer border border-transparent hover:border-foreground/[0.08] group relative",
          collapsed ? "justify-center p-2.5" : "p-3"
        )} onClick={handleLogout}>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-wa-blue/20 to-wa-purple/20 flex items-center justify-center text-wa-blue font-bold text-sm border border-wa-blue/30 flex-shrink-0 relative">
            {user?.full_name?.charAt(0) || "A"}
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-wa-green rounded-full border-2 border-card" />
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0 animate-fade-in">
              <p className="text-sm font-semibold text-foreground truncate group-hover:text-wa-blue transition-colors">{user?.full_name || "Admin User"}</p>
              <p className="text-[11px] text-muted-foreground truncate">{user?.email || "admin@persynix.io"}</p>
            </div>
          )}
          {!collapsed && (
            <div className="w-8 h-8 rounded-md hover:bg-wa-rose/10 flex items-center justify-center transition-colors group/logout">
              <LogOut className="w-4 h-4 text-slate-500 group-hover/logout:text-wa-rose transition-colors flex-shrink-0" />
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
