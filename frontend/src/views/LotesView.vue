<template>
  <div class="page">
    <div class="page-header">
      <h1 class="section-title">📦 Lotes de produção</h1>
    </div>

    <div v-if="erro" class="erro-box" role="alert">
      <span>⚠ Não foi possível carregar os lotes.</span>
      <button type="button" class="btn-retry" @click="carregar">Tentar novamente</button>
    </div>

    <!-- Resumo -->
    <div v-if="lotes.length" class="resumo-grid">
      <div v-for="r in resumo" :key="r.status" class="resumo-card" :class="`resumo-${r.status}`">
        <div class="resumo-val">{{ r.total }}</div>
        <div class="resumo-lbl">{{ r.label }}</div>
      </div>
    </div>

    <!-- Tabela -->
    <div v-if="lotes.length" class="table-wrap">
      <div class="table-header" aria-hidden="true">
        <span>Lote</span><span>Florada</span><span>Volume</span><span>Destino</span><span>Status</span>
      </div>

      <article v-for="l in lotes" :key="l.id" class="lote" :class="{ expanded: sel === l.id }">
        <button
          type="button"
          class="table-row"
          :aria-expanded="sel === l.id"
          :aria-controls="`lote-detalhe-${l.id}`"
          @click="alternar(l.id)"
        >
          <span>
            <span class="lote-codigo">{{ l.codigo }}</span>
            <span class="lote-data">{{ formatarData(l.data_extracao) }}</span>
          </span>
          <span class="lote-florada">{{ l.florada || '—' }}</span>
          <span>
            <span class="lote-vol">{{ fmt(l.volume_kg, 1) }} kg</span>
            <span class="lote-data">{{ l.colmeias.join(', ') || '—' }}</span>
          </span>
          <span class="lote-destino">{{ l.destino || '—' }}</span>
          <span class="badge" :class="`badge-${l.status_lab}`">{{ STATUS_LOTE[l.status_lab] ?? l.status_lab }}</span>
        </button>

        <div v-if="sel === l.id" :id="`lote-detalhe-${l.id}`" class="detalhe">
          <!-- Laudo -->
          <div v-if="l.laudo" class="laudo-expand">
            <div class="laudo-title">
              📋 Laudo técnico — {{ l.codigo }}
              <span v-if="l.laudo.data_analise" class="laudo-dataa">· {{ formatarData(l.laudo.data_analise) }}</span>
            </div>
            <div class="laudo-grid">
              <div v-for="item in laudoItens(l.laudo)" :key="item.k" class="laudo-item">
                <div class="laudo-key">{{ item.k }}</div>
                <div class="laudo-val">{{ item.v }}</div>
              </div>
            </div>
            <div class="laudo-result" :class="l.laudo.aprovado ? 'ok' : 'fail'">
              {{ l.laudo.aprovado ? '✅ APROVADO — apto para consumo e comercialização' : '❌ REPROVADO' }}
            </div>
          </div>
          <div v-else class="sem-laudo">
            {{ l.status_lab === 'em_analise' ? '🧪 Laudo ainda não emitido — lote em análise.' : 'Sem laudo cadastrado.' }}
          </div>

          <!-- QR code (só para lote aprovado) -->
          <div v-if="l.status_lab === 'aprovado'" class="qr-section">
            <button
              v-if="!qr[l.codigo]"
              type="button"
              class="btn-qr"
              :disabled="gerandoQR === l.codigo"
              @click="gerarQR(l.codigo)"
            >
              {{ gerandoQR === l.codigo ? 'Gerando...' : '📱 Gerar QR code do consumidor' }}
            </button>
            <div v-if="erroQR === l.codigo" class="erro-qr" role="alert">Não foi possível gerar o QR code.</div>
            <div v-if="qr[l.codigo]" class="qr-wrap">
              <img :src="qr[l.codigo].qr_code_base64" :alt="`QR code do lote ${l.codigo}`" class="qr-img" />
              <div class="qr-info">
                <div class="qr-url">
                  Página do consumidor:<br>
                  <a :href="`/rastreio/${l.codigo}`" target="_blank" rel="noopener">{{ qr[l.codigo].url }}</a>
                </div>
                <a :href="qr[l.codigo].qr_code_base64" :download="`qrcode-${l.codigo}.png`" class="btn-baixar">
                  ⬇ Baixar PNG
                </a>
              </div>
            </div>
          </div>
        </div>
      </article>
    </div>

    <div v-if="!lotes.length && !carregando && !erro" class="empty">Nenhum lote cadastrado ainda.</div>
    <div v-if="carregando" class="loading">Carregando lotes...</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getLotes, getQR } from '../api'
import { STATUS_LOTE } from '../constants'
import { fmt, formatarData } from '../utils/format'

const lotes = ref([])
const sel = ref(null)
const qr = ref({})            // codigo → { url, qr_code_base64 }
const gerandoQR = ref(null)
const erroQR = ref(null)
const carregando = ref(true)
const erro = ref(false)

const resumo = computed(() =>
  ['aprovado', 'em_analise', 'reprovado'].map(status => ({
    status,
    label: { aprovado: 'Aprovados', em_analise: 'Em análise', reprovado: 'Reprovados' }[status],
    total: lotes.value.filter(l => l.status_lab === status).length,
  }))
)

function alternar(id) {
  sel.value = sel.value === id ? null : id
}

function laudoItens(l) {
  return [
    { k: 'Brix', v: `${fmt(l.brix, 1)}%` },
    { k: 'pH', v: fmt(l.ph, 1) },
    { k: 'HMF', v: `${fmt(l.hmf, 1)} mg/kg` },
    { k: 'Diastase', v: `${fmt(l.diastase, 1)} DN` },
    { k: 'Umidade', v: `${fmt(l.umidade_mel, 1)}%` },
    { k: 'Cor', v: l.cor || '—' },
    { k: 'Laboratório', v: l.laboratorio || '—' },
    { k: 'Responsável', v: l.responsavel_tecnico || '—' },
  ]
}

async function gerarQR(codigo) {
  gerandoQR.value = codigo
  erroQR.value = null
  try {
    const { data } = await getQR(codigo)
    qr.value = { ...qr.value, [codigo]: data }
  } catch (e) {
    console.error('[qr]', e)
    erroQR.value = codigo
  } finally {
    gerandoQR.value = null
  }
}

async function carregar() {
  carregando.value = true
  erro.value = false
  try {
    const { data } = await getLotes()
    lotes.value = data
  } catch (e) {
    console.error('[lotes]', e)
    erro.value = true
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
.page { max-width: 1160px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 20px; }
.section-title { font-size: 17px; font-weight: 700; color: var(--br); }

.erro-box { display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--rdl); border: 1px solid var(--rd); color: var(--rd); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; font-size: 14px; font-weight: 600; }
.btn-retry { background: var(--rd); color: #fff; border: none; border-radius: 8px; padding: 8px 14px; font-weight: 700; cursor: pointer; }

.resumo-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 24px; }
.resumo-card { background: var(--wh); border-radius: 14px; padding: 20px; text-align: center; border: 2px solid; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.resumo-val { font-size: 36px; font-weight: 800; margin-bottom: 4px; }
.resumo-lbl { font-size: 12px; color: var(--gy); text-transform: uppercase; letter-spacing: 1px; }
.resumo-aprovado { border-color: var(--gn); color: var(--gn); }
.resumo-em_analise { border-color: var(--in); color: var(--in); }
.resumo-reprovado { border-color: var(--rd); color: var(--rd); }

.table-wrap { background: var(--wh); border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.06); }
.table-header, .table-row { display: grid; grid-template-columns: 1.2fr 1.5fr .8fr 1.2fr 120px; gap: 12px; align-items: center; }
.table-header { padding: 10px 16px; background: var(--gyl); font-size: 11px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; }
.lote { border-bottom: 1px solid var(--gyl); }
.lote:last-child { border-bottom: none; }
.lote.expanded { background: var(--gpl); }
.table-row {
  width: 100%; padding: 14px 16px; border: none; background: transparent;
  text-align: left; font: inherit; font-size: 13px; color: inherit; cursor: pointer;
  transition: background-color .2s;
}
.table-row:hover { background: var(--of); }
.lote.expanded .table-row:hover { background: transparent; }
.table-row:focus-visible { outline: 3px solid var(--gd); outline-offset: -3px; }
.lote-codigo { display: block; font-weight: 700; color: var(--br); }
.lote-data { display: block; font-size: 11px; color: var(--gy); margin-top: 2px; }
.lote-florada { color: var(--br2); }
.lote-vol { display: block; font-weight: 700; color: var(--gn); font-size: 15px; }
.lote-destino { font-size: 12px; color: var(--gy); }

.badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; white-space: nowrap; justify-self: start; }
.badge-aprovado { background: var(--gnl); color: var(--gnk); }
.badge-em_analise { background: var(--inl); color: var(--ink); }
.badge-reprovado { background: var(--rdl); color: var(--rd); }

.detalhe { padding: 0 16px 16px; }
.laudo-expand { padding: 16px; background: var(--wh); border-radius: 12px; }
.laudo-title { font-weight: 700; font-size: 14px; color: var(--br); margin-bottom: 14px; }
.laudo-dataa { font-weight: 400; color: var(--gy); font-size: 13px; }
.laudo-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px; }
.laudo-item { background: var(--of); border-radius: 10px; padding: 12px; text-align: center; }
.laudo-key { font-size: 10px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
.laudo-val { font-size: 14px; font-weight: 700; color: var(--br); overflow-wrap: anywhere; }
.laudo-result { padding: 12px; border-radius: 10px; text-align: center; font-weight: 700; font-size: 13px; }
.laudo-result.ok { background: var(--gnl); color: var(--gnk); }
.laudo-result.fail { background: var(--rdl); color: var(--rd); }
.sem-laudo { padding: 14px 16px; background: var(--wh); border-radius: 12px; font-size: 13px; color: var(--gy); }

.qr-section { padding-top: 14px; }
.btn-qr { background: var(--br); color: var(--gd); border: none; border-radius: 10px; padding: 10px 20px; cursor: pointer; font-size: 13px; font-weight: 700; }
.btn-qr:disabled { opacity: .6; cursor: wait; }
.erro-qr { margin-top: 8px; font-size: 12px; color: var(--rd); }
.qr-wrap { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.qr-img { width: 140px; height: 140px; border-radius: 8px; border: 3px solid var(--gd); background: #fff; }
.qr-info { display: flex; flex-direction: column; gap: 10px; }
.qr-url { font-size: 13px; color: var(--br2); overflow-wrap: anywhere; }
.qr-url a { color: var(--gdk); }
.btn-baixar { align-self: flex-start; background: var(--gd); color: var(--br); border-radius: 8px; padding: 8px 14px; font-size: 12px; font-weight: 700; text-decoration: none; }

.loading, .empty { text-align: center; color: var(--gy); padding: 60px; }

/* Celular: cada lote vira um cartão */
@media (max-width: 760px) {
  .page { padding: 16px; }
  .resumo-grid { gap: 8px; }
  .resumo-card { padding: 14px 8px; }
  .resumo-val { font-size: 26px; }
  .table-header { display: none; }
  .table-row { grid-template-columns: 1fr auto; row-gap: 6px; }
  .table-row > span:not(.badge) { grid-column: 1; }
  .badge { grid-column: 2; grid-row: 1; justify-self: end; }
  .laudo-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>