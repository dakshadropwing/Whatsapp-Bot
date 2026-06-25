import { useEffect, useRef, useCallback } from 'react'
import { useAuthStore } from '@store/auth'

export function useWebSocket(onMessage?: (data: unknown) => void) {
  const wsRef = useRef<WebSocket | null>(null)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const accessToken = useAuthStore((s) => s.accessToken)

  const connect = useCallback(() => {
    if (!isAuthenticated || !accessToken) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/socket.io/?token=${accessToken}`)

    ws.onopen = () => console.log('[WS] Connected')
    ws.onclose = () => console.log('[WS] Disconnected')
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch { /* ignore */ }
    }

    wsRef.current = ws
  }, [isAuthenticated, accessToken, onMessage])

  useEffect(() => {
    connect()
    return () => { wsRef.current?.close() }
  }, [connect])

  const send = useCallback((data: unknown) => {
    wsRef.current?.send(JSON.stringify(data))
  }, [])

  return { send, ws: wsRef.current }
}
