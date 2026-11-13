import { fmtClock } from '../lib/format'
import { STATUS_COLOR, STATUS_LABEL, type TableState } from '../lib/types'

function TableCard({ t }: { t: TableState }) {
  const color = STATUS_COLOR[t.status]
  const free = t.status === 'LIBRE'
  return (
    <div
      className={`rounded-lg border-t-4 bg-[#161b22] px-3 py-2 ${t.status === 'ALERTA' ? 'kipu-pulse' : ''}`}
      style={{ borderColor: color, borderTopStyle: free ? 'dashed' : 'solid' }}
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold">{t.name}</span>
        <span className="text-xs font-bold uppercase" style={{ color }}>
          {STATUS_LABEL[t.status]}
        </span>
      </div>
      <div className="text-3xl font-bold tabular-nums" style={{ color: free ? '#6e7681' : color }}>
        {fmtClock(t.elapsed_s)}
      </div>
      <div className="truncate text-sm text-[#9da7b3]">{t.stage_note}</div>
    </div>
  )
}

export function TableStrip({ tables }: { tables: TableState[] }) {
  if (!tables.length) {
    return (
      <div className="rounded-lg bg-[#161b22] p-4 text-center text-[#9da7b3]">
        No hay mesas configuradas. Pulsa <kbd className="rounded bg-[#30363d] px-2">C</kbd> para calibrar.
      </div>
    )
  }
  return (
    <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${Math.min(tables.length, 8)}, minmax(0, 1fr))` }}>
      {tables.map((t) => (
        <TableCard key={t.id} t={t} />
      ))}
    </div>
  )
}
