import { useState } from "react"
import { Modal } from "@/components/Modal"
import { api } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { Loader2, Building2, Mail, Phone, User } from "lucide-react"

interface CreateClientModalProps {
  isOpen: boolean
  onClose: () => void
}

export function CreateClientModal({ isOpen, onClose }: CreateClientModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    company: "",
  })

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await api.post("/clients", data)
      return res.data
    },
    onSuccess: () => {
      toast.success("Client added successfully")
      queryClient.invalidateQueries({ queryKey: ["clients"] })
      onClose()
      setFormData({ name: "", phone: "", email: "", company: "" })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error || "Failed to add client")
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
      title="Add New Client"
      description="Register a new contact or organization in your system."
      className="max-w-xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Full Name</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                required
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Jane Smith"
                className="w-full h-12 pl-11 pr-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
              />
            </div>
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Phone Number</label>
            <div className="relative">
              <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                required
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1 (555) 000-0000"
                className="w-full h-12 pl-11 pr-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
              />
            </div>
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="jane@example.com"
                className="w-full h-12 pl-11 pr-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
              />
            </div>
          </div>

          <div className="col-span-2 sm:col-span-1">
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Company</label>
            <div className="relative">
              <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                placeholder="Acme Corp"
                className="w-full h-12 pl-11 pr-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-green/50 focus:ring-2 focus:ring-wa-green/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
              />
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
            disabled={isPending || !formData.name || !formData.phone}
            className="h-11 px-6 bg-wa-green hover:bg-wa-green-dark text-slate-950 font-bold rounded-xl flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(37,211,102,0.15)] hover:shadow-[0_0_30px_rgba(37,211,102,0.25)]"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Add Client"}
          </button>
        </div>
      </form>
    </Modal>
  )
}
