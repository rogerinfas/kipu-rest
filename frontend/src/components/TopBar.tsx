import { fmtClock } from '../lib/format'
import type { SalonState } from '../lib/types'

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline gap-2">
      <span className="text-sm uppercase tracking-wider text-[#9da7b3]">{label}</span>
      <span className="text-2xl font-bold tabular-nums">{value}</span>
    </div>
  )
}

export function TopBar({ state, connected }: { state: SalonState | null; connected: boolean }) {
  return (
    <header className="flex items-center justify-between px-6 py-3">
      <div className="flex items-baseline gap-3">
        <span className="text-2xl font-extrabold text-[#f0b429]">KipuRest</span>
        <span className="text-xl font-semibold">Live Vision</span>
        <span className="text-[#9da7b3]">· Salón principal</span>
      </div>
      <div className="flex items-center gap-8">
        <Kpi label="Ocupación" value={state ? `${state.occupancy_pct}%` : '--'} />
        <Kpi label="Prom. mesa" value={state && state.rotations ? fmtClock(state.avg_occupancy_s) : '--:--'} />
        <Kpi label="Rotaciones" value={state ? String(state.rotations) : '--'} />
        {connected ? (
          <span className="flex items-center gap-2 font-bold text-[#ff5c5c]">
            <span className="h-3 w-3 animate-pulse rounded-full bg-[#ff5c5c]" />
            EN VIVO
          </span>
        ) : (
          <span className="font-semibold text-[#f0b429]">Reconectando…</span>
        )}
      </div>
    </header>
  )
}
