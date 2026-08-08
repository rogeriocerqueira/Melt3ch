<template>
  <div class="page">
    <div class="page-header">
      <div class="section-title">📦 Lotes de produção</div>
    </div>

    <!-- Resumo -->
    <div class="resumo-grid" v-if="lotes.length">
      <div class="resumo-card" style="border-color:var(--gn)">
        <div class="resumo-val" style="color:var(--gn)">{{ aprovados }}</div>
        <div class="resumo-lbl">Aprovados</div>
      </div>
      <div class="resumo-card" style="border-color:#6366F1">
        <div class="resumo-val" style="color:#6366F1">{{ emAnalise }}</div>
        <div class="resumo-lbl">Em análise</div>
      </div>
      <div class="resumo-card" style="border-color:var(--rd)">
        <div class="resumo-val" style="color:var(--rd)">{{ reprovados }}</div>
        <div class="resumo-lbl">Reprovados</div>
      </div>
    </div>

    <!-- Tabela -->
    <div class="table-wrap">
      <div class="table-header">
        <span>Lote</span><span>Florada</span>
        <span>Volume</span><span>Destino</span><span>Status</span>
      </div>
      <div
        v-for="l in lotes" :key="l.id"
        class="table-row"
        :class="{expanded: sel===l.id}"
        @click="sel = sel===l.id ? null : l.id"
      >
        <div>
          <div class="lote-codigo">{{ l.codigo }}</div>
          <div class="lote-data">{{ formatDate(l.data_extracao) }}</div>
        </div>
        <div class="lote-florada">{{ l.florada }}</div>
        <div>
          <div class="lote-vol">{{ l.volume_kg }} kg</div>
          <div class="lote-data">{{ l.colmeias?.join(', ') }}</div>
        </div>
        <div class="lote-destino">{{ l.destino || '—' }}</div>
        <span class="badge" :class="`badge-${l.status_lab}`">
          {{ labelStatus(l.status_lab) }}
        </span>

        <!-- Laudo expandido -->
        <div v-if="sel===l.id && l.laudo" class="laudo-expand">
          <div class="laudo-title">📋 Laudo técnico — {{ l.codigo }}</div>
          <div class="laudo-grid">
            <div class="laudo-item" v-for="(v,k) in laudoItens(l.laudo)" :key="k">
              <div class="laudo-key">{{ k }}</div>
              <div class="laudo-val">{{ v }}</div>
            </div>
          </div>
          <div class="laudo-result" :class="l.laudo.aprovado?'ok':'fail'">
            {{ l.laudo.aprovado ? '✅ APROVADO — apto para consumo e comercialização' : '❌ REPROVADO' }}
          </div>
        </div>

        <!-- QR code -->
        <div v-if="sel===l.id && l.status_lab==='aprovado'" class="qr-section">
          <button @click.stop="gerarQR(l.codigo)" class="btn-qr">
            📱 Gerar QR code do consumidor
          </button>
          <div v-if="qrData[l.codigo]" class="qr-wrap">
            <img :src="qrData[l.codigo]" alt="QR Code" class="qr-img"/>
            <div class="qr-url">
              URL: <a :href="`/rastreio/${l.codigo}`" target="_blank">
                /rastreio/{{ l.codigo }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!lotes.length && !carregando" class="empty">Nenhum lote cadastrado ainda.</div>
    <div v-if="carregando" class="loading">Carregando lotes...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getLotes, getQR } from '../api'

const lotes = ref([])
const sel = ref(null)
const qrData = ref({})
const carregando = ref(true)

const aprovados = computed(() => lotes.value.filter(l=>l.status_lab==='aprovado').length)
const emAnalise = computed(() => lotes.value.filter(l=>l.status_lab==='em_analise').length)
const reprovados = computed(() => lotes.value.filter(l=>l.status_lab==='reprovado').length)

function labelStatus(s) {
  return s==='aprovado'?'✓ Aprovado':s==='em_analise'?'⏳ Em análise':'✗ Reprovado'
}
function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}
function laudoItens(l) {
  return {
    'Brix': `${l.brix}%`, 'pH': l.ph,
    'HMF': `${l.hmf} mg/kg`, 'Diastase': `${l.diastase} DN`,
    'Umidade': `${l.umidade_mel}%`, 'Cor': l.cor,
    'Laboratório': l.laboratorio, 'Responsável': l.responsavel_tecnico
  }
}
async function gerarQR(codigo) {
  try {
    const { data } = await getQR(codigo)
    qrData.value[codigo] = data.qr_base64
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  try { const { data } = await getLotes(); lotes.value = data }
  catch (e) { console.error(e) }
  finally { carregando.value = false }
})
</script>

<style scoped>
.page { max-width: 1160px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 20px; }
.section-title { font-size: 17px; font-weight: 700; color: var(--br); }
.resumo-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 24px; }
.resumo-card { background: var(--wh); border-radius: 14px; padding: 20px; text-align: center; border: 2px solid; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.resumo-val { font-size: 36px; font-weight: 800; margin-bottom: 4px; }
.resumo-lbl { font-size: 12px; color: var(--gy); text-transform: uppercase; letter-spacing: 1px; }
.table-wrap { background: var(--wh); border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.06); }
.table-header { display: grid; grid-template-columns: 1.2fr 1.5fr .8fr 1.2fr 100px; gap: 12px; padding: 10px 16px; background: var(--gyl); font-size: 11px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; }
.table-row { display: grid; grid-template-columns: 1.2fr 1.5fr .8fr 1.2fr 100px; gap: 12px; align-items: center; padding: 14px 16px; border-bottom: 1px solid var(--gyl); cursor: pointer; transition: background .2s; font-size: 13px; }
.table-row:hover { background: var(--of); }
.table-row.expanded { background: var(--gpl); grid-template-columns: 1fr; }
.table-row.expanded > *:not(.laudo-expand):not(.qr-section) { display: none; }
.lote-codigo { font-weight: 700; color: var(--br); }
.lote-data { font-size: 11px; color: var(--gy); margin-top: 2px; }
.lote-florada { color: var(--br2); }
.lote-vol { font-weight: 700; color: var(--gn); font-size: 15px; }
.lote-destino { font-size: 12px; color: var(--gy); }
.badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.badge-aprovado { background: var(--gnl); color: var(--gnk); }
.badge-em_analise { background: #EEF2FF; color: #3730A3; }
.badge-reprovado { background: var(--rdl); color: var(--rd); }
.laudo-expand { grid-column: 1/-1; padding: 16px; background: var(--wh); border-radius: 12px; margin-top: 8px; }
.laudo-title { font-weight: 700; font-size: 14px; color: var(--br); margin-bottom: 14px; }
.laudo-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 14px; }
.laudo-item { background: var(--of); border-radius: 10px; padding: 12px; text-align: center; }
.laudo-key { font-size: 10px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
.laudo-val { font-size: 14px; font-weight: 700; color: var(--br); }
.laudo-result { padding: 12px; border-radius: 10px; text-align: center; font-weight: 700; font-size: 13px; }
.laudo-result.ok { background: var(--gnl); color: var(--gnk); }
.laudo-result.fail { background: var(--rdl); color: var(--rd); }
.qr-section { grid-column: 1/-1; padding: 12px 16px; }
.btn-qr { background: var(--br); color: var(--gd); border: none; border-radius: 10px; padding: 10px 20px; cursor: pointer; font-size: 13px; font-weight: 700; }
.qr-wrap { display: flex; align-items: center; gap: 16px; margin-top: 12px; }
.qr-img { width: 120px; height: 120px; border-radius: 8px; border: 3px solid var(--gd); }
.qr-url { font-size: 13px; color: var(--br2); }
.qr-url a { color: var(--gdk); }
.loading, .empty { text-align: center; color: var(--gy); padding: 60px; }
</style>
