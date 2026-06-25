import { useState } from "react"
import { Modal } from "@/components/Modal"
import { api } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { Loader2 } from "lucide-react"

interface CreatePromptModalProps {
  isOpen: boolean
  onClose: () => void
}

export function CreatePromptModal({ isOpen, onClose }: CreatePromptModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: "",
    system_prompt: "",
    agent_id: "", 
  })

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await api.post("/prompts", data)
      return res.data
    },
    onSuccess: () => {
      toast.success("Prompt created successfully")
      queryClient.invalidateQueries({ queryKey: ["prompts"] })
      onClose()
      setFormData({ name: "", system_prompt: "", agent_id: "" })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error || "Failed to create prompt")
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
      title="Create Prompt Template"
      description="Add a new system prompt or message template."
      className="max-w-xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-6">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Template Name</label>
            <input
              required
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. Sales Qualification Prompt"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Agent Binding (Optional)</label>
            <input
              type="text"
              value={formData.agent_id}
              onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })}
              placeholder="Agent ID to bind this prompt to"
              className="w-full h-12 px-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all placeholder:text-slate-500 hover:bg-foreground/[0.05]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Prompt Content</label>
            <textarea
              required
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              placeholder="Enter your prompt here. You can use {{variables}}..."
              className="w-full h-40 p-4 rounded-xl bg-foreground/[0.03] border border-foreground/[0.08] text-sm text-foreground font-mono focus:outline-none focus:border-wa-purple/50 focus:ring-2 focus:ring-wa-purple/20 transition-all resize-none placeholder:text-slate-500 hover:bg-foreground/[0.05]"
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
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save Template"}
          </button>
        </div>
      </form>
    </Modal>
  )
}
