"use client"

import { Search, Bell, Command, Sun, Moon, Swords, Ticket, CheckCircle2 } from "lucide-react"
import { useEffect, useState, useRef } from "react"
import { useTickets } from "@/hooks/useQueries"
import { timeAgo } from "@/lib/utils"
import toast from "react-hot-toast"

type Theme = "dark" | "light" | "war";

interface TopBarProps {
  title: string
  subtitle?: string
  actions?: React.ReactNode
}

export function TopBar({ title, subtitle, actions }: TopBarProps) {
  const [theme, setTheme] = useState<Theme>("dark");
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  const { data: ticketsResponse } = useTickets({ status: "open" })
  const openTicketsCount = ticketsResponse?.total || ticketsResponse?.data?.length || 0;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleMarkAllRead = () => {
    toast.success("All notifications marked as read!");
    setShowNotifications(false);
  };

  useEffect(() => {
    // Remove all theme classes first
    document.documentElement.classList.remove("light", "war");
    if (theme !== "dark") {
      document.documentElement.classList.add(theme);
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === "dark" ? "light" : prev === "light" ? "war" : "dark");
  };

  return (
    <header className="h-16 flex items-center justify-between px-8 border-b border-foreground/[0.08] bg-background/60 backdrop-blur-xl sticky top-0 z-40 transition-colors duration-300">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight font-outfit">{title}</h1>
        {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Search Bar */}
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-wa-green transition-colors z-10" />
          <input
            type="text"
            placeholder="Search..."
            className="w-56 focus:w-72 h-9 pl-9 pr-10 rounded-full bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground placeholder:text-slate-500 focus:outline-none focus:border-wa-green/40 focus:bg-foreground/[0.05] focus:ring-4 focus:ring-wa-green/10 transition-all duration-300 ease-out"
          />
          <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1 text-slate-500 pointer-events-none">
            <Command className="w-3 h-3" />
            <span className="text-[10px] font-bold">K</span>
          </div>
        </div>

        <div className="w-px h-5 bg-foreground/[0.08] mx-1" />

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative w-9 h-9 rounded-full bg-foreground/[0.03] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground hover:bg-foreground/[0.08] hover:border-foreground/[0.15] hover:scale-105 active:scale-95 transition-all">
            <Bell className="w-4 h-4" />
            {openTicketsCount > 0 && (
              <div className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-wa-rose rounded-full flex items-center justify-center border-2 border-background">
                <span className="text-[9px] font-bold text-white">{openTicketsCount}</span>
              </div>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-3 w-80 rounded-2xl glass-card overflow-hidden shadow-2xl animate-fade-in-up border border-foreground/[0.08] z-50">
              <div className="p-4 border-b border-foreground/[0.06] flex items-center justify-between">
                <h3 className="font-semibold text-sm text-foreground">Notifications</h3>
                <button onClick={handleMarkAllRead} className="text-xs text-wa-green cursor-pointer hover:underline font-medium bg-transparent border-none">Mark all read</button>
              </div>
              <div className="max-h-[320px] overflow-y-auto no-scrollbar">
                {ticketsResponse?.data?.slice(0, 5).map((ticket: any) => (
                  <div key={ticket.id} className="p-4 border-b border-foreground/[0.03] hover:bg-foreground/[0.04] transition-colors cursor-pointer flex gap-3 group">
                    <div className="w-8 h-8 rounded-full bg-wa-rose/10 flex items-center justify-center flex-shrink-0 mt-0.5 border border-wa-rose/20">
                      <Ticket className="w-4 h-4 text-wa-rose group-hover:scale-110 transition-transform" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate group-hover:text-wa-green transition-colors">Ticket #{ticket.id}</p>
                      <p className="text-xs text-slate-500 mt-0.5 truncate">{ticket.subject || ticket.customerName || "Requires agent attention"}</p>
                      <p className="text-[10px] text-slate-600 mt-1.5 font-medium">{timeAgo(ticket.created_at || ticket.createdAt || new Date())}</p>
                    </div>
                  </div>
                ))}
                {(!ticketsResponse?.data || ticketsResponse.data.length === 0) && (
                  <div className="p-8 flex flex-col items-center justify-center text-center">
                    <div className="w-12 h-12 rounded-full bg-wa-green/10 flex items-center justify-center mb-3">
                      <CheckCircle2 className="w-6 h-6 text-wa-green" />
                    </div>
                    <p className="text-sm font-medium text-foreground">All caught up!</p>
                    <p className="text-xs text-slate-500 mt-1">No new notifications.</p>
                  </div>
                )}
              </div>
              <div className="p-3 border-t border-foreground/[0.06] bg-foreground/[0.02] text-center">
                <a href="/tickets" className="text-xs text-wa-green hover:text-wa-green-dark transition-colors font-semibold">View all activity</a>
              </div>
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button 
          onClick={toggleTheme}
          title={`Switch Theme (Current: ${theme})`}
          className="relative w-9 h-9 rounded-full bg-foreground/[0.03] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground hover:bg-foreground/[0.08] hover:border-foreground/[0.15] hover:scale-105 active:scale-95 transition-all">
          {theme === "light" ? <Sun className="w-4 h-4" /> : theme === "war" ? <Swords className="w-4 h-4 text-wa-rose" /> : <Moon className="w-4 h-4" />}
        </button>

        <div className="w-px h-5 bg-foreground/[0.08] mx-1" />

        {/* Extra Actions */}
        {actions}
      </div>
    </header>
  )
}
