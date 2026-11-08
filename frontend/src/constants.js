// Regras compartilhadas entre as telas.

// Limite superior da faixa "ok" de cada sensor.
// Mesmos valores de backend/app/services/iot.py — mantenha os dois iguais.
export const LIMITES = {
  temp: 36,        // °C
  umidade: 70,     // %
  som: 300,        // Hz (agitação)
  somCritico: 450, // Hz
}

// Valor que corresponde a 100% nas barras de cada sensor
export const ESCALA = { temp: 45, umidade: 100, peso: 70, som: 600 }

export const STATUS_COLMEIA = {
  normal: 'Normal',
  alerta: '⚠ Alerta',
  critico: '🔴 Crítico',
}

export const STATUS_LOTE = {
  aprovado: '✓ Aprovado',
  em_analise: '⏳ Em análise',
  reprovado: '✗ Reprovado',
}