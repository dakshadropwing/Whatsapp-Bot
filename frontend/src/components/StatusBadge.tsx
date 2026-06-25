"use client"

import { cn } from "@/lib/utils"

interface StatusBadgeProps {
  status: string
  size?: "sm" | "md"
}

const statusConfig: Record<string, { label: string; className: string; dot: string }> = {
  // Conversation statuses
  active: { label: "Active", className: "text-wa-green bg-wa-green/10 border-wa-green/20", dot: "bg-wa-green" },
  waiting: { label: "Waiting", className: "text-wa-amber bg-wa-amber/10 border-wa-amber/20", dot: "bg-wa-amber" },
  bot_handling: { label: "AI Handling", className: "text-wa-purple bg-wa-purple/10 border-wa-purple/20", dot: "bg-wa-purple" },
  human_handling: { label: "Human", className: "text-wa-blue bg-wa-blue/10 border-wa-blue/20", dot: "bg-wa-blue" },
  escalated: { label: "Escalated", className: "text-wa-rose bg-wa-rose/10 border-wa-rose/20", dot: "bg-wa-rose" },
  resolved: { label: "Resolved", className: "text-slate-400 bg-slate-400/10 border-slate-400/20", dot: "bg-slate-400" },
  closed: { label: "Closed", className: "text-slate-500 bg-slate-500/10 border-slate-500/20", dot: "bg-slate-500" },

  // Ticket statuses
  open: { label: "Open", className: "text-wa-green bg-wa-green/10 border-wa-green/20", dot: "bg-wa-green" },
  in_progress: { label: "In Progress", className: "text-wa-blue bg-wa-blue/10 border-wa-blue/20", dot: "bg-wa-blue" },
  waiting_on_customer: { label: "Awaiting Reply", className: "text-wa-amber bg-wa-amber/10 border-wa-amber/20", dot: "bg-wa-amber" },

  // Priorities
  low: { label: "Low", className: "text-slate-400 bg-slate-400/10 border-slate-400/20", dot: "bg-slate-400" },
  medium: { label: "Medium", className: "text-wa-amber bg-wa-amber/10 border-wa-amber/20", dot: "bg-wa-amber" },
  high: { label: "High", className: "text-wa-rose bg-wa-rose/10 border-wa-rose/20", dot: "bg-wa-rose" },
  urgent: { label: "Urgent", className: "text-red-400 bg-red-400/10 border-red-400/20 animate-pulse", dot: "bg-red-400" },

  // Agent roles
  support: { label: "Support", className: "text-wa-green bg-wa-green/10 border-wa-green/20", dot: "bg-wa-green" },
  sales: { label: "Sales", className: "text-wa-blue bg-wa-blue/10 border-wa-blue/20", dot: "bg-wa-blue" },
  lead: { label: "Lead", className: "text-wa-amber bg-wa-amber/10 border-wa-amber/20", dot: "bg-wa-amber" },
  appointment: { label: "Appointment", className: "text-wa-cyan bg-wa-cyan/10 border-wa-cyan/20", dot: "bg-wa-cyan" },
  knowledge: { label: "Knowledge", className: "text-wa-purple bg-wa-purple/10 border-wa-purple/20", dot: "bg-wa-purple" },
  supervisor: { label: "Supervisor", className: "text-white bg-white/10 border-white/20", dot: "bg-white" },

  // User roles
  admin: { label: "Admin", className: "text-wa-rose bg-wa-rose/10 border-wa-rose/20", dot: "bg-wa-rose" },
  manager: { label: "Manager", className: "text-wa-purple bg-wa-purple/10 border-wa-purple/20", dot: "bg-wa-purple" },
  agent: { label: "Agent", className: "text-wa-blue bg-wa-blue/10 border-wa-blue/20", dot: "bg-wa-blue" },
  viewer: { label: "Viewer", className: "text-slate-400 bg-slate-400/10 border-slate-400/20", dot: "bg-slate-400" },

  // Workflow triggers
  message_received: { label: "On Message", className: "text-wa-green bg-wa-green/10 border-wa-green/20", dot: "bg-wa-green" },
  ticket_created: { label: "On Ticket", className: "text-wa-amber bg-wa-amber/10 border-wa-amber/20", dot: "bg-wa-amber" },
  conversation_closed: { label: "On Close", className: "text-wa-blue bg-wa-blue/10 border-wa-blue/20", dot: "bg-wa-blue" },
  manual: { label: "Manual", className: "text-slate-400 bg-slate-400/10 border-slate-400/20", dot: "bg-slate-400" },
  scheduled: { label: "Scheduled", className: "text-wa-purple bg-wa-purple/10 border-wa-purple/20", dot: "bg-wa-purple" },
}

export function StatusBadge({ status, size = "sm" }: StatusBadgeProps) {
  const config = statusConfig[status] || {
    label: status,
    className: "text-slate-400 bg-slate-400/10 border-slate-400/20",
    dot: "bg-slate-400",
  }

  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 font-semibold border rounded-lg",
      config.className,
      size === "sm" ? "text-[10px] px-2 py-0.5" : "text-xs px-2.5 py-1"
    )}>
      <span className={cn("w-1.5 h-1.5 rounded-full", config.dot)} />
      {config.label}
    </span>
  )
}
