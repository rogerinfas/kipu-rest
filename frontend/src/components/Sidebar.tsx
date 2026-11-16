import { Link } from '@tanstack/react-router'

type Item = { label: string; icon: string; to?: '/' | '/calibrar'; badge?: string }

// Iconos SVG inline (trazos de 24x24) para no depender de librerías.
const ICON: Record<string, string> = {
  home: 'M3 11l9-8 9 8v9a1 1 0 01-1 1h-5v-6H9v6H4a1 1 0 01-1-1z',
  eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zm10 3a3 3 0 100-6 3 3 0 000 6z',
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
  receipt: 'M6 2h12v20l-3-2-3 2-3-2-3 2zM9 7h6M9 11h6M9 15h4',
  box: 'M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10',
  cash: 'M2 6h20v12H2zM12 15a3 3 0 100-6 3 3 0 000 6z',
  chart: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  users: 'M16 21v-2a4 4 0 00-8 0v2M12 11a4 4 0 100-8 4 4 0 000 8z',
  gear: 'M12 15a3 3 0 100-6 3 3 0 000 6zM19 12l2-1-1-3-2 .5-1.5-1.5L17 5l-3-1-1 2h-2L10 4 7 5l.5 2L6 8.5 4 8l-1 3 2 1v0l-2 1 1 3 2-.5L7.5 17 7 19l3 1 1-2h2l1 2 3-1-.5-2 1.5-1.5 2 .5 1-3z',
  cam: 'M3 7h4l2-3h6l2 3h4v13H3zM12 17a4 4 0 100-8 4 4 0 000 8z',
}

const SECTIONS: { title: string; items: Item[] }[] = [
  { title: 'General', items: [{ label: 'Inicio', icon: 'home' }] },
  {
    title: 'Operación',
    items: [
      { label: 'Live Vision', icon: 'eye', to: '/', badge: 'IA' },
      { label: 'Mapa de mesas', icon: 'grid' },
      { label: 'Comandas', icon: 'receipt' },
      { label: 'Inventario', icon: 'box' },
      { label: 'Caja', icon: 'cash' },
    ],
  },
  {
    title: 'Gestión',
    items: [
      { label: 'Reportes', icon: 'chart' },
      { label: 'Personal', icon: 'users' },
      { label: 'Cámaras', icon: 'cam', to: '/calibrar' },
      { label: 'Configuración', icon: 'gear' },
    ],
  },
]

function Icon({ name }: { name: string }) {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5 shrink-0" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d={ICON[name]} />
    </svg>
  )
}

export function Sidebar() {
  return (
    <aside className="flex w-60 shrink-0 flex-col bg-[#1E140F] px-3 py-5">
      <div className="mb-8 flex items-center gap-3 px-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#C0573E] text-lg font-black text-[#F5EBDD]">K</div>
        <div>
          <div className="text-lg leading-none font-extrabold text-[#F5EBDD]">KipuRest</div>
          <div className="text-xs text-[#C4B2A0]">Gestión inteligente</div>
        </div>
      </div>
      <nav className="flex-1 space-y-6">
        {SECTIONS.map((s) => (
          <div key={s.title}>
            <div className="mb-2 px-3 text-[0.65rem] font-bold tracking-widest text-[#8A7B70] uppercase">{s.title}</div>
            <ul className="space-y-1">
              {s.items.map((it) => {
                const base = 'flex items-center gap-3 rounded-lg px-3 py-2 text-sm'
                const inner = (
                  <>
                    <Icon name={it.icon} />
                    <span className="flex-1">{it.label}</span>
                    {it.badge && <span className="rounded bg-[#E0A43A] px-1.5 text-[0.6rem] font-bold text-[#2B1D16]">{it.badge}</span>}
                  </>
                )
                return (
                  <li key={it.label}>
                    {it.to ? (
                      <Link
                        to={it.to}
                        className={`${base} text-[#C4B2A0] hover:bg-[#3A2A21]`}
                        activeOptions={{ exact: true }}
                        activeProps={{ className: `${base} bg-[#C0573E] font-semibold text-[#F5EBDD]` }}
                      >
                        {inner}
                      </Link>
                    ) : (
                      <span className={`${base} cursor-default text-[#C4B2A0]/70 hover:bg-[#3A2A21]/60`}>{inner}</span>
                    )}
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>
      <div className="mt-4 flex items-center gap-3 rounded-lg bg-[#3A2A21] px-3 py-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#E0A43A] text-sm font-bold text-[#2B1D16]">AD</div>
        <div className="text-xs">
          <div className="font-semibold text-[#F5EBDD]">Administrador</div>
          <div className="text-[#C4B2A0]">Sede Miraflores</div>
        </div>
      </div>
    </aside>
  )
}
