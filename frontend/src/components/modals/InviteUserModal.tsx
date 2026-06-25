import { useState } from "react"
import { Modal } from "@/components/Modal"
import { api } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { Loader2, ShieldCheck, UserCheck, Eye } from "lucide-react"
import { cn } from "@/lib/utils"

interface InviteUserModalProps {
  isOpen: boolean
  onClose: () => void
}

const roleOptions = [
  { id: "admin", label: "Admin", icon: ShieldCheck, desc: "Full platform access" },
  { id: "agent", label: "Agent", icon: UserCheck, desc: "Can manage tickets and conversations" },
  { id: "viewer", label: "Viewer", icon: Eye, desc: "Read-only access" },
]

export function InviteUserModal({ isOpen, onClose }: InviteUserModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    email: "",
    full_name: "",
    role: "agent",
  })

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await api.post("/users", data)
      return res.data
    },
    onSuccess: () => {
      toast.success("User invited successfully")
      queryClient.invalidateQueries({ queryKey: ["users"] })
      onClose()
      setFormData({ email: "", full_name: "", role: "agent" })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error || "Failed to invite user")
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
      title="Invite Team Member"
      description="Add a new user to your organization workspace."
      className="max-w-xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Full Name</label>
            <input
              required
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              placeholder="e.g. John Doe"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Email Address</label>
            <input
              required
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="john@example.com"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Access Role</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {roleOptions.map((role) => {
                const isSelected = formData.role === role.id
                return (
                  <div
                    key={role.id}
                    onClick={() => setFormData({ ...formData, role: role.id })}
                    className={cn(
                      "relative p-4 rounded-xl border cursor-pointer transition-all duration-200 group flex flex-col",
                      isSelected
                        ? "bg-wa-green/10 border-wa-green shadow-[0_0_20px_rgba(37,211,102,0.15)]"
                        : "bg-foreground/[0.02] border-foreground/[0.08] hover:border-foreground/[0.15] hover:bg-foreground/[0.04]"
                    )}
                  >
                    {isSelected && (
                      <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-wa-green animate-pulse" />
                    )}
                    <div className={cn(
                      "w-8 h-8 rounded-lg flex items-center justify-center mb-3 transition-colors",
                      isSelected ? "bg-wa-green text-slate-950" : "bg-foreground/[0.04] text-slate-500 group-hover:text-foreground"
                    )}>
                      <role.icon className="w-4 h-4" />
                    </div>
                    <h4 className={cn("text-sm font-semibold mb-1", isSelected ? "text-wa-green" : "text-foreground")}>{role.label}</h4>
                    <p className="text-[10px] text-slate-500 leading-relaxed">{role.desc}</p>
                  </div>
                )
              })}
            </div>
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
            disabled={isPending || !formData.full_name || !formData.email}
            className="h-11 px-6 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-bold rounded-xl flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(37,211,102,0.15)] hover:shadow-[0_0_30px_rgba(37,211,102,0.25)]"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Send Invite"}
          </button>
        </div>
      </form>
    </Modal>
  )
}
