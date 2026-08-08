<template>
  <div class="page">

    <!-- ── STATS ─────────────────────────────────────── -->
    <div class="stats-grid" v-if="dash">
      <div class="stat" style="border-left-color:var(--gd)">
        <div class="stat-label">Colmeias ativas</div>
        <div class="stat-val" style="color:var(--br)">{{ dash.total_colmeias }}</div>
        <div class="stat-sub">monitoradas por IoT</div>
      </div>
      <div class="stat" :style="`border-left-color:${dash.colmeias_alerta>0?'var(--rd)':'var(--gn)'}`">
        <div class="stat-label">Alertas ativos</div>
        <div class="stat-val" :style="`color:${dash.colmeias_alerta>0?'var(--rd)':'var(--gn)'}`">
          {{ dash.colmeias_alerta }}
        </div>
        <div class="stat-sub">{{ dash.colmeias_alerta===0 ? 'todas normais ✓' : 'requerem atenção' }}</div>
      </div>
      <div class="stat" style="border-left-color:var(--gn)">
        <div class="stat-label">Produção estimada</div>
        <div class="stat-val" style="color:var(--gn)">{{ dash.producao_total_estimada?.toFixed(1) }} kg</div>
        <div class="stat-sub">ciclo atual</div>
      </div>
      <div class="stat" style="border-left-color:var(--br3)">
        <div class="stat-label">Último ciclo IoT</div>
        <div class="stat-val" style="color:var(--br3);font-size:18px">{{ ultimaLeitura }}</div>
        <div class="stat-sub">atualiza a cada 30s</div>
      </div>
    </div>

    <!-- ── HEADER COLMEIAS ──────────────────────────── -->
    <div class="section-header">
      <div class="section-title">🐝 Monitoramento em tempo real · Capitão Poço — AL</div>
      <div class="live-pill">
        <span class="live-dot"></span>
        IoT ativo · ciclo {{ ciclo }}
      </div>
    </div>

    <!-- ── GRID COLMEIAS ────────────────────────────── -->
    <div class="hive-grid" v-if="dash">
      <div
        v-for="c in dash.colmeias" :key="c.id"
        class="hive-card"
        :class="{ selected: sel===c.id, alerta: c.status==='alerta', critico: c.status==='critico' }"
        @click="abrirColmeia(c)"
      >
        <div class="hive-top">
          <span class="hive-id">🐝 {{ c.codigo }}</span>
          <span class="badge" :class="`badge-${c.status}`">
            {{ c.status==='normal'?'Normal':c.status==='alerta'?'⚠ Alerta':'🔴 Crítico' }}
          </span>
        </div>
        <div class="hive-florada">🌸 {{ c.florada }}</div>

        <template v-if="c.ultima_leitura">
          <div class="gauge" v-for="g in gauges(c)" :key="g.label">
            <div class="gauge-row">
              <span>{{ g.label }}</span>
              <span class="gauge-val" :style="`color:${g.color}`">{{ g.val }}</span>
            </div>
            <div class="gauge-track">
              <div class="gauge-fill" :style="`width:${g.pct}%;background:${g.color}`"></div>
            </div>
          </div>
          <div class="hive-prod">
            🍯 Produção estimada: <strong>{{ c.producao_estimada?.toFixed(1) }} kg</strong>
          </div>
        </template>

        <div v-else class="sem-dados">Aguardando leitura IoT...</div>

        <div class="hive-click-hint">
          {{ sel===c.id ? '▲ fechar' : '▼ detalhes + histórico' }}
        </div>
      </div>
    </div>

    <div v-if="!dash" class="loading">
      <div class="loading-spinner"></div>
      Carregando dados IoT...
    </div>

    <!-- ── MODAL DETALHE ────────────────────────────── -->
    <Teleport to="body">
      <div v-if="modalColmeia" class="modal-overlay" @click.self="fecharModal">
        <div class="modal">
          <div class="modal-header">
            <div>
              <div class="modal-title">🐝 {{ modalColmeia.codigo }}</div>
              <div class="modal-sub">{{ modalColmeia.florada }} · {{ modalColmeia.status }}</div>
            </div>
            <button class="modal-close" @click="fecharModal">✕</button>
          </div>

          <!-- Sensores em tempo real -->
          <div class="sensor-grid">
            <div class="sensor-box" :class="modalColmeia.ultima_leitura?.temperatura>37?'sensor-warn':''">
              <div class="sensor-ico">🌡️</div>
              <div class="sensor-lbl">Temperatura</div>
              <div class="sensor-num" :style="modalColmeia.ultima_leitura?.temperatura>37?'color:var(--rd)':''">
                {{ modalColmeia.ultima_leitura?.temperatura?.toFixed(1) }}°C
              </div>
              <div class="sensor-status">{{ modalColmeia.ultima_leitura?.temperatura>37?'⚠ Acima do ideal':'✓ Normal' }}</div>
            </div>
            <div class="sensor-box" :class="modalColmeia.ultima_leitura?.umidade>70?'sensor-warn':''">
              <div class="sensor-ico">💧</div>
              <div class="sensor-lbl">Umidade</div>
              <div class="sensor-num">{{ modalColmeia.ultima_leitura?.umidade?.toFixed(1) }}%</div>
              <div class="sensor-status">{{ modalColmeia.ultima_leitura?.umidade>70?'⚠ Alta':'✓ Normal' }}</div>
            </div>
            <div class="sensor-box">
              <div class="sensor-ico">⚖️</div>
              <div class="sensor-lbl">Peso colônia</div>
              <div class="sensor-num">{{ modalColmeia.ultima_leitura?.peso?.toFixed(1) }} kg</div>
              <div class="sensor-status">produção: {{ modalColmeia.producao_estimada?.toFixed(1) }} kg</div>
            </div>
            <div class="sensor-box" :class="modalColmeia.ultima_leitura?.som>350?'sensor-warn':''">
              <div class="sensor-ico">🔊</div>
              <div class="sensor-lbl">Som abelhas</div>
              <div class="sensor-num" :style="modalColmeia.ultima_leitura?.som>350?'color:var(--rd)':''">
                {{ modalColmeia.ultima_leitura?.som?.toFixed(0) }} Hz
              </div>
              <div class="sensor-status">{{ modalColmeia.ultima_leitura?.som>350?'⚠ Agitação':'✓ Calma' }}</div>
            </div>
          </div>

          <!-- Gráfico histórico temperatura -->
          <div class="chart-section">
            <div class="chart-title">📈 Temperatura — últimas leituras</div>
            <div v-if="historico.length" class="chart-wrap">
              <svg :viewBox="`0 0 ${chartW} ${chartH}`" class="chart-svg">
                <!-- Grid lines -->
                <line v-for="y in [0.25,0.5,0.75]" :key="y"
                  x1="40" :y1="chartH*y" :x2="chartW-10" :y2="chartH*y"
                  stroke="#E8E4DC" stroke-width="1"/>
                <!-- Y labels -->
                <text v-for="(v,i) in yLabels" :key="i"
                  x="35" :y="chartH-(chartH*i/3)+4"
                  font-size="10" fill="#888780" text-anchor="end">{{v}}°</text>
                <!-- Line path -->
                <polyline
                  :points="chartPoints"
                  fill="none" stroke="#F5B800" stroke-width="2.5"
                  stroke-linejoin="round" stroke-linecap="round"/>
                <!-- Area fill -->
                <polygon :points="chartArea" fill="rgba(245,184,0,0.08)"/>
                <!-- Dots -->
                <circle v-for="(p,i) in chartDots" :key="i"
                  :cx="p.x" :cy="p.y" r="3"
                  :fill="p.hot?'#C0392B':'#F5B800'" stroke="#fff" stroke-width="1.5"/>
              </svg>
              <div class="chart-info">
                Mín: <strong>{{ tempMin }}°C</strong>
                Máx: <strong>{{ tempMax }}°C</strong>
                Média: <strong>{{ tempMedia }}°C</strong>
                · {{ historico.length }} leituras
              </div>
            </div>
            <div v-else class="chart-empty">Carregando histórico...</div>
          </div>

          <!-- Diagnóstico -->
          <div v-if="modalColmeia.status !== 'normal'" class="diagnostico">
            <div class="diag-title">⚠ Diagnóstico automático MelT3ch</div>
            <div class="diag-body">
              <template v-if="modalColmeia.status==='critico'">
                Padrão sonoro anômalo (>500 Hz) combinado com temperatura elevada indica possível
                enxameamento ou presença de varroase. <strong>Vistoria presencial recomendada em até 12h.</strong>
              </template>
              <template v-else>
                Temperatura e umidade acima dos limites ideais. Monitorar nas próximas 6h.
                Se persistir, avaliar sombreamento adicional e ventilação da colmeia.
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getDashboard, getHistorico } from '../api'

const dash         = ref(null)
const sel          = ref(null)
const modalColmeia = ref(null)
const historico    = ref([])
const ciclo        = ref(0)
const ultimaLeitura = ref('—')
let timer = null

const chartW = 560
const chartH = 120

// ── Carrega dashboard ──────────────────────────────
async function carregar() {
  try {
    const { data } = await getDashboard()
    dash.value = data
    ciclo.value++
    const agora = new Date()
    ultimaLeitura.value = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch (e) { console.error(e) }
}

// ── Abre modal e carrega histórico ────────────────
async function abrirColmeia(c) {
  if (sel.value === c.id) { fecharModal(); return }
  sel.value = c.id
  modalColmeia.value = c
  historico.value = []
  try {
    const { data } = await getHistorico(c.codigo, 48)
    historico.value = data.slice().reverse()
  } catch (e) { console.error(e) }
}

function fecharModal() {
  sel.value = null
  modalColmeia.value = null
  historico.value = []
}

// ── Gauges ────────────────────────────────────────
function gauges(c) {
  const l = c.ultima_leitura
  if (!l) return []
  return [
    { label: 'Temperatura', val: `${l.temperatura?.toFixed(1)}°C`,
      pct: (l.temperatura/45)*100,
      color: l.temperatura > 37 ? 'var(--rd)' : 'var(--gd)' },
    { label: 'Umidade', val: `${l.umidade?.toFixed(1)}%`,
      pct: l.umidade,
      color: l.umidade > 70 ? '#F59E0B' : 'var(--br3)' },
    { label: 'Peso', val: `${l.peso?.toFixed(1)} kg`,
      pct: (l.peso/70)*100,
      color: 'var(--gn)' },
  ]
}

// ── Chart ─────────────────────────────────────────
const temps = computed(() => historico.value.map(r => r.temperatura).filter(Boolean))
const tempMin   = computed(() => temps.value.length ? Math.min(...temps.value).toFixed(1) : '—')
const tempMax   = computed(() => temps.value.length ? Math.max(...temps.value).toFixed(1) : '—')
const tempMedia = computed(() => temps.value.length ? (temps.value.reduce((a,b)=>a+b,0)/temps.value.length).toFixed(1) : '—')
const yLabels   = computed(() => {
  if (!temps.value.length) return []
  const mn = parseFloat(tempMin.value), mx = parseFloat(tempMax.value)
  const rng = mx - mn || 1
  return [mn.toFixed(0), (mn+rng/2).toFixed(0), mx.toFixed(0)]
})

const chartDots = computed(() => {
  if (!temps.value.length) return []
  const mn = Math.min(...temps.value), mx = Math.max(...temps.value)
  const rng = mx - mn || 1
  const pad = 14
  return temps.value.map((t, i) => ({
    x: 40 + (i / Math.max(temps.value.length-1,1)) * (chartW - 50),
    y: pad + (1 - (t - mn) / rng) * (chartH - pad*2),
    hot: t > 37
  }))
})

const chartPoints = computed(() =>
  chartDots.value.map(p => `${p.x},${p.y}`).join(' ')
)
const chartArea = computed(() => {
  if (!chartDots.value.length) return ''
  const first = chartDots.value[0]
  const last  = chartDots.value[chartDots.value.length-1]
  return `${first.x},${chartH} ${chartPoints.value} ${last.x},${chartH}`
})

onMounted(() => { carregar(); timer = setInterval(carregar, 30000) })
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.page { max-width: 1160px; margin: 0 auto; padding: 24px; }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 24px; }
.stat { background: var(--wh); border-radius: 14px; padding: 18px 20px; border-left: 4px solid; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.stat-label { font-size: 11px; color: var(--gy); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.stat-val { font-size: 30px; font-weight: 800; line-height: 1; }
.stat-sub { font-size: 11px; color: var(--gy); margin-top: 4px; }

/* Header */
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.section-title { font-size: 16px; font-weight: 700; color: var(--br); }
.live-pill { display: flex; align-items: center; gap: 6px; background: var(--gnl); border: 1px solid var(--gn); border-radius: 20px; padding: 4px 12px; font-size: 12px; color: var(--gnk); font-weight: 600; }
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--gn); animation: pulse 1.8s infinite; }
@keyframes pulse { 0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(74,124,63,.5)}50%{opacity:.7;box-shadow:0 0 0 5px rgba(74,124,63,0)} }

/* Grid colmeias */
.hive-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }
.hive-card { background: var(--wh); border-radius: 14px; padding: 18px; cursor: pointer; transition: all .25s; border: 2px solid transparent; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.hive-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.1); }
.hive-card.selected { border-color: var(--gd); background: var(--gpl); box-shadow: 0 0 0 4px rgba(245,184,0,.15); }
.hive-card.alerta { border-color: #F59E0B; }
.hive-card.critico { border-color: var(--rd); animation: glow 2s infinite; }
@keyframes glow { 0%,100%{box-shadow:0 2px 10px rgba(0,0,0,.06)}50%{box-shadow:0 0 16px rgba(192,57,43,.35)} }
.hive-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.hive-id { font-weight: 800; font-size: 15px; color: var(--br); }
.badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge-normal { background: var(--gnl); color: var(--gnk); }
.badge-alerta { background: #FFF3CD; color: #856404; }
.badge-critico { background: var(--rdl); color: var(--rd); }
.hive-florada { font-size: 12px; color: var(--gy); margin-bottom: 12px; }
.gauge { margin-bottom: 10px; }
.gauge-row { display: flex; justify-content: space-between; font-size: 11px; color: var(--gy); margin-bottom: 3px; }
.gauge-val { font-weight: 700; }
.gauge-track { height: 7px; background: var(--gyl); border-radius: 4px; overflow: hidden; }
.gauge-fill { height: 100%; border-radius: 4px; transition: width .7s cubic-bezier(.4,0,.2,1); }
.hive-prod { font-size: 12px; color: var(--gy); margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--gyl); }
.hive-prod strong { color: var(--gn); }
.hive-click-hint { font-size: 11px; color: var(--gdk); text-align: center; margin-top: 12px; opacity: .6; }
.sem-dados { font-size: 12px; color: var(--gy); text-align: center; padding: 16px; }
.loading { text-align: center; color: var(--gy); padding: 60px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.loading-spinner { width: 32px; height: 32px; border: 3px solid var(--gyl); border-top-color: var(--gd); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 200; backdrop-filter: blur(2px); }
.modal { background: var(--of); border-radius: 20px; padding: 28px; width: 620px; max-width: 95vw; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,.3); }
.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.modal-title { font-size: 22px; font-weight: 800; color: var(--br); }
.modal-sub { font-size: 13px; color: var(--gy); margin-top: 3px; }
.modal-close { background: var(--gyl); border: none; border-radius: 50%; width: 32px; height: 32px; cursor: pointer; font-size: 14px; color: var(--br); transition: background .2s; }
.modal-close:hover { background: var(--gd); }

/* Sensor grid no modal */
.sensor-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 20px; }
.sensor-box { background: var(--wh); border-radius: 12px; padding: 14px; text-align: center; border: 1px solid var(--gyl); transition: all .2s; }
.sensor-box.sensor-warn { background: var(--rdl); border-color: var(--rd); }
.sensor-ico { font-size: 24px; margin-bottom: 5px; }
.sensor-lbl { font-size: 10px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
.sensor-num { font-size: 20px; font-weight: 800; color: var(--br); }
.sensor-status { font-size: 10px; color: var(--gy); margin-top: 4px; }

/* Chart */
.chart-section { background: var(--wh); border-radius: 14px; padding: 18px; margin-bottom: 16px; border: 1px solid var(--gyl); }
.chart-title { font-size: 13px; font-weight: 700; color: var(--br); margin-bottom: 14px; }
.chart-wrap { display: flex; flex-direction: column; gap: 8px; }
.chart-svg { width: 100%; height: 120px; }
.chart-info { font-size: 12px; color: var(--gy); text-align: center; }
.chart-info strong { color: var(--br); }
.chart-empty { text-align: center; color: var(--gy); padding: 30px; font-size: 13px; }

/* Diagnóstico */
.diagnostico { background: var(--rdl); border: 1px solid var(--rd); border-radius: 12px; padding: 16px; }
.diag-title { font-weight: 700; color: var(--rd); margin-bottom: 8px; font-size: 14px; }
.diag-body { font-size: 13px; color: var(--br); line-height: 1.6; }
</style>