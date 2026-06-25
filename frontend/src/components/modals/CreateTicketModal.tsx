import { useState } from "react"
import { Modal } from "@/components/Modal"
import { api } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { Loader2, ArrowDownCircle, AlertCircle, AlertTriangle, Flame } from "lucide-react"
import { cn } from "@/lib/utils"

interface CreateTicketModalProps {
  isOpen: boolean
  onClose: () => void
}

const priorityOptions = [
  { id: "low", label: "Low", icon: ArrowDownCircle, color: "text-slate-400" },
  { id: "normal", label: "Normal", icon: AlertCircle, color: "text-wa-green" },
  { id: "high", label: "High", icon: AlertTriangle, color: "text-wa-amber" },
  { id: "urgent", label: "Urgent", icon: Flame, color: "text-wa-rose" },
]

export function CreateTicketModal({ isOpen, onClose }: CreateTicketModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    priority: "normal",
  })

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await api.post("/tickets", data)
      return res.data
    },
    onSuccess: () => {
      toast.success("Ticket created successfully")
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
      onClose()
      setFormData({ title: "", description: "", priority: "normal" })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error || "Failed to create ticket")
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutate(formData)
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Ticket"
      description="Open a manual support ticket for team follow-up."
      className="max-w-xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-6">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Ticket Title</label>
            <input
              required
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g. Refund request for order #123"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Priority Level</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {priorityOptions.map((priority) => {
                const isSelected = formData.priority === priority.id
                return (
                  <div
                    key={priority.id}
                    onClick={() => setFormData({ ...formData, priority: priority.id })}
                    className={cn(
                      "relative p-3 rounded-xl border cursor-pointer transition-all duration-200 flex flex-col items-center justify-center text-center",
                      isSelected
                        ? "bg-wa-green/10 border-wa-green shadow-[0_0_20px_rgba(37,211,102,0.15)]"
                        : "bg-foreground/[0.02] border-foreground/[0.08] hover:border-foreground/[0.15] hover:bg-foreground/[0.04]"
                    )}
                  >
                    <priority.icon className={cn("w-5 h-5 mb-2 transition-colors", isSelected ? priority.color : "text-slate-500")} />
                    <span className={cn("text-xs font-semibold", isSelected ? "text-foreground" : "text-slate-400")}>{priority.label}</span>
                  </div>
                )
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Description</label>
            <textarea
              required
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Provide complete details about the issue..."
              className="w-full h-32 p-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all resize-none placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6 border-t border-foreground/[0.06]">
          <button
            type="button"
            onClick={onClose}
            className="h-11 px-5 rounded-xl text-sm font-medium text-slate-400 hover:text-foreground hover:bg-foreground/[0.04] transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isPending || !formData.title || !formData.description}
            className="h-11 px-6 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-bold rounded-xl flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(37,211,102,0.15)] hover:shadow-[0_0_30px_rgba(37,211,102,0.25)]"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Ticket"}
          </button>
        </div>
      </form>
    </Modal>
  )
}
