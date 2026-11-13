import { useEffect, useState } from 'react'
import type { SalonState } from '../lib/types'

const RECONNECT_MS = 1000

export function useSalonState(): { state: SalonState | null; connected: boolean } {
  const [state, setState] = useState<SalonState | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let ws: WebSocket | null = null
    let timer: ReturnType<typeof setTimeout> | undefined
    let closed = false

    const connect = () => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws'
      ws = new WebSocket(`${proto}://${location.host}/ws/state`)
      ws.onopen = () => setConnected(true)
      ws.onmessage = (e) => setState(JSON.parse(e.data) as SalonState)
      ws.onclose = () => {
        setConnected(false)
        if (!closed) timer = setTimeout(connect, RECONNECT_MS)
      }
      ws.onerror = () => ws?.close()
    }
    connect()

    return () => {
      closed = true
      clearTimeout(timer)
      ws?.close()
    }
  }, [])

  return { state, connected }
}
