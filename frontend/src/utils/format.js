// Formatação de valores para exibição (pt-BR).

/** Número com casas decimais fixas; '—' para valor ausente. */
export function fmt(v, casas = 1) {
  return typeof v === 'number' && !Number.isNaN(v) ? v.toFixed(casas) : '—'
}

/** Percentual de v em relação a max, limitado entre 0 e 100. */
export function pct(v, max) {
  if (typeof v !== 'number' || Number.isNaN(v)) return 0
  return Math.max(0, Math.min(100, (v / max) * 100))
}

/**
 * Data da API ("2026-06-12" ou ISO com hora) → "12/06/2026".
 * Datas sem hora são tratadas como dia local, para não "voltar um dia" pelo fuso.
 */
export function formatarData(valor) {
  if (!valor) return '—'
  const soData = /^(\d{4})-(\d{2})-(\d{2})$/.exec(valor)
  const d = soData ? new Date(+soData[1], +soData[2] - 1, +soData[3]) : new Date(valor)
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString('pt-BR')
}

/** Timestamp (ms) → "14:30:05". */
export function formatarHora(ms) {
  return new Date(ms).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

/** "Maceió — AL", ou só o que existir. */
export function localidade(municipio, estado) {
  return [municipio, estado].filter(Boolean).join(' — ')
}