<template>
  <div class="page">

    <!-- Stats -->
    <div class="stats-grid" v-if="dash">
      <div class="stat" style="border-left-color:var(--gd)">
        <div class="stat-label">Colmeias ativas</div>
        <div class="stat-val" style="color:var(--br)">{{ dash.total_colmeias }}</div>
      </div>
      <div class="stat" :style="`border-left-color:${dash.colmeias_alerta>0?'var(--rd)':'var(--gn)'}`">
        <div class="stat-label">Alertas ativos</div>
        <div class="stat-val" :style="`color:${dash.colmeias_alerta>0?'var(--rd)':'var(--gn)'}`">
          {{ dash.colmeias_alerta }}
        </div>
      </div>
      <div class="stat" style="border-left-color:var(--gn)">
        <div class="stat-label">Produção estimada</div>
        <div class="stat-val" style="color:var(--gn)">{{ dash.producao_total_estimada.toFixed(1) }} kg</div>
      </div>
      <div class="stat" style="border-left-color:var(--br3)">
        <div class="stat-label">Lotes aprovados</div>
        <div class="stat-val" style="color:var(--br3)">{{ dash.lotes_aprovados }}</div>
      </div>
    </div>

    <!-- Colmeias -->
    <div class="section-title">🐝 Monitoramento em tempo real · Capitão Poço — AL</div>
    <div class="hive-grid" v-if="dash">
      <div
        v-for="c in dash.colmeias" :key="c.id"
        class="hive-card"
        :class="{ selected: sel===c.id, alerta: c.status==='alerta', critico: c.status==='critico' }"
        @click="sel = sel===c.id ? null : c.id"
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
              <span class="gauge-val">{{ g.val }}</span>
            </div>
            <div class="gauge-track">
              <div class="gauge-fill" :style="`width:${g.pct}%;background:${g.color}`"></div>
            </div>
          </div>
        </template>

        <!-- Expandido -->
        <div v-if="sel===c.id && c.ultima_leitura" class="hive-detail">
          <div class="sensor-box">
            <div class="sensor-ico">🌡️</div>
            <div class="sensor-lbl">Temperatura</div>
            <div class="sensor-num" :style="c.ultima_leitura.temperatura>37?'color:var(--rd)':''">
              {{ c.ultima_leitura.temperatura }}°C
            </div>
          </div>
          <div class="sensor-box">
            <div class="sensor-ico">💧</div>
            <div class="sensor-lbl">Umidade</div>
            <div class="sensor-num">{{ c.ultima_leitura.umidade }}%</div>
          </div>
          <div class="sensor-box">
            <div class="sensor-ico">⚖️</div>
            <div class="sensor-lbl">Peso</div>
            <div class="sensor-num">{{ c.ultima_leitura.peso }} kg</div>
          </div>
          <div class="sensor-box">
            <div class="sensor-ico">🔊</div>
            <div class="sensor-lbl">Som</div>
            <div class="sensor-num" :style="c.ultima_leitura.som>350?'color:var(--rd)':''">
              {{ c.ultima_leitura.som }} Hz
            </div>
          </div>
          <div class="sensor-box" style="grid-column:1/-1;background:var(--gnl)">
            <div class="sensor-ico">🍯</div>
            <div class="sensor-lbl">Produção estimada</div>
            <div class="sensor-num" style="color:var(--gn);font-size:20px">
              {{ c.producao_estimada_kg?.toFixed(2) ?? '—' }} kg
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="!dash" class="loading">Carregando dados IoT...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getDashboard } from '../api'

const dash = ref(null)
const sel  = ref(null)
let timer  = null

async function carregar() {
  try {
    const { data } = await getDashboard()
    dash.value = data
  } catch (e) { console.error(e) }
}

function gauges(c) {
  const l = c.ultima_leitura
  return [
    { label: 'Temperatura', val: `${l.temperatura}°C`,
      pct: (l.temperatura/45)*100,
      color: l.temperatura > 37 ? 'var(--rd)' : 'var(--gd)' },
    { label: 'Umidade', val: `${l.umidade}%`,
      pct: l.umidade,
      color: l.umidade > 70 ? '#F59E0B' : 'var(--br3)' },
    { label: 'Peso', val: `${l.peso} kg`,
      pct: (l.peso/70)*100,
      color: 'var(--gn)' },
  ]
}

onMounted(() => { carregar(); timer = setInterval(carregar, 30000) })
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.page { max-width: 1160px; margin: 0 auto; padding: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 24px; }
.stat { background: var(--wh); border-radius: 14px; padding: 18px 20px; border-left: 4px solid; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.stat-label { font-size: 11px; color: var(--gy); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.stat-val { font-size: 30px; font-weight: 800; }
.section-title { font-size: 16px; font-weight: 700; color: var(--br); margin-bottom: 14px; }
.hive-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; }
.hive-card { background: var(--wh); border-radius: 14px; padding: 18px; cursor: pointer; transition: all .25s; border: 2px solid transparent; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.hive-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.1); }
.hive-card.selected { border-color: var(--gd); background: var(--gpl); }
.hive-card.alerta { border-color: #F59E0B; }
.hive-card.critico { border-color: var(--rd); animation: glow 2s infinite; }
@keyframes glow { 0%,100%{box-shadow:0 2px 10px rgba(0,0,0,.06)}50%{box-shadow:0 0 16px rgba(192,57,43,.35)} }
.hive-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.hive-id { font-weight: 800; font-size: 15px; }
.badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge-normal { background: var(--gnl); color: var(--gnk); }
.badge-alerta { background: #FFF3CD; color: #856404; }
.badge-critico { background: var(--rdl); color: var(--rd); }
.hive-florada { font-size: 12px; color: var(--gy); margin-bottom: 12px; }
.gauge { margin-bottom: 10px; }
.gauge-row { display: flex; justify-content: space-between; font-size: 11px; color: var(--gy); margin-bottom: 3px; }
.gauge-val { font-weight: 700; color: var(--br); }
.gauge-track { height: 7px; background: var(--gyl); border-radius: 4px; overflow: hidden; }
.gauge-fill { height: 100%; border-radius: 4px; transition: width .7s; }
.hive-detail { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--gyl); }
.sensor-box { background: var(--of); border-radius: 10px; padding: 12px; text-align: center; }
.sensor-ico { font-size: 22px; margin-bottom: 4px; }
.sensor-lbl { font-size: 10px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; }
.sensor-num { font-size: 18px; font-weight: 800; margin-top: 2px; }
.loading { text-align: center; color: var(--gy); padding: 60px; }
</style>
