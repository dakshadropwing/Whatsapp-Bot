"use client"

import { cn } from "@/lib/utils"
import { ArrowUpRight, ArrowDownRight, TrendingUp } from "lucide-react"

interface StatCardProps {
  title: string
  value: string
  trend: string
  trendDown?: boolean
  icon: React.ReactNode
  color?: "green" | "teal" | "purple" | "blue" | "amber" | "rose" | "cyan"
  sparkline?: number[]
  className?: string
  delay?: number
}

const colorMap = {
  green: {
    icon: "bg-wa-green/10 border-wa-green/20 text-wa-green",
    glow: "from-wa-green/8",
    sparkline: "bg-wa-green",
  },
  teal: {
    icon: "bg-wa-teal/10 border-wa-teal/20 text-wa-teal",
    glow: "from-wa-teal/8",
    sparkline: "bg-wa-teal",
  },
  purple: {
    icon: "bg-wa-purple/10 border-wa-purple/20 text-wa-purple",
    glow: "from-wa-purple/8",
    sparkline: "bg-wa-purple",
  },
  blue: {
    icon: "bg-wa-blue/10 border-wa-blue/20 text-wa-blue",
    glow: "from-wa-blue/8",
    sparkline: "bg-wa-blue",
  },
  amber: {
    icon: "bg-wa-amber/10 border-wa-amber/20 text-wa-amber",
    glow: "from-wa-amber/8",
    sparkline: "bg-wa-amber",
  },
  rose: {
    icon: "bg-wa-rose/10 border-wa-rose/20 text-wa-rose",
    glow: "from-wa-rose/8",
    sparkline: "bg-wa-rose",
  },
  cyan: {
    icon: "bg-wa-cyan/10 border-wa-cyan/20 text-wa-cyan",
    glow: "from-wa-cyan/8",
    sparkline: "bg-wa-cyan",
  },
}

export function StatCard({
  title,
  value,
  trend,
  trendDown = false,
  icon,
  color = "green",
  sparkline,
  className,
  delay = 0,
}: StatCardProps) {
  const colors = colorMap[color]

  return (
    <div
      className={cn(
        "glass-card p-5 relative overflow-hidden group cursor-default",
        "opacity-0 animate-fade-in-up",
        className
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Background glow */}
      <div className={cn("absolute -right-8 -top-8 w-28 h-28 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700", `bg-gradient-to-br ${colors.glow} to-transparent`)} />

      <div className="flex justify-between items-start mb-4 relative z-10">
        <div className={cn("w-11 h-11 rounded-xl flex items-center justify-center border", colors.icon)}>
          {icon}
        </div>
        <div className={cn(
          "flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-lg",
          trendDown
            ? "text-wa-rose bg-wa-rose/10 border border-wa-rose/15"
            : "text-wa-green bg-wa-green/10 border border-wa-green/15"
        )}>
          {trendDown
            ? <ArrowDownRight className="w-3 h-3" />
            : <ArrowUpRight className="w-3 h-3" />
          }
          {trend}
        </div>
      </div>

      <div className="relative z-10">
        <p className="text-xs font-medium text-slate-500 mb-1 tracking-wide">{title}</p>
        <p className="text-3xl font-bold text-foreground tracking-tight font-outfit">{value}</p>
      </div>

      {/* Mini sparkline */}
      {sparkline && sparkline.length > 0 && (
        <div className="flex items-end gap-[3px] mt-4 h-8 relative z-10">
          {sparkline.map((val, i) => {
            const maxVal = Math.max(...sparkline)
            const height = maxVal > 0 ? (val / maxVal) * 100 : 0
            return (
              <div
                key={i}
                className={cn("mini-bar flex-1 rounded-sm opacity-30 group-hover:opacity-60 transition-opacity", colors.sparkline)}
                style={{
                  height: `${height}%`,
                  transitionDelay: `${i * 50}ms`,
                }}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
