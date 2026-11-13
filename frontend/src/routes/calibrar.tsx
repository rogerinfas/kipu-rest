import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useCallback, useEffect, useRef, useState } from 'react'
import type { Zone } from '../lib/types'

export const Route = createFileRoute('/calibrar')({ component: Calibrar })

type Pt = [number, number]
const pad = (n: number) => String(n).padStart(2, '0')

function nextName(zones: Zone[]): { id: string; name: string } {
  let n = 1
  const ids = new Set(zones.map((z) => z.id))
  while (ids.has(`m${pad(n)}`)) n++
  return { id: `m${pad(n)}`, name: `Mesa ${pad(n)}` }
}

function Calibrar() {
  const navigate = useNavigate()
  const svgRef = useRef<SVGSVGElement>(null)
  const [zones, setZones] = useState<Zone[]>([])
  const [draft, setDraft] = useState<Pt[]>([])
  const [frameKey, setFrameKey] = useState(() => Date.now())
  const [msg, setMsg] = useState('')

  const load = useCallback(async () => {
    const r = await fetch('/api/zones')
    if (r.ok) setZones(await r.json())
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const closeDraft = useCallback(() => {
    if (draft.length < 3) {
      setMsg('Una mesa necesita al menos 3 puntos')
      return
    }
    const def = nextName(zones)
    const name = window.prompt('Nombre de la mesa', def.name)?.trim() || def.name
    setZones([...zones, { id: def.id, name, polygon: draft }])
    setDraft([])
    setMsg('')
  }, [draft, zones])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter') closeDraft()
      if (e.key === 'Backspace') setDraft((d) => d.slice(0, -1))
      if (e.key === 'Escape') {
        if (draft.length) setDraft([])
        else navigate({ to: '/' })
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [closeDraft, draft.length, navigate])

  const onClick = (e: React.MouseEvent<SVGSVGElement>) => {
    const r = svgRef.current!.getBoundingClientRect()
    const x = (e.clientX - r.left) / r.width
    const y = (e.clientY - r.top) / r.height
    setDraft((d) => [...d, [+x.toFixed(4), +y.toFixed(4)]])
  }

  const save = async () => {
    const r = await fetch('/api/zones', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(zones),
    })
    setMsg(r.ok ? `Guardadas ${zones.length} mesas` : `Error al guardar (${r.status})`)
  }

  const pts = (p: Pt[]) => p.map(([x, y]) => `${x * 100},${y * 100}`).join(' ')

  return (
    <div className="flex h-full gap-4 p-4">
      <div className="relative aspect-video h-full max-w-[calc(100%-20rem)] flex-1 self-start">
        <img
          src={`/api/frame.jpg?t=${frameKey}`}
          alt="Frame del video"
          className="h-full w-full rounded-lg object-contain"
        />
        <svg
          ref={svgRef}
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="absolute inset-0 h-full w-full cursor-crosshair"
          onClick={onClick}
        >
          {zones.map((z) => (
            <g key={z.id}>
              <polygon points={pts(z.polygon)} fill="#3fb95033" stroke="#3fb950" strokeWidth={0.25} />
              <text x={z.polygon[0][0] * 100} y={z.polygon[0][1] * 100 - 0.8} fontSize={2.2} fill="#3fb950">
                {z.name}
              </text>
            </g>
          ))}
          {draft.length > 0 && (
            <polyline points={pts(draft)} fill="#f0b42933" stroke="#f0b429" strokeWidth={0.3} />
          )}
          {draft.map(([x, y], i) => (
            <circle key={i} cx={x * 100} cy={y * 100} r={0.5} fill="#f0b429" />
          ))}
        </svg>
      </div>
      <aside className="flex w-80 shrink-0 flex-col gap-3">
        <h1 className="text-xl font-bold text-[#f0b429]">Calibrar mesas</h1>
        <ol className="list-decimal space-y-1 pl-5 text-sm text-[#9da7b3]">
          <li>Haz clic alrededor de cada mesa, <b>incluyendo sus sillas</b>.</li>
          <li><kbd>Enter</kbd> cierra la mesa · <kbd>Retroceso</kbd> borra el último punto.</li>
          <li><kbd>Esc</kbd> cancela el dibujo o vuelve a la demo.</li>
        </ol>
        <ul className="flex-1 space-y-1 overflow-auto">
          {zones.map((z) => (
            <li key={z.id} className="flex items-center justify-between rounded bg-[#161b22] px-3 py-1">
              <span>{z.name}</span>
              <button
                className="text-sm text-[#ff5c5c] hover:underline"
                onClick={() => setZones(zones.filter((x) => x.id !== z.id))}
              >
                borrar
              </button>
            </li>
          ))}
        </ul>
        {msg && <p className="text-sm text-[#f0b429]">{msg}</p>}
        <div className="grid grid-cols-2 gap-2">
          <button className="rounded bg-[#3fb950] px-3 py-2 font-semibold text-black" onClick={save}>
            Guardar
          </button>
          <button className="rounded bg-[#30363d] px-3 py-2" onClick={load}>
            Cargar
          </button>
          <button className="rounded bg-[#30363d] px-3 py-2" onClick={() => setFrameKey(Date.now())}>
            Otro frame
          </button>
          <button className="rounded bg-[#30363d] px-3 py-2" onClick={() => navigate({ to: '/' })}>
            Volver
          </button>
        </div>
      </aside>
    </div>
  )
}
