export function AiHint({ hint }: { hint: string }) {
  const alert = hint.startsWith('Priorizar')
  return (
    <div
      className={`max-w-md rounded-lg border px-4 py-2 backdrop-blur-sm ${
        alert ? 'border-[#D2452B] bg-[#3D1A12]/85 text-[#F2B8A8]' : 'border-[#6B8F4E] bg-[#1F2A17]/85 text-[#BFD4A4]'
      }`}
    >
      <div className="text-xs font-bold uppercase tracking-widest opacity-80">Sugerencia IA</div>
      <div className="text-lg font-semibold">{hint}</div>
    </div>
  )
}
