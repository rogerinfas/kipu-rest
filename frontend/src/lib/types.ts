export type Status = 'LIBRE' | 'ATENCION' | 'OPTIMO' | 'ALERTA'

export interface TableState {
  id: string
  name: string
  status: Status
  people: number
  elapsed_s: number
  stage: string | null
  amount: number
  stage_note: string
}

export interface SalonState {
  tables: TableState[]
  occupancy_pct: number
  avg_occupancy_s: number
  rotations: number
  hint: string
  fps: number
  device: string
}

export interface Zone {
  id: string
  name: string
  polygon: [number, number][]
}

export const STATUS_COLOR: Record<Status, string> = {
  LIBRE: '#8A7B70',
  ATENCION: '#E0A43A',
  OPTIMO: '#6B8F4E',
  ALERTA: '#D2452B',
}

export const STATUS_LABEL: Record<Status, string> = {
  LIBRE: 'Libre',
  ATENCION: 'Atención',
  OPTIMO: 'Óptimo',
  ALERTA: 'Alerta',
}
