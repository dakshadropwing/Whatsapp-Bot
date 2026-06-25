"use client"

import { cn } from "@/lib/utils"

interface MiniChartProps {
  data: { label: string; inbound: number; outbound: number }[]
  className?: string
}

export function MiniBarChart({ data, className }: MiniChartProps) {
  const maxVal = data.length > 0 ? Math.max(...data.flatMap((d) => [d.inbound, d.outbound])) : 0

  return (
    <div className={cn("w-full", className)}>
      {/* Y-axis labels */}
      <div className="flex items-end gap-1 h-[200px] relative px-2">
        {/* Grid lines */}
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center gap-2 w-full">
              <span className="text-[9px] text-slate-600 w-6 text-right font-mono">
                {Math.round(maxVal - (maxVal / 4) * i)}
              </span>
              <div className="flex-1 h-px bg-foreground/[0.04]" />
            </div>
          ))}
        </div>

        {/* Bars */}
        <div className="flex items-end gap-[6px] flex-1 ml-8 relative z-10 h-full pb-1 pt-4">
          {data.map((d, i) => {
            const inH = maxVal > 0 ? (d.inbound / maxVal) * 100 : 0
            const outH = maxVal > 0 ? (d.outbound / maxVal) * 100 : 0
            return (
              <div key={i} className="flex-1 flex items-end gap-[2px] h-full group cursor-pointer relative">
                {/* Tooltip */}
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 border border-foreground/10 rounded-lg px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity z-20 whitespace-nowrap shadow-xl">
                  <p className="text-[9px] text-slate-400">{d.label}</p>
                  <div className="flex gap-2">
                    <span className="text-[9px] text-wa-green">↑{d.inbound}</span>
                    <span className="text-[9px] text-wa-teal">↓{d.outbound}</span>
                  </div>
                </div>

                <div
                  className="flex-1 bg-wa-green/60 rounded-t-sm hover:bg-wa-green/80 transition-all duration-500"
                  style={{ height: `${inH}%`, transitionDelay: `${i * 30}ms` }}
                />
                <div
                  className="flex-1 bg-wa-teal/40 rounded-t-sm hover:bg-wa-teal/60 transition-all duration-500"
                  style={{ height: `${outH}%`, transitionDelay: `${i * 30 + 15}ms` }}
                />
              </div>
            )
          })}
        </div>
      </div>

      {/* X-axis labels */}
      <div className="flex gap-[6px] ml-8 mt-2 px-2">
        {data.map((d, i) => (
          <div key={i} className="flex-1 text-center">
            <span className="text-[8px] text-slate-600 font-mono">{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

interface DonutChartProps {
  segments: { label: string; value: number; color: string }[]
  centerLabel: string
  centerValue: string
  className?: string
}

export function DonutChart({ segments, centerLabel, centerValue, className }: DonutChartProps) {
  const total = segments.reduce((sum, s) => sum + s.value, 0)
  let cumulativePercent = 0

  const SIZE = 120
  const STROKE_WIDTH = 12
  const RADIUS = (SIZE - STROKE_WIDTH) / 2
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg width={SIZE} height={SIZE} className="-rotate-90">
        {/* Background ring */}
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--border)"
          strokeWidth={STROKE_WIDTH}
        />
        {/* Segments */}
        {segments.map((seg, i) => {
          const percent = total > 0 ? seg.value / total : 0
          const dashLength = CIRCUMFERENCE * percent
          const dashOffset = -CIRCUMFERENCE * cumulativePercent
          cumulativePercent += percent
          return (
            <circle
              key={i}
              cx={SIZE / 2}
              cy={SIZE / 2}
              r={RADIUS}
              fill="none"
              stroke={seg.color}
              strokeWidth={STROKE_WIDTH}
              strokeDasharray={`${dashLength} ${CIRCUMFERENCE - dashLength}`}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              className="transition-all duration-1000"
              style={{ transitionDelay: `${i * 100}ms` }}
            />
          )
        })}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold text-foreground font-outfit">{centerValue}</span>
        <span className="text-[9px] text-slate-500 uppercase tracking-wider">{centerLabel}</span>
      </div>
    </div>
  )
}
