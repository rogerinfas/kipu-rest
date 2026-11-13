import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { AiHint } from '../components/AiHint'
import { TableStrip } from '../components/TableStrip'
import { TopBar } from '../components/TopBar'
import { VideoStage } from '../components/VideoStage'
import { useSalonState } from '../hooks/useSalonState'

export const Route = createFileRoute('/')({ component: Demo })

function Demo() {
  const { state, connected } = useSalonState()
  const navigate = useNavigate()

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'f' || e.key === 'F') {
        if (document.fullscreenElement) document.exitFullscreen()
        else document.documentElement.requestFullscreen()
      }
      if (e.key === 'c' || e.key === 'C') navigate({ to: '/calibrar' })
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [navigate])

  return (
    <div className="flex h-full flex-col">
      <TopBar state={state} connected={connected} />
      <main className="min-h-0 flex-1 px-6">
        <VideoStage>
          {state && (
            <div className="absolute right-4 bottom-4">
              <AiHint hint={state.hint} />
            </div>
          )}
        </VideoStage>
      </main>
      <footer className="px-6 py-4">
        <TableStrip tables={state?.tables ?? []} />
      </footer>
    </div>
  )
}
