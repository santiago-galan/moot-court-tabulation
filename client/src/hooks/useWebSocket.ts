import { useEffect, useRef, useCallback } from 'react'

type Handler = (event: string, data: Record<string, unknown>) => void

export function useWebSocket(onMessage: Handler) {
  const wsRef = useRef<WebSocket | null>(null)
  const handlerRef = useRef(onMessage)
  handlerRef.current = onMessage

  useEffect(() => {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${location.host}/ws`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data)
        handlerRef.current(msg.event, msg.data)
      } catch { /* ignore malformed */ }
    }
    ws.onclose = () => {
      setTimeout(() => {
        if (wsRef.current === ws) wsRef.current = null
      }, 2000)
    }

    return () => { ws.close() }
  }, [])

  const send = useCallback((data: unknown) => {
    wsRef.current?.send(JSON.stringify(data))
  }, [])

  return { send }
}
