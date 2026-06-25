import { useState } from "react"
import { Modal } from "@/components/Modal"
import { api } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { Loader2, ShieldAlert, Headset, TrendingUp, Calendar, UserCheck, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

interface CreateAgentModalProps {
  isOpen: boolean
  onClose: () => void
}

const roleOptions = [
  { id: "support", label: "Support", icon: Headset },
  { id: "sales", label: "Sales", icon: TrendingUp },
  { id: "lead", label: "Lead Capture", icon: UserCheck },
  { id: "appointment", label: "Appointment", icon: Calendar },
  { id: "supervisor", label: "Supervisor", icon: ShieldAlert },
]

export function CreateAgentModal({ isOpen, onClose }: CreateAgentModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: "",
    role_type: "support",
    system_prompt: "",
    provider: "gemini",
    model_name: "gemini-2.5-flash",
  })

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await api.post("/agents", data)
      return res.data
    },
    onSuccess: () => {
      toast.success("Agent created successfully")
      queryClient.invalidateQueries({ queryKey: ["agents"] })
      onClose()
      setFormData({
        name: "",
        role_type: "support",
        system_prompt: "",
        provider: "gemini",
        model_name: "gemini-2.5-flash",
      })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error || "Failed to create agent")
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
      title="Create AI Agent"
      description="Configure a new AI agent for your platform."
      className="max-w-2xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div className="col-span-2">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Agent Name</label>
            <input
              required
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. Tier 1 Support Bot"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Agent Role</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              {roleOptions.map((role) => {
                const isSelected = formData.role_type === role.id
                return (
                  <div
                    key={role.id}
                    onClick={() => setFormData({ ...formData, role_type: role.id })}
                    className={cn(
                      "relative p-3 rounded-xl border cursor-pointer transition-all duration-200 flex flex-col items-center justify-center text-center",
                      isSelected
                        ? "bg-wa-purple/10 border-wa-purple shadow-[0_0_20px_rgba(139,92,246,0.15)]"
                        : "bg-foreground/[0.02] border-foreground/[0.08] hover:border-foreground/[0.15] hover:bg-foreground/[0.04]"
                    )}
                  >
                    <role.icon className={cn("w-5 h-5 mb-2 transition-colors", isSelected ? "text-wa-purple" : "text-slate-500")} />
                    <span className={cn("text-xs font-semibold", isSelected ? "text-wa-purple" : "text-foreground")}>{role.label}</span>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">AI Provider</label>
            <div className="relative">
              <select
                value={formData.provider}
                onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                className="w-full h-12 px-4 pr-10 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all appearance-none hover:bg-foreground/[0.05] cursor-pointer"
              >
                <option value="gemini" className="bg-slate-900 text-white">Google Gemini</option>
                <option value="ollama" className="bg-slate-900 text-white">Ollama (Local)</option>
              </select>
              <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Model Name</label>
            <input
              required
              type="text"
              value={formData.model_name}
              onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
              placeholder="e.g. gemini-2.5-flash"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">System Prompt</label>
            <textarea
              required
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              placeholder="You are a helpful assistant..."
              className="w-full h-32 p-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground font-mono focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all resize-none placeholder:text-slate-500 hover:bg-foreground/[0.05]"
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
            disabled={isPending || !formData.name || !formData.system_prompt}
            className="h-11 px-6 bg-wa-purple hover:bg-wa-purple-dark text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(139,92,246,0.15)] hover:shadow-[0_0_30px_rgba(139,92,246,0.25)]"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Agent"}
          </button>
        </div>
      </form>
    </Modal>
  )
}
