import { X } from "lucide-react"
import { useEffect } from "react"
import { cn } from "@/lib/utils"

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  description?: string
  children: React.ReactNode
  className?: string
}

export function Modal({ isOpen, onClose, title, description, children, className }: ModalProps) {
  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "unset"
    }
    return () => {
      document.body.style.overflow = "unset"
    }
  }, [isOpen])

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div 
        className={cn(
          "relative w-full max-w-lg glass-card flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200 shadow-[0_0_40px_rgba(0,0,0,0.3)]",
          className
        )}
      >
        {/* Header */}
        <div className="flex flex-col gap-1 p-6 border-b border-foreground/[0.06] flex-shrink-0 relative overflow-hidden rounded-t-3xl">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-wa-green via-wa-teal to-wa-blue opacity-50" />
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">{title}</h2>
            <button 
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-foreground/[0.04] border border-foreground/[0.08] flex items-center justify-center text-slate-400 hover:text-foreground hover:bg-foreground/[0.08] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          {description && (
            <p className="text-sm text-slate-500">{description}</p>
          )}
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto no-scrollbar">
          {children}
        </div>
      </div>
    </div>
  )
}
