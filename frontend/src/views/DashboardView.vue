<template>
  <div class="page">
    <div class="stats-grid" v-if="dash">
      <div class="stat" style="border-left-color:var(--gd)">
        <div class="stat-label">Colmeias ativas</div>
        <div class="stat-val" style="color:var(--br)">{{ dash.total_colmeias }}</div>
        <div class="stat-sub">monitoradas por IoT</div>
      </div>
      <div class="stat" :style="`border-left-color:${dash.colmeias_alerta>0?'var(--rd)':'var(--gn)'}`">
        <div class="stat-label">Alertas ativos</div>
        <div class="stat-val" :style="`color:${dash.colmeias_alerta>0?'var(--rd)':'var(--gn)'}`">{{ dash.colmeias_alerta }}</div>
        <div class="stat-sub">{{ dash.colmeias_alerta===0?'todas normais ✓':'requerem atenção' }}</div>
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

    <div class="section-header">
      <div class="section-title">🐝 Monitoramento em tempo real · Capitão Poço — AL</div>
      <div class="live-pill"><span class="live-dot"></span>IoT ativo · ciclo {{ ciclo }}</div>
    </div>

    <div class="hive-grid" v-if="dash">
      <div v-for="c in dash.colmeias" :key="c.id"
        class="hive-card"
        :class="{ selected:sel===c.id, alerta:c.status==='alerta', critico:c.status==='critico' }"
        @click="abrirColmeia(c)">
        <div class="hive-top">
          <span class="hive-id">🐝 {{ c.codigo }}</span>
          <span class="badge" :class="`badge-${c.status}`">
            {{ c.status==='normal'?'Normal':c.status==='alerta'?'⚠ Alerta':'🔴 Crítico' }}
          </span>
        </div>
        <div class="hive-florada">🌸 {{ c.florada }}</div>
        <template v-if="c.ultima_leitura">
          <div class="gauge" v-for="g in gauges(c)" :key="g.label">
            <div class="gauge-row"><span>{{ g.label }}</span><span class="gauge-val" :style="`color:${g.color}`">{{ g.val }}</span></div>
            <div class="gauge-track"><div class="gauge-fill" :style="`width:${g.pct}%;background:${g.color}`"></div></div>
          </div>
          <div class="hive-prod">🍯 Produção estimada: <strong>{{ c.producao_estimada?.toFixed(1) }} kg</strong></div>
        </template>
        <div v-else class="sem-dados">Aguardando leitura IoT...</div>
        <div class="hive-click-hint">{{ sel===c.id?'▲ fechar':'▼ detalhes em tempo real' }}</div>
      </div>
    </div>

    <div v-if="!dash" class="loading"><div class="loading-spinner"></div>Carregando dados IoT...</div>

    <Teleport to="body">
      <div v-if="modalColmeia" class="modal-overlay" @click.self="fecharModal">
        <div class="modal">
          <div class="modal-header">
            <div>
              <div class="modal-title">🐝 {{ modalColmeia.codigo }}</div>
              <div class="modal-sub">{{ modalColmeia.florada }} · {{ modalColmeia.status }}</div>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
              <div class="live-pill-sm"><span class="live-dot"></span>ao vivo · {{ liveSegundos }}s</div>
              <button class="modal-close" @click="fecharModal">✕</button>
            </div>
          </div>

          <!-- Sensores em tempo real -->
          <div class="sensor-grid">
            <div class="sensor-box" :class="[liveData.temperatura>37?'sensor-warn':'', tempFlash?'flash':'']">
              <div class="sensor-ico">🌡️</div>
              <div class="sensor-lbl">Temperatura</div>
              <div class="sensor-num" :style="liveData.temperatura>37?'color:var(--rd)':''">
                <span class="num-animate">{{ liveData.temperatura?.toFixed(1) }}</span>°C
              </div>
              <div class="sensor-bar">
                <div class="sensor-bar-fill" :style="`width:${(liveData.temperatura/45)*100}%;background:${liveData.temperatura>37?'var(--rd)':'var(--gd)'}`"></div>
              </div>
              <div class="sensor-status">{{ liveData.temperatura>37?'⚠ Acima do ideal':'✓ Normal' }}</div>
            </div>
            <div class="sensor-box" :class="liveData.umidade>70?'sensor-warn':''">
              <div class="sensor-ico">💧</div>
              <div class="sensor-lbl">Umidade</div>
              <div class="sensor-num">{{ liveData.umidade?.toFixed(1) }}%</div>
              <div class="sensor-bar">
                <div class="sensor-bar-fill" :style="`width:${liveData.umidade}%;background:${liveData.umidade>70?'#F59E0B':'var(--br3)'}`"></div>
              </div>
              <div class="sensor-status">{{ liveData.umidade>70?'⚠ Alta':'✓ Normal' }}</div>
            </div>
            <div class="sensor-box">
              <div class="sensor-ico">⚖️</div>
              <div class="sensor-lbl">Peso colônia</div>
              <div class="sensor-num">{{ liveData.peso?.toFixed(2) }} kg</div>
              <div class="sensor-bar">
                <div class="sensor-bar-fill" :style="`width:${(liveData.peso/70)*100}%;background:var(--gn)`"></div>
              </div>
              <div class="sensor-status">produção: {{ modalColmeia.producao_estimada?.toFixed(1) }} kg</div>
            </div>
            <div class="sensor-box" :class="liveData.som>350?'sensor-warn':''">
              <div class="sensor-ico">🔊</div>
              <div class="sensor-lbl">Som abelhas</div>
              <div class="sensor-num" :style="liveData.som>350?'color:var(--rd)':''">{{ liveData.som?.toFixed(0) }} Hz</div>
              <div class="sensor-bar">
                <div class="sensor-bar-fill" :style="`width:${(liveData.som/600)*100}%;background:${liveData.som>350?'var(--rd)':'var(--br3)'}`"></div>
              </div>
              <div class="sensor-status">{{ liveData.som>350?'⚠ Agitação':'✓ Calma' }}</div>
            </div>
          </div>

          <!-- Gráfico acumulando em tempo real -->
          <div class="chart-section">
            <div class="chart-header">
              <div class="chart-title">📈 Temperatura — acumulando em tempo real</div>
              <div class="chart-meta">{{ liveHistorico.length }} pontos · atualiza a cada 5s</div>
            </div>
            <div v-if="liveHistorico.length>1" class="chart-wrap">
              <svg :viewBox="`0 0 ${chartW} ${chartH}`" class="chart-svg">
                <!-- Grid -->
                <line v-for="y in [0.25,0.5,0.75]" :key="y"
                  x1="40" :y1="chartH*y" :x2="chartW-10" :y2="chartH*y"
                  stroke="#E8E4DC" stroke-width="1" stroke-dasharray="4,4"/>
                <!-- Y labels -->
                <text v-for="(v,i) in yLabels" :key="i"
                  x="35" :y="chartH-(chartH*i/3)+4"
                  font-size="10" fill="#888780" text-anchor="end">{{v}}°</text>
                <!-- Área -->
                <polygon :points="chartArea" fill="rgba(245,184,0,0.08)"/>
                <!-- Linha -->
                <polyline :points="chartPoints" fill="none" stroke="#F5B800"
                  stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
                <!-- Último ponto pulsando -->
                <circle v-if="chartDots.length"
                  :cx="chartDots[chartDots.length-1].x"
                  :cy="chartDots[chartDots.length-1].y"
                  r="5" fill="#F5B800" stroke="#fff" stroke-width="2">
                  <animate attributeName="r" values="5;8;5" dur="1.5s" repeatCount="indefinite"/>
                  <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/>
                </circle>
                <!-- Todos os pontos -->
                <circle v-for="(p,i) in chartDots.slice(0,-1)" :key="i"
                  :cx="p.x" :cy="p.y" r="2.5"
                  :fill="p.hot?'#C0392B':'#F5B800'" stroke="#fff" stroke-width="1"/>
              </svg>
              <div class="chart-info">
                Mín: <strong>{{ tempMin }}°C</strong> ·
                Máx: <strong>{{ tempMax }}°C</strong> ·
                Média: <strong>{{ tempMedia }}°C</strong> ·
                Agora: <strong :style="liveData.temperatura>37?'color:var(--rd)':''">{{ liveData.temperatura?.toFixed(1) }}°C</strong>
              </div>
            </div>
            <div v-else class="chart-empty">
              <div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div>
              Acumulando leituras...
            </div>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getDashboard, getHistorico } from '../api'

const dash = ref(null)
const sel = ref(null)
const modalColmeia = ref(null)
const liveHistorico = ref([])
const liveData = ref({ temperatura: 0, umidade: 0, peso: 0, som: 0 })
const ciclo = ref(0)
const ultimaLeitura = ref('—')
const liveSegundos = ref(0)
const tempFlash = ref(false)
let timerDash = null
let timerLive = null
let timerSeg = null
const chartW = 560, chartH = 120
const MAX_LIVE_POINTS = 60

async function carregar() {
  try {
    const { data } = await getDashboard()
    dash.value = data
    ciclo.value++
    ultimaLeitura.value = new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})
    // Atualiza liveData se modal aberto
    if (modalColmeia.value) {
      const c = data.colmeias.find(x => x.id === modalColmeia.value.id)
      if (c?.ultima_leitura) atualizarLive(c.ultima_leitura)
    }
  } catch (e) { console.error(e) }
}

function atualizarLive(leitura) {
  const prev = liveData.value.temperatura
  liveData.value = { ...leitura }
  // Flash se temperatura mudou significativamente
  if (Math.abs(leitura.temperatura - prev) > 0.5) {
    tempFlash.value = true
    setTimeout(() => tempFlash.value = false, 800)
  }
  // Adiciona ao histórico ao vivo
  liveHistorico.value.push({ ...leitura, ts: Date.now() })
  if (liveHistorico.value.length > MAX_LIVE_POINTS)
    liveHistorico.value.shift()
}

async function abrirColmeia(c) {
  if (sel.value === c.id) { fecharModal(); return }
  sel.value = c.id
  modalColmeia.value = c
  liveHistorico.value = []
  liveSegundos.value = 0

  // Carrega histórico inicial
  try {
    const { data } = await getHistorico(c.codigo, 20)
    const hist = data.slice().reverse()
    hist.forEach(r => liveHistorico.value.push({ ...r, ts: Date.now() }))
    if (c.ultima_leitura) liveData.value = { ...c.ultima_leitura }
  } catch (e) { console.error(e) }

  // Timer live — busca nova leitura a cada 5s
  timerLive = setInterval(async () => {
    try {
      const { data } = await getDashboard()
      const col = data.colmeias.find(x => x.id === c.id)
      if (col?.ultima_leitura) atualizarLive(col.ultima_leitura)
    } catch (e) {}
  }, 5000)

  // Contador de segundos
  timerSeg = setInterval(() => liveSegundos.value++, 1000)
}

function fecharModal() {
  sel.value = null
  modalColmeia.value = null
  liveHistorico.value = []
  liveData.value = { temperatura:0, umidade:0, peso:0, som:0 }
  clearInterval(timerLive)
  clearInterval(timerSeg)
  timerLive = null
  timerSeg = null
}

function gauges(c) {
  const l = c.ultima_leitura
  if (!l) return []
  return [
    { label:'Temperatura', val:`${l.temperatura?.toFixed(1)}°C`, pct:(l.temperatura/45)*100, color:l.temperatura>37?'var(--rd)':'var(--gd)' },
    { label:'Umidade', val:`${l.umidade?.toFixed(1)}%`, pct:l.umidade, color:l.umidade>70?'#F59E0B':'var(--br3)' },
    { label:'Peso', val:`${l.peso?.toFixed(1)} kg`, pct:(l.peso/70)*100, color:'var(--gn)' },
  ]
}

// Chart computeds
const temps = computed(() => liveHistorico.value.map(r=>r.temperatura).filter(Boolean))
const tempMin = computed(() => temps.value.length ? Math.min(...temps.value).toFixed(1) : '—')
const tempMax = computed(() => temps.value.length ? Math.max(...temps.value).toFixed(1) : '—')
const tempMedia = computed(() => temps.value.length ? (temps.value.reduce((a,b)=>a+b,0)/temps.value.length).toFixed(1) : '—')
const yLabels = computed(() => {
  if (!temps.value.length) return []
  const mn=parseFloat(tempMin.value), mx=parseFloat(tempMax.value), rng=mx-mn||1
  return [mn.toFixed(0),(mn+rng/2).toFixed(0),mx.toFixed(0)]
})
const chartDots = computed(() => {
  if (!temps.value.length) return []
  const mn=Math.min(...temps.value), mx=Math.max(...temps.value), rng=mx-mn||1, pad=14
  return temps.value.map((t,i)=>({
    x: 40+(i/Math.max(temps.value.length-1,1))*(chartW-50),
    y: pad+(1-(t-mn)/rng)*(chartH-pad*2),
    hot: t>37
  }))
})
const chartPoints = computed(()=>chartDots.value.map(p=>`${p.x},${p.y}`).join(' '))
const chartArea = computed(()=>{
  if (!chartDots.value.length) return ''
  const f=chartDots.value[0], l=chartDots.value[chartDots.value.length-1]
  return `${f.x},${chartH} ${chartPoints.value} ${l.x},${chartH}`
})

onMounted(()=>{ carregar(); timerDash=setInterval(carregar,30000) })
onUnmounted(()=>{ clearInterval(timerDash); clearInterval(timerLive); clearInterval(timerSeg) })
</script>

<style scoped>
.page{max-width:1160px;margin:0 auto;padding:24px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
.stat{background:var(--wh);border-radius:14px;padding:18px 20px;border-left:4px solid;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.stat-label{font-size:11px;color:var(--gy);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.stat-val{font-size:30px;font-weight:800;line-height:1}
.stat-sub{font-size:11px;color:var(--gy);margin-top:4px}
.section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.section-title{font-size:16px;font-weight:700;color:var(--br)}
.live-pill{display:flex;align-items:center;gap:6px;background:var(--gnl);border:1px solid var(--gn);border-radius:20px;padding:4px 12px;font-size:12px;color:var(--gnk);font-weight:600}
.live-pill-sm{display:flex;align-items:center;gap:5px;background:rgba(74,124,63,.1);border:1px solid var(--gn);border-radius:20px;padding:3px 10px;font-size:11px;color:var(--gnk);font-weight:600}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--gn);animation:pulse 1.8s infinite;flex-shrink:0}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(74,124,63,.5)}50%{opacity:.7;box-shadow:0 0 0 5px rgba(74,124,63,0)}}
.hive-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.hive-card{background:var(--wh);border-radius:14px;padding:18px;cursor:pointer;transition:all .25s;border:2px solid transparent;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.hive-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.1)}
.hive-card.selected{border-color:var(--gd);background:var(--gpl);box-shadow:0 0 0 4px rgba(245,184,0,.15)}
.hive-card.alerta{border-color:#F59E0B}
.hive-card.critico{border-color:var(--rd);animation:glow 2s infinite}
@keyframes glow{0%,100%{box-shadow:0 2px 10px rgba(0,0,0,.06)}50%{box-shadow:0 0 16px rgba(192,57,43,.35)}}
.hive-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.hive-id{font-weight:800;font-size:15px;color:var(--br)}
.badge{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.badge-normal{background:var(--gnl);color:var(--gnk)}
.badge-alerta{background:#FFF3CD;color:#856404}
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
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:200;backdrop-filter:blur(2px)}
.modal{background:var(--of);border-radius:20px;padding:28px;width:640px;max-width:95vw;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.modal-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px}
.modal-title{font-size:22px;font-weight:800;color:var(--br)}
.modal-sub{font-size:13px;color:var(--gy);margin-top:3px}
.modal-close{background:var(--gyl);border:none;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:14px;color:var(--br);transition:background .2s}
.modal-close:hover{background:var(--gd)}
/* Sensores */
.sensor-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px}
.sensor-box{background:var(--wh);border-radius:12px;padding:14px;text-align:center;border:1px solid var(--gyl);transition:all .3s}
.sensor-box.sensor-warn{background:var(--rdl);border-color:var(--rd)}
.sensor-box.flash{animation:flash-anim .8s ease}
@keyframes flash-anim{0%,100%{background:var(--wh)}50%{background:rgba(245,184,0,.3)}}
.sensor-ico{font-size:24px;margin-bottom:5px}
.sensor-lbl{font-size:10px;color:var(--gy);text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px}
.sensor-num{font-size:22px;font-weight:800;color:var(--br);transition:color .3s}
.sensor-bar{height:4px;background:var(--gyl);border-radius:2px;overflow:hidden;margin:6px 0 4px}
.sensor-bar-fill{height:100%;border-radius:2px;transition:width .8s cubic-bezier(.4,0,.2,1)}
.sensor-status{font-size:10px;color:var(--gy)}
/* Chart */
.chart-section{background:var(--wh);border-radius:14px;padding:18px;margin-bottom:16px;border:1px solid var(--gyl)}
.chart-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.chart-title{font-size:13px;font-weight:700;color:var(--br)}
.chart-meta{font-size:11px;color:var(--gy)}
.chart-svg{width:100%;height:120px}
.chart-info{font-size:12px;color:var(--gy);text-align:center;margin-top:8px}
.chart-info strong{color:var(--br)}
.chart-empty{display:flex;align-items:center;justify-content:center;gap:10px;color:var(--gy);padding:20px;font-size:13px}
/* Diagnóstico */
.diagnostico{background:var(--rdl);border:1px solid var(--rd);border-radius:12px;padding:16px}
.diag-title{font-weight:700;color:var(--rd);margin-bottom:8px;font-size:14px}
.diag-body{font-size:13px;color:var(--br);line-height:1.6}
</style>
