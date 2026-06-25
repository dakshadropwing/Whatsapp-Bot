import { useState } from "react"
import { Modal } from "@/components/Modal"
import { api } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { Loader2, MessageSquare, Ticket, CheckCircle, Clock, MousePointer2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface CreateWorkflowModalProps {
  isOpen: boolean
  onClose: () => void
}

const triggerOptions = [
  { id: "message_received", label: "Message Received", icon: MessageSquare, desc: "When a new WhatsApp message arrives" },
  { id: "ticket_created", label: "Ticket Created", icon: Ticket, desc: "When a new support ticket is opened" },
  { id: "conversation_closed", label: "Chat Closed", icon: CheckCircle, desc: "When an agent marks a chat resolved" },
  { id: "scheduled", label: "Scheduled", icon: Clock, desc: "Run periodically or at a specific time" },
  { id: "manual", label: "Manual Action", icon: MousePointer2, desc: "Triggered manually by team members" },
]

export function CreateWorkflowModal({ isOpen, onClose }: CreateWorkflowModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    trigger: "message_received",
  })

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await api.post("/workflows", data)
      return res.data
    },
    onSuccess: () => {
      toast.success("Workflow created successfully")
      queryClient.invalidateQueries({ queryKey: ["workflows"] })
      onClose()
      setFormData({ name: "", description: "", trigger: "message_received" })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error || "Failed to create workflow")
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
      title="Create New Workflow"
      description="Design a new automated sequence for your platform."
      className="max-w-2xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Workflow Name</label>
            <input
              required
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. New Lead Onboarding"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Description</label>
            <input
              required
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="What does this workflow do?"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Select Trigger</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {triggerOptions.map((option) => {
              const isSelected = formData.trigger === option.id
              return (
                <div
                  key={option.id}
                  onClick={() => setFormData({ ...formData, trigger: option.id })}
                  className={cn(
                    "relative p-4 rounded-xl border cursor-pointer transition-all duration-200 group",
                    isSelected
                      ? "bg-wa-green/10 border-wa-green shadow-[0_0_20px_rgba(37,211,102,0.15)]"
                      : "bg-foreground/[0.02] border-foreground/[0.08] hover:border-foreground/[0.15] hover:bg-foreground/[0.04]"
                  )}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-wa-green animate-pulse" />
                  )}
                  <div className={cn(
                    "w-10 h-10 rounded-lg flex items-center justify-center mb-3 transition-colors",
                    isSelected ? "bg-wa-green text-slate-950" : "bg-foreground/[0.04] text-slate-500 group-hover:text-foreground"
                  )}>
                    <option.icon className="w-5 h-5" />
                  </div>
                  <h4 className={cn("text-sm font-semibold mb-1", isSelected ? "text-wa-green" : "text-foreground")}>{option.label}</h4>
                  <p className="text-[10px] text-slate-500 leading-relaxed">{option.desc}</p>
                </div>
              )
            })}
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
            disabled={isPending || !formData.name || !formData.description}
            className="h-11 px-6 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-bold rounded-xl flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(37,211,102,0.15)] hover:shadow-[0_0_30px_rgba(37,211,102,0.25)]"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Workflow"}
          </button>
        </div>
      </form>
    </Modal>
  )
}
