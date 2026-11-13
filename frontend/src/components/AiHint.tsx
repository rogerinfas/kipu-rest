export function AiHint({ hint }: { hint: string }) {
  const alert = hint.startsWith('Priorizar')
  return (
    <div
      className={`max-w-md rounded-lg border px-4 py-2 backdrop-blur-sm ${
        alert ? 'border-[#ff5c5c] bg-[#2a1215]/85 text-[#ffb4b4]' : 'border-[#3fb950] bg-[#122117]/85 text-[#a6e3a1]'
      }`}
    >
      <div className="text-xs font-bold uppercase tracking-widest opacity-80">Sugerencia IA</div>
      <div className="text-lg font-semibold">{hint}</div>
    </div>
  )
}
