import { useEffect, useState, type ReactNode } from 'react'

const RETRY_MS = 1000

/** MJPEG del backend. Se recarga si el stream falla o cuando el WebSocket vuelve a conectar. */
export function VideoStage({ connected, children }: { connected: boolean; children?: ReactNode }) {
  const [key, setKey] = useState(() => Date.now())
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (connected) setKey(Date.now())
  }, [connected])

  useEffect(() => {
    if (!failed) return
    const t = setTimeout(() => {
      setFailed(false)
      setKey(Date.now())
    }, RETRY_MS)
    return () => clearTimeout(t)
  }, [failed])

  return (
    <div className="relative mx-auto aspect-video h-full max-w-full overflow-hidden rounded-xl bg-black">
      <img
        key={key}
        src={`/video?t=${key}`}
        alt="Cámara del salón"
        className="h-full w-full object-contain"
        onError={() => setFailed(true)}
      />
      {(failed || !connected) && (
        <div className="absolute inset-0 flex items-center justify-center text-xl text-[#C4B2A0]">
          Conectando con la cámara…
        </div>
      )}
      <span className="absolute bottom-3 left-4 rounded bg-black/60 px-2 py-1 text-sm text-[#C4B2A0]">
        CAM-01 · YOLO en vivo · sin rostros
      </span>
      {children}
    </div>
  )
}
