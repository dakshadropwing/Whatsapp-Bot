"use client"

import { useEffect } from "react"
import { useAuthStore } from "@/store/auth"
import { usePathname } from "next/navigation"

export function AuthWrapper({ children }: { children: React.ReactNode }) {
  const checkAuth = useAuthStore((state) => state.checkAuth)
  const pathname = usePathname()

  useEffect(() => {
    // Only check auth if we're not on the login page
    if (pathname !== "/login") {
      checkAuth()
    }
  }, [checkAuth, pathname])

  return <>{children}</>
}
