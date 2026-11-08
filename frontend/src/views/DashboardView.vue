<template>
  <div class="page">
    <!-- Erro no carregamento inicial -->
    <div v-if="erro && !dash" class="erro-box">
      <span>⚠ Não foi possível carregar os dados IoT.</span>
      <button class="btn-retry" @click="carregar">Tentar novamente</button>
    </div>

    <div class="stats-grid" v-if="dash">
      <div class="stat" style="border-left-color:var(--gd)">
        <div class="stat-label">Colmeias ativas</div>
        <div class="stat-val" style="color:var(--br)">{{ dash.total_colmeias }}</div>
        <div class="stat-sub">monitoradas por IoT</div>
      </div>
      <div class="stat" :style="`border-left-color:${dash.colmeias_alerta > 0 ? 'var(--rd)' : 'var(--gn)'}`">
        <div class="stat-label">Alertas ativos</div>
        <div class="stat-val" :style="`color:${dash.colmeias_alerta > 0 ? 'var(--rd)' : 'var(--gn)'}`">{{ dash.colmeias_alerta }}</div>
        <div class="stat-sub">{{ dash.colmeias_alerta === 0 ? 'todas normais ✓' : 'requerem atenção' }}</div>
      </div>
      <div class="stat" style="border-left-color:var(--gn)">
        <div class="stat-label">Produção estimada</div>
        <div class="stat-val" style="color:var(--gn)">{{ fmt(dash.producao_total_estimada, 1) }} kg</div>
        <div class="stat-sub">ciclo atual</div>
      </div>
      <div class="stat" :style="`border-left-color:${dadosAntigos ? 'var(--rd)' : 'var(--br3)'}`">
        <div class="stat-label">Última leitura IoT</div>
        <div class="stat-val" :style="`color:${dadosAntigos ? 'var(--rd)' : 'var(--br3)'};font-size:18px`">{{ ultimaLeitura }}</div>
        <div class="stat-sub">{{ dadosAntigos ? '⚠ sensores sem leitura recente' : `atualiza a cada ${DASH_MS / 1000}s` }}</div>
      </div>
    </div>

    <div class="section-header" v-if="dash">
      <div class="section-title">🐝 Monitoramento em tempo real<template v-if="local"> · {{ local }}</template></div>
      <div class="live-pill" :class="{ 'live-pill-off': dadosAntigos || erro }">
        <span class="live-dot"></span>
        {{ erro ? 'falha na conexão' : `IoT ativo · ciclo ${ciclo}` }}
      </div>
    </div>

    <div class="hive-grid" v-if="dash">
      <div v-for="c in dash.colmeias" :key="c.id"
        class="hive-card"
        role="button"
        tabindex="0"
        :aria-label="`Abrir detalhes da colmeia ${c.codigo}`"
        :class="{ selected: sel === c.id, alerta: c.status === 'alerta', critico: c.status === 'critico' }"
        @click="abrirColmeia(c)"
        @keydown.enter.prevent="abrirColmeia(c)"
        @keydown.space.prevent="abrirColmeia(c)">
        <div class="hive-top">
          <span class="hive-id">🐝 {{ c.codigo }}</span>
          <span class="badge" :class="`badge-${c.status}`">{{ STATUS_COLMEIA[c.status] ?? c.status }}</span>
        </div>
        <div class="hive-florada">🌸 {{ c.florada }}</div>
        <template v-if="c.ultima_leitura">
          <div class="gauge" v-for="g in gauges(c)" :key="g.label">
            <div class="gauge-row"><span>{{ g.label }}</span><span class="gauge-val" :style="`color:${g.color}`">{{ g.val }}</span></div>
            <div class="gauge-track"><div class="gauge-fill" :style="`width:${g.pct}%;background:${g.color}`"></div></div>
          </div>
          <div class="hive-prod">🍯 Produção estimada: <strong>{{ fmt(c.producao_estimada, 1) }} kg</strong></div>
        </template>
        <div v-else class="sem-dados">Aguardando leitura IoT...</div>
        <div class="hive-click-hint">▼ detalhes em tempo real</div>
      </div>
    </div>

    <div v-if="!dash && !erro" class="loading"><div class="loading-spinner"></div>Carregando dados IoT...</div>

    <Teleport to="body">
      <div v-if="modalColmeia" class="modal-overlay" @click.self="fecharModal">
        <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-colmeia-titulo">
          <div class="modal-header">
            <div>
              <div class="modal-title" id="modal-colmeia-titulo">🐝 {{ modalColmeia.codigo }}</div>
              <div class="modal-sub">{{ modalColmeia.florada }} · {{ STATUS_COLMEIA[modalColmeia.status] ?? modalColmeia.status }}</div>
            </div>
            <div class="modal-header-right">
              <div class="live-pill-sm"><span class="live-dot"></span>ao vivo · {{ liveSegundos }}s</div>
              <button ref="btnFechar" class="modal-close" aria-label="Fechar" @click="fecharModal">✕</button>
            </div>
          </div>

          <!-- Sensores em tempo real -->
          <div class="sensor-grid">
            <div v-for="s in sensores" :key="s.key"
              class="sensor-box"
              :class="{ 'sensor-warn': s.warn, flash: s.flash }">
              <div class="sensor-ico">{{ s.ico }}</div>
              <div class="sensor-lbl">{{ s.lbl }}</div>
              <div class="sensor-num" :style="s.warn ? 'color:var(--rd)' : ''">{{ s.num }}</div>
              <div class="sensor-bar">
                <div class="sensor-bar-fill" :style="`width:${s.pct}%;background:${s.cor}`"></div>
              </div>
              <div class="sensor-status">{{ s.status }}</div>
            </div>
          </div>

          <!-- Gráfico acumulando em tempo real -->
          <div class="chart-section">
            <div class="chart-header">
              <div class="chart-title">📈 Temperatura — acumulando em tempo real</div>
              <div class="chart-meta">{{ temps.length }} pontos · atualiza a cada {{ LIVE_MS / 1000 }}s</div>
            </div>
            <div v-if="temps.length > 1" class="chart-wrap">
              <svg :viewBox="`0 0 ${CHART.w} ${CHART.h}`" class="chart-svg" role="img" aria-label="Gráfico de temperatura">
                <!-- Grade + rótulos Y (mesma escala dos pontos) -->
                <g v-for="(l, i) in yLabels" :key="i">
                  <line :x1="CHART.left" :y1="l.y" :x2="CHART.w - CHART.right" :y2="l.y" class="grid-line"/>
                  <text :x="CHART.left - 5" :y="l.y + 4" class="y-label" text-anchor="end">{{ l.v }}°</text>
                </g>
                <!-- Área -->
                <polygon :points="chartArea" class="chart-area"/>
                <!-- Linha -->
                <polyline :points="chartPoints" class="chart-line"/>
                <!-- Pontos anteriores -->
                <circle v-for="(p, i) in chartDots.slice(0, -1)" :key="i"
                  :cx="p.x" :cy="p.y" r="2.5"
                  class="chart-dot" :class="{ hot: p.hot }"/>
                <!-- Último ponto pulsando -->
                <circle v-if="ultimoDot"
                  :cx="ultimoDot.x" :cy="ultimoDot.y"
                  r="5" class="chart-dot chart-dot-last" :class="{ hot: ultimoDot.hot }">
                  <animate attributeName="r" values="5;8;5" dur="1.5s" repeatCount="indefinite"/>
                  <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/>
                </circle>
              </svg>
              <div class="chart-info">
                Mín: <strong>{{ tempMin }}°C</strong> ·
                Máx: <strong>{{ tempMax }}°C</strong> ·
                Média: <strong>{{ tempMedia }}°C</strong> ·
                Agora: <strong :style="tempAlta ? 'color:var(--rd)' : ''">{{ fmt(liveData.temperatura, 1) }}°C</strong>
              </div>
            </div>
            <div v-else class="chart-empty">
              <div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div>
              Acumulando leituras...
            </div>
          </div>

          <!-- Diagnóstico -->
          <div v-if="diagnostico" class="diagnostico" :class="`diag-${modalColmeia.status}`">
            <div class="diag-title">⚠ Diagnóstico automático MelT3ch</div>
            <div class="diag-body">
              {{ diagnostico.texto }} <strong>{{ diagnostico.acao }}</strong>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { getDashboard, getHistorico } from '../api'
import { ESCALA, LIMITES, STATUS_COLMEIA } from '../constants'
import { fmt, formatarHora, localidade, pct } from '../utils/format'

// ───────── Configuração ─────────
const DASH_MS = 30000          // atualização da página
const LIVE_MS = 5000           // atualização do modal
const MAX_LIVE_POINTS = 60
const DADOS_ANTIGOS_MS = 2 * DASH_MS + 30000   // sem leitura nova há mais que isso → aviso

const CHART = { w: 560, h: 120, left: 40, right: 10, pad: 14 }

const COR = {
  rd: 'var(--rd)',
  gd: 'var(--gd)',
  gn: 'var(--gn)',
  br3: 'var(--br3)',
  am: 'var(--am)',
}

const LEITURA_VAZIA = () => ({ temperatura: null, umidade: null, peso: null, som: null })

// ───────── Estado ─────────
const dash = ref(null)
const erro = ref(null)
const sel = ref(null)
const liveHistorico = ref([])
const liveData = ref(LEITURA_VAZIA())
const ciclo = ref(0)
const ultimaLeitura = ref('—')
const dadosAntigos = ref(false)
const liveSegundos = ref(0)
const tempFlash = ref(false)
const btnFechar = ref(null)

let timerDash = null
let timerLive = null
let timerSeg = null
let timerFlash = null
let carregando = false
let desmontado = false
let sessaoModal = 0   // invalida callbacks assíncronos de um modal já fechado

// O modal sempre reflete o dado mais recente do dashboard (antes era um "retrato" congelado)
const modalColmeia = computed(() =>
  sel.value == null ? null : dash.value?.colmeias?.find(c => c.id === sel.value) ?? null
)

const local = computed(() => localidade(dash.value?.produtor_municipio, dash.value?.produtor_estado))

// ───────── Helpers ─────────
function tsLeitura(l) {
  if (!l?.timestamp) return null
  const t = new Date(l.timestamp).getTime()
  return Number.isNaN(t) ? null : t
}
function mesmaLeitura(a, b) {
  if (!a || !b) return false
  if (a.id != null && b.id != null) return a.id === b.id
  const ta = tsLeitura(a), tb = tsLeitura(b)
  if (ta != null && tb != null) return ta === tb
  // Sem id nem timestamp: compara os valores
  return a.temperatura === b.temperatura && a.umidade === b.umidade &&
         a.peso === b.peso && a.som === b.som
}

// ───────── Dashboard (polling de 30s) ─────────
function aplicarDashboard(data) {
  dash.value = data
  if (sel.value != null) {
    const c = data.colmeias?.find(x => x.id === sel.value)
    if (c?.ultima_leitura) atualizarLive(c.ultima_leitura)
  }
}

async function carregar() {
  if (carregando || desmontado) return
  carregando = true
  clearTimeout(timerDash)
  try {
    if (!document.hidden || !dash.value) {
      const { data } = await getDashboard()
      if (desmontado) return
      aplicarDashboard(data)
      erro.value = null
      ciclo.value++

      // Hora da leitura mais recente dos sensores (não a hora da requisição)
      const tss = (data.colmeias ?? []).map(c => tsLeitura(c.ultima_leitura)).filter(t => t != null)
      if (tss.length) {
        const maisRecente = Math.max(...tss)
        ultimaLeitura.value = formatarHora(maisRecente)
        dadosAntigos.value = Date.now() - maisRecente > DADOS_ANTIGOS_MS
      } else {
        ultimaLeitura.value = formatarHora(Date.now())
        dadosAntigos.value = false
      }
    }
  } catch (e) {
    console.error('[dashboard]', e)
    erro.value = e
  } finally {
    carregando = false
    if (!desmontado) timerDash = setTimeout(carregar, DASH_MS)
  }
}

// ───────── Modal / tempo real (polling de 5s) ─────────
function atualizarLive(leitura) {
  const ultimo = liveHistorico.value.at(-1)
  liveData.value = { ...leitura }
  if (mesmaLeitura(ultimo, leitura)) return   // evita pontos duplicados

  const prev = ultimo?.temperatura
  if (typeof prev === 'number' && typeof leitura.temperatura === 'number' &&
      Math.abs(leitura.temperatura - prev) > 0.5) {
    tempFlash.value = true
    clearTimeout(timerFlash)
    timerFlash = setTimeout(() => (tempFlash.value = false), 800)
  }

  liveHistorico.value.push({ ...leitura })
  if (liveHistorico.value.length > MAX_LIVE_POINTS) liveHistorico.value.shift()
}

async function tickLive(sessao) {
  if (sessao !== sessaoModal) return
  if (!document.hidden) {
    try {
      const { data } = await getDashboard()
      if (sessao !== sessaoModal) return
      aplicarDashboard(data)
    } catch (e) {
      console.error('[live]', e)
    }
  }
  if (sessao !== sessaoModal) return
  timerLive = setTimeout(() => tickLive(sessao), LIVE_MS)
}

function pararTimersLive() {
  clearTimeout(timerLive)
  clearInterval(timerSeg)
  clearTimeout(timerFlash)
  timerLive = timerSeg = timerFlash = null
  tempFlash.value = false
}

async function abrirColmeia(c) {
  if (sel.value === c.id) { fecharModal(); return }
  pararTimersLive()
  const sessao = ++sessaoModal

  sel.value = c.id
  liveHistorico.value = []
  liveSegundos.value = 0
  liveData.value = c.ultima_leitura ? { ...c.ultima_leitura } : LEITURA_VAZIA()

  timerSeg = setInterval(() => liveSegundos.value++, 1000)
  nextTick(() => btnFechar.value?.focus())

  // Histórico inicial
  try {
    const { data } = await getHistorico(c.codigo, 20)
    if (sessao !== sessaoModal) return   // modal fechado durante a requisição
    liveHistorico.value = (data ?? []).slice().reverse().slice(-MAX_LIVE_POINTS)
    if (c.ultima_leitura) atualizarLive(c.ultima_leitura)
  } catch (e) {
    console.error('[historico]', e)
  }
  if (sessao !== sessaoModal) return

  timerLive = setTimeout(() => tickLive(sessao), LIVE_MS)
}

function fecharModal() {
  sessaoModal++
  pararTimersLive()
  sel.value = null
  liveHistorico.value = []
  liveData.value = LEITURA_VAZIA()
}

// Fecha o modal se a colmeia sumir do dashboard
watch(modalColmeia, (c) => {
  if (sel.value != null && dash.value && !c) fecharModal()
})

// Trava o scroll da página com o modal aberto
watch(sel, (v) => {
  document.body.style.overflow = v != null ? 'hidden' : ''
})

function onKeydown(e) {
  if (e.key === 'Escape' && sel.value != null) fecharModal()
}
function onVisibilidade() {
  if (!document.hidden) carregar()   // atualiza na hora ao voltar para a aba
}

// ───────── Cards ─────────
function gauges(c) {
  const l = c.ultima_leitura
  if (!l) return []
  return [
    { label: 'Temperatura', val: `${fmt(l.temperatura, 1)}°C`, pct: pct(l.temperatura, ESCALA.temp), color: l.temperatura > LIMITES.temp ? COR.rd : COR.gd },
    { label: 'Umidade', val: `${fmt(l.umidade, 1)}%`, pct: pct(l.umidade, ESCALA.umidade), color: l.umidade > LIMITES.umidade ? COR.am : COR.br3 },
    { label: 'Peso', val: `${fmt(l.peso, 1)} kg`, pct: pct(l.peso, ESCALA.peso), color: COR.gn },
  ]
}

// ───────── Sensores do modal ─────────
const tempAlta = computed(() => liveData.value.temperatura > LIMITES.temp)

const sensores = computed(() => {
  const d = liveData.value
  const umidAlta = d.umidade > LIMITES.umidade
  const somAlto = d.som > LIMITES.som
  return [
    {
      key: 'temp', ico: '🌡️', lbl: 'Temperatura',
      num: `${fmt(d.temperatura, 1)}°C`,
      pct: pct(d.temperatura, ESCALA.temp),
      cor: tempAlta.value ? COR.rd : COR.gd,
      warn: tempAlta.value, flash: tempFlash.value,
      status: d.temperatura == null ? '—' : tempAlta.value ? '⚠ Acima do ideal' : '✓ Normal',
    },
    {
      key: 'umid', ico: '💧', lbl: 'Umidade',
      num: `${fmt(d.umidade, 1)}%`,
      pct: pct(d.umidade, ESCALA.umidade),
      cor: umidAlta ? COR.am : COR.br3,
      warn: umidAlta, flash: false,
      status: d.umidade == null ? '—' : umidAlta ? '⚠ Alta' : '✓ Normal',
    },
    {
      key: 'peso', ico: '⚖️', lbl: 'Peso colônia',
      num: `${fmt(d.peso, 2)} kg`,
      pct: pct(d.peso, ESCALA.peso),
      cor: COR.gn,
      warn: false, flash: false,
      status: `produção: ${fmt(modalColmeia.value?.producao_estimada, 1)} kg`,
    },
    {
      key: 'som', ico: '🔊', lbl: 'Som abelhas',
      num: `${fmt(d.som, 0)} Hz`,
      pct: pct(d.som, ESCALA.som),
      cor: somAlto ? COR.rd : COR.br3,
      warn: somAlto, flash: false,
      status: d.som == null ? '—' : somAlto ? '⚠ Agitação' : '✓ Calma',
    },
  ]
})

// ───────── Diagnóstico (textos coerentes com os limiares) ─────────
const diagnostico = computed(() => {
  const c = modalColmeia.value
  if (!c || c.status === 'normal') return null
  if (c.status === 'critico') {
    return {
      texto: `Padrão sonoro anômalo (acima de ${LIMITES.somCritico} Hz) combinado com temperatura elevada (acima de ${LIMITES.temp} °C) indica possível enxameamento ou presença de varroase.`,
      acao: 'Vistoria presencial recomendada em até 12h.',
    }
  }
  return {
    texto: `Temperatura e/ou umidade acima dos limites ideais (${LIMITES.temp} °C / ${LIMITES.umidade}%). Monitorar nas próximas 6h.`,
    acao: 'Se persistir, avaliar sombreamento adicional e ventilação da colmeia.',
  }
})

// ───────── Gráfico ─────────
const temps = computed(() =>
  liveHistorico.value.map(r => r.temperatura).filter(t => typeof t === 'number' && !Number.isNaN(t))
)

const estat = computed(() => {
  const t = temps.value
  if (!t.length) return null
  const mn = Math.min(...t), mx = Math.max(...t)
  return { mn, mx, media: t.reduce((a, b) => a + b, 0) / t.length }
})
const tempMin = computed(() => fmt(estat.value?.mn, 1))
const tempMax = computed(() => fmt(estat.value?.mx, 1))
const tempMedia = computed(() => fmt(estat.value?.media, 1))

// Faixa do eixo Y: mínimo de 1 °C para não achatar a linha nem repetir rótulos
const faixaY = computed(() => {
  const e = estat.value
  if (!e) return null
  let lo = e.mn, hi = e.mx
  if (hi - lo < 1) {
    const mid = (lo + hi) / 2
    lo = mid - 0.5
    hi = mid + 0.5
  }
  return { lo, hi }
})

function yDe(t) {
  const { lo, hi } = faixaY.value
  return CHART.pad + (1 - (t - lo) / (hi - lo)) * (CHART.h - CHART.pad * 2)
}

const yLabels = computed(() => {
  const f = faixaY.value
  if (!f) return []
  return [f.hi, (f.lo + f.hi) / 2, f.lo].map(v => ({ v: v.toFixed(1), y: yDe(v) }))
})

const chartDots = computed(() => {
  if (!faixaY.value) return []
  const n = temps.value.length
  const larguraUtil = CHART.w - CHART.left - CHART.right
  return temps.value.map((t, i) => ({
    x: CHART.left + (i / Math.max(n - 1, 1)) * larguraUtil,
    y: yDe(t),
    hot: t > LIMITES.temp,
  }))
})
const ultimoDot = computed(() => chartDots.value.at(-1) ?? null)
const chartPoints = computed(() => chartDots.value.map(p => `${p.x},${p.y}`).join(' '))
const chartArea = computed(() => {
  if (!chartDots.value.length) return ''
  const f = chartDots.value[0], l = ultimoDot.value
  return `${f.x},${CHART.h} ${chartPoints.value} ${l.x},${CHART.h}`
})

// ───────── Ciclo de vida ─────────
onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  document.addEventListener('visibilitychange', onVisibilidade)
  carregar()
})

onUnmounted(() => {
  desmontado = true
  sessaoModal++
  clearTimeout(timerDash)
  pararTimersLive()
  window.removeEventListener('keydown', onKeydown)
  document.removeEventListener('visibilitychange', onVisibilidade)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.page{max-width:1160px;margin:0 auto;padding:24px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
.stat{background:var(--wh);border-radius:14px;padding:18px 20px;border-left:4px solid;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.stat-label{font-size:11px;color:var(--gy);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.stat-val{font-size:30px;font-weight:800;line-height:1}
.stat-sub{font-size:11px;color:var(--gy);margin-top:4px}

.erro-box{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--rdl);border:1px solid var(--rd);color:var(--rd);border-radius:12px;padding:14px 18px;margin-bottom:20px;font-size:14px;font-weight:600}
.btn-retry{background:var(--rd);color:#fff;border:none;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer}
.btn-retry:hover{opacity:.9}

.section-header{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.section-title{font-size:16px;font-weight:700;color:var(--br)}
.live-pill{display:flex;align-items:center;gap:6px;background:var(--gnl);border:1px solid var(--gn);border-radius:20px;padding:4px 12px;font-size:12px;color:var(--gnk);font-weight:600}
.live-pill-off{background:var(--rdl);border-color:var(--rd);color:var(--rd)}
.live-pill-off .live-dot{background:var(--rd);animation:none}
.live-pill-sm{display:flex;align-items:center;gap:5px;background:rgba(74,124,63,.1);border:1px solid var(--gn);border-radius:20px;padding:3px 10px;font-size:11px;color:var(--gnk);font-weight:600;white-space:nowrap}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--gn);animation:pulse 1.8s infinite;flex-shrink:0}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(74,124,63,.5)}50%{opacity:.7;box-shadow:0 0 0 5px rgba(74,124,63,0)}}

.hive-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.hive-card{background:var(--wh);border-radius:14px;padding:18px;cursor:pointer;transition:all .25s;border:2px solid transparent;box-shadow:0 2px 10px rgba(0,0,0,.06);outline:none}
.hive-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.1)}
.hive-card:focus-visible{box-shadow:0 0 0 3px var(--gd)}
.hive-card.selected{border-color:var(--gd);background:var(--gpl);box-shadow:0 0 0 4px rgba(245,184,0,.15)}
.hive-card.alerta{border-color:var(--am)}
.hive-card.critico{border-color:var(--rd);animation:glow 2s infinite}
@keyframes glow{0%,100%{box-shadow:0 2px 10px rgba(0,0,0,.06)}50%{box-shadow:0 0 16px rgba(192,57,43,.35)}}
.hive-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.hive-id{font-weight:800;font-size:15px;color:var(--br)}
.badge{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.badge-normal{background:var(--gnl);color:var(--gnk)}
.badge-alerta{background:var(--aml);color:var(--amk)}
.badge-critico{background:var(--rdl);color:var(--rd)}
.hive-florada{font-size:12px;color:var(--gy);margin-bottom:12px}
.gauge{margin-bottom:10px}
.gauge-row{display:flex;justify-content:space-between;font-size:11px;color:var(--gy);margin-bottom:3px}
.gauge-val{font-weight:700}
.gauge-track{height:7px;background:var(--gyl);border-radius:4px;overflow:hidden}
.gauge-fill{height:100%;border-radius:4px;transition:width .7s cubic-bezier(.4,0,.2,1)}
.hive-prod{font-size:12px;color:var(--gy);margin-top:10px;padding-top:10px;border-top:1px solid var(--gyl)}
.hive-prod strong{color:var(--gn)}
.hive-click-hint{font-size:11px;color:var(--gdk);text-align:center;margin-top:12px;opacity:.6}
.sem-dados{font-size:12px;color:var(--gy);text-align:center;padding:16px}
.loading{text-align:center;color:var(--gy);padding:60px;display:flex;flex-direction:column;align-items:center;gap:12px}
.loading-spinner{width:32px;height:32px;border:3px solid var(--gyl);border-top-color:var(--gd);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* Modal */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:200;backdrop-filter:blur(2px);padding:16px}
.modal{background:var(--of);border-radius:20px;padding:28px;width:640px;max-width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.modal-header{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:20px}
.modal-header-right{display:flex;align-items:center;gap:10px}
.modal-title{font-size:22px;font-weight:800;color:var(--br)}
.modal-sub{font-size:13px;color:var(--gy);margin-top:3px}
.modal-close{background:var(--gyl);border:none;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:14px;color:var(--br);transition:background .2s;flex-shrink:0}
.modal-close:hover,.modal-close:focus-visible{background:var(--gd);outline:none}

/* Sensores */
.sensor-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px}
.sensor-box{background:var(--wh);border-radius:12px;padding:14px;text-align:center;border:1px solid var(--gyl);transition:all .3s}
.sensor-box.sensor-warn{background:var(--rdl);border-color:var(--rd)}
/* Anima a sombra (não o fundo) para não apagar o vermelho do alerta */
.sensor-box.flash{animation:flash-anim .8s ease}
@keyframes flash-anim{0%,100%{box-shadow:0 0 0 0 rgba(245,184,0,0)}50%{box-shadow:0 0 0 4px rgba(245,184,0,.55)}}
.sensor-ico{font-size:24px;margin-bottom:5px}
.sensor-lbl{font-size:10px;color:var(--gy);text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px}
.sensor-num{font-size:22px;font-weight:800;color:var(--br);transition:color .3s}
.sensor-bar{height:4px;background:var(--gyl);border-radius:2px;overflow:hidden;margin:6px 0 4px}
.sensor-bar-fill{height:100%;border-radius:2px;transition:width .8s cubic-bezier(.4,0,.2,1)}
.sensor-status{font-size:10px;color:var(--gy)}

/* Gráfico */
.chart-section{background:var(--wh);border-radius:14px;padding:18px;margin-bottom:16px;border:1px solid var(--gyl)}
.chart-header{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.chart-title{font-size:13px;font-weight:700;color:var(--br)}
.chart-meta{font-size:11px;color:var(--gy)}
.chart-svg{width:100%;height:120px}
.grid-line{stroke:var(--gyl);stroke-width:1;stroke-dasharray:4,4}
.y-label{font-size:10px;fill:var(--gy)}
.chart-area{fill:rgba(245,184,0,.08)}
.chart-line{fill:none;stroke:var(--gd);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.chart-dot{fill:var(--gd);stroke:#fff;stroke-width:1}
.chart-dot.hot{fill:var(--rd)}
.chart-dot-last{stroke-width:2}
.chart-info{font-size:12px;color:var(--gy);text-align:center;margin-top:8px}
.chart-info strong{color:var(--br)}
.chart-empty{display:flex;align-items:center;justify-content:center;gap:10px;color:var(--gy);padding:20px;font-size:13px}

/* Diagnóstico */
.diagnostico{border-radius:12px;padding:16px;border:1px solid}
.diag-critico{background:var(--rdl);border-color:var(--rd)}
.diag-alerta{background:var(--aml);border-color:var(--am)}
.diag-title{font-weight:700;margin-bottom:8px;font-size:14px}
.diag-critico .diag-title{color:var(--rd)}
.diag-alerta .diag-title{color:var(--amk)}
.diag-body{font-size:13px;color:var(--br);line-height:1.6}

/* Responsivo */
@media (max-width: 960px){
  .stats-grid{grid-template-columns:repeat(2,1fr)}
  .hive-grid{grid-template-columns:repeat(2,1fr)}
}
@media (max-width: 600px){
  .page{padding:16px}
  .stats-grid{grid-template-columns:1fr 1fr;gap:10px}
  .stat{padding:14px}
  .stat-val{font-size:24px}
  .hive-grid{grid-template-columns:1fr}
  .modal{padding:18px;border-radius:16px}
  .modal-header{flex-direction:column}
  .sensor-grid{grid-template-columns:repeat(2,1fr)}
}
</style>