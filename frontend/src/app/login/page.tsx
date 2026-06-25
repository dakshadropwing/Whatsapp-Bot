"use client"

import { useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { api } from "@/lib/api"
import { Zap, Lock, Mail, ArrowRight, Loader2, Bot } from "lucide-react"
import toast, { Toaster } from "react-hot-toast"
import { cn } from "@/lib/utils"

function LoginContent() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const setAuth = useAuthStore((state) => state.setAuth)
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const { data } = await api.post("/auth/login", { email, password })
      setAuth(data.user, data.access_token, data.refresh_token)
      
      toast.success("Welcome back!")
      
      const callbackUrl = searchParams.get("callbackUrl")
      if (callbackUrl) {
        router.push(callbackUrl)
      } else {
        router.push("/")
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Failed to login. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-[420px]">
      <div className="text-center mb-10 opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-wa-green to-wa-teal flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(37,211,102,0.3)]">
          <Bot className="w-8 h-8 text-slate-950" />
        </div>
        <h1 className="text-3xl font-bold text-white tracking-tight font-outfit mb-2">Persynix Bot</h1>
        <p className="text-slate-500">Enterprise AI Operations Platform</p>
      </div>

      <form onSubmit={handleLogin} className="glass-card p-8 space-y-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-2 uppercase tracking-wider">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@persynix.io"
                className="w-full h-12 pl-11 pr-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-wa-green/40 focus:bg-white/[0.05] transition-all"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider">Password</label>
              <a href="#" className="text-xs text-wa-green hover:text-wa-green-light transition-colors">Forgot?</a>
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full h-12 pl-11 pr-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-wa-green/40 focus:bg-white/[0.05] transition-all"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full h-12 bg-wa-green hover:bg-wa-green-dark disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-semibold rounded-xl flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(37,211,102,0.15)] hover:shadow-[0_0_30px_rgba(37,211,102,0.25)]"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Sign In to Platform <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      <p className="text-center text-xs text-slate-600 mt-8 opacity-0 animate-fade-in-up" style={{ animationDelay: "300ms" }}>
        Protected by neural encryption. Authorized personnel only.
      </p>
    </div>
  )
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-4 relative overflow-hidden font-sans">
      <Toaster position="top-right" toastOptions={{ className: "!bg-slate-900 !text-white !border !border-white/[0.08]" }} />
      
      {/* Ambient background glow */}
      <div className="absolute top-0 right-0 w-full h-full overflow-hidden pointer-events-none -z-10">
        <div className="ambient-light-1 absolute top-[-15%] right-[-5%] w-[600px] h-[600px] rounded-full bg-wa-green/[0.05] blur-[150px]" />
        <div className="ambient-light-2 absolute bottom-[-15%] left-[-5%] w-[500px] h-[500px] rounded-full bg-wa-purple/[0.05] blur-[150px]" />
        <div className="ambient-light-3 absolute top-[40%] left-[30%] w-[400px] h-[400px] rounded-full bg-wa-blue/[0.03] blur-[120px]" />
      </div>

      <Suspense fallback={<Loader2 className="w-8 h-8 animate-spin text-wa-green" />}>
        <LoginContent />
      </Suspense>
    </div>
  )
}
