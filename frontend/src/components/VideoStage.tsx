import type { ReactNode } from 'react'

export function VideoStage({ children }: { children?: ReactNode }) {
  return (
    <div className="relative mx-auto aspect-video h-full max-w-full overflow-hidden rounded-xl bg-black">
      <img src="/video" alt="Cámara del salón" className="h-full w-full object-contain" />
      <span className="absolute bottom-3 left-4 rounded bg-black/60 px-2 py-1 text-sm text-[#9da7b3]">
        CAM-01 · YOLO en vivo · sin rostros
      </span>
      {children}
    </div>
  )
}
