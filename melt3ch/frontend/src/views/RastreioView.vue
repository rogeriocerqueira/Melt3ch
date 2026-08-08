<template>
  <div class="rastreio-page">

    <!-- LOADING -->
    <div v-if="carregando" class="loading-screen">
      <div class="loading-ico">🍯</div>
      <div class="loading-txt">Verificando autenticidade...</div>
    </div>

    <!-- ERRO -->
    <div v-else-if="erro" class="erro-screen">
      <div style="font-size:48px;margin-bottom:12px">❌</div>
      <div style="font-weight:700;font-size:17px;color:var(--rd)">Lote não encontrado</div>
      <div style="color:var(--gy);margin-top:8px">{{ route.params.codigo }}</div>
    </div>

    <!-- CONTEÚDO -->
    <div v-else-if="lote">

      <!-- HERO -->
      <div class="hero">
        <div class="hero-glow"></div>
        <div class="hero-content">
          <div class="qr-ok">
            <span class="qr-dot"></span>
            <span>QR code verificado · Produto autêntico</span>
          </div>
          <div class="hero-ico">🍯</div>
          <div class="hero-brand">MEL IGAPÓ</div>
          <div class="hero-slogan">DA FLORESTA AO SEU POTE</div>
          <div class="hero-lote">
            <div class="lote-cod">Lote {{ lote.codigo }}</div>
            <div class="lote-tags">
              <span class="tag" v-if="lote.status_lab==='aprovado'">✅ Aprovado</span>
              <span class="tag">📡 IoT</span>
              <span class="tag">🌿 {{ lote.produtor_municipio }} — {{ lote.produtor_estado }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- TABS -->
      <div class="tabs">
        <button v-for="t in abas" :key="t.id"
          class="tab" :class="{active:aba===t.id}" @click="aba=t.id">
          {{ t.label }}
        </button>
      </div>

      <!-- ORIGEM -->
      <div v-if="aba==='origem'" class="section">
        <div class="eyebrow">🌿 Origem</div>
        <div class="title">Nasceu no sertão de {{ lote.produtor_municipio }}</div>
        <div class="body">Mel produzido em área de caatinga preservada, sem agrotóxicos, com florada de <strong>{{ lote.florada }}</strong>.</div>
        <div v-if="lote.data_extracao" class="info-card">
          <div class="info-row">
            <span class="info-key">Extração</span>
            <span class="info-val">{{ formatDate(lote.data_extracao) }}</span>
          </div>
          <div class="info-row">
            <span class="info-key">Volume do lote</span>
            <span class="info-val">{{ lote.volume_kg }} kg</span>
          </div>
          <div class="info-row">
            <span class="info-key">Colmeias</span>
            <span class="info-val">{{ lote.colmeias.join(', ') }}</span>
          </div>
          <div class="info-row">
            <span class="info-key">Florada</span>
            <span class="info-val">{{ lote.florada }}</span>
          </div>
        </div>
      </div>

      <!-- LAUDO -->
      <div v-if="aba==='laudo'" class="section">
        <div class="eyebrow">🔬 Análise laboratorial</div>
        <div class="title">Laudo técnico completo</div>
        <div class="body" v-if="lote.laudo">
          Realizado em {{ formatDate(lote.laudo.data_analise) }} por {{ lote.laudo.responsavel_tecnico }}.
        </div>
        <div v-if="lote.laudo" class="laudo-grid">
          <div class="laudo-item" v-for="(v,k) in laudoItens" :key="k">
            <div class="laudo-key">{{ k }}</div>
            <div class="laudo-val">{{ v }}</div>
          </div>
        </div>
        <div v-if="lote.laudo?.aprovado" class="aprovado">
          <div style="font-size:28px;margin-bottom:6px">🏆</div>
          <div style="font-weight:700;color:var(--gnk);font-size:15px">APROVADO · PREMIUM</div>
          <div style="font-size:12px;color:var(--gn);margin-top:4px">
            Apto para consumo · Todos os parâmetros dentro da legislação vigente
          </div>
        </div>
        <div v-else-if="lote.laudo" class="reprovado">Lote reprovado</div>
        <div v-else class="em-analise">🧪 Em análise laboratorial</div>
      </div>

      <!-- JORNADA -->
      <div v-if="aba==='jornada'" class="section">
        <div class="eyebrow">📍 Jornada</div>
        <div class="title">Da colmeia ao seu pote</div>

        <div class="etapas">
          <div v-for="(e,i) in lote.etapas" :key="i" class="etapa" @click="etapaAtiva=i">
            <div class="etapa-spine">
              <div class="etapa-circulo" :class="i<etapaAtiva?'feito':i===etapaAtiva?'ativo':'pend'">
                {{ e.icone }}
              </div>
              <div v-if="i<lote.etapas.length-1" class="etapa-linha" :class="i<etapaAtiva?'feito':'pend'"></div>
            </div>
            <div class="etapa-body">
              <div class="etapa-card" :class="i<etapaAtiva?'feito':i===etapaAtiva?'ativo':'pend'">
                <div class="etapa-titulo">{{ e.titulo }}</div>
                <div class="etapa-meta">{{ e.data }} · {{ e.local }}</div>
                <div v-if="i===etapaAtiva" class="etapa-detalhe">{{ e.detalhe }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="impacto">
          <div style="font-size:20px;margin-bottom:6px">🌿</div>
          <div style="font-weight:700;color:var(--gnk);font-size:14px">Floresta preservada · Bioeconomia</div>
          <div style="font-size:12px;color:var(--gn);margin-top:4px;line-height:1.6">
            A qualidade deste mel depende da floresta. Ao escolher Mel Igapó, você apoia a preservação da caatinga alagoana.
          </div>
        </div>
      </div>

      <!-- FOOTER -->
      <div class="footer">
        <div class="footer-brand">MEL IGAPÓ</div>
        <div class="footer-sub">DA FLORESTA AO SEU POTE</div>
        <button class="btn-compartilhar" @click="compartilhar">📤 Compartilhar</button>
        <div class="footer-legal">
          MelT3ch Platform · Rastreabilidade apícola com IoT<br>
          Lote {{ lote.codigo }} · {{ lote.produtor_municipio }} — {{ lote.produtor_estado }}
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getRastreio } from '../api'

const route = useRoute()
const lote = ref(null)
const carregando = ref(true)
const erro = ref(false)
const aba = ref('origem')
const etapaAtiva = ref(6)

const abas = [
  { id: 'origem', label: '🌿 Origem' },
  { id: 'laudo',  label: '🔬 Análise' },
  { id: 'jornada', label: '📍 Jornada' },
]

const laudoItens = computed(() => {
  if (!lote.value?.laudo) return {}
  const l = lote.value.laudo
  return {
    'Brix': `${l.brix}%`, 'pH': l.ph,
    'HMF': `${l.hmf} mg/kg`, 'Diastase': `${l.diastase} DN`,
    'Umidade': `${l.umidade_mel}%`, 'Cor': l.cor,
  }
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}

function compartilhar() {
  if (navigator.share) {
    navigator.share({ title: 'Mel Igapó', text: 'Mel rastreado da caatinga alagoana!', url: window.location.href })
  } else {
    navigator.clipboard?.writeText(window.location.href)
  }
}

onMounted(async () => {
  try {
    const { data } = await getRastreio(route.params.codigo)
    lote.value = data
  } catch (e) {
    erro.value = true
  } finally {
    carregando.value = false
  }
})
</script>

<style scoped>
.rastreio-page { max-width: 480px; margin: 0 auto; background: var(--of); min-height: 100vh; }
.loading-screen,.erro-screen { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--br); text-align: center; }
.loading-ico { font-size: 52px; animation: float 2s ease-in-out infinite; margin-bottom: 16px; }
.loading-txt { color: var(--gdk); font-size: 14px; letter-spacing: 2px; }
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}

.hero { background: linear-gradient(160deg,#1a0d04,var(--br)); padding: 36px 24px; text-align: center; position: relative; overflow: hidden; }
.hero-glow { position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 40%, rgba(245,184,0,.1) 0%, transparent 70%); }
.hero-content { position: relative; z-index: 1; }
.qr-ok { display: inline-flex; align-items: center; gap: 8px; background: rgba(74,124,63,.2); border: 1px solid rgba(74,124,63,.4); border-radius: 20px; padding: 6px 14px; margin-bottom: 20px; }
.qr-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--gn); animation: pulse 1.8s infinite; }
.qr-ok span { font-size: 12px; color: var(--gnl); }
.hero-ico { font-size: 64px; animation: float 3s ease-in-out infinite; margin-bottom: 10px; filter: drop-shadow(0 8px 20px rgba(245,184,0,.3)); }
.hero-brand { font-size: 30px; font-weight: 800; color: var(--gd); letter-spacing: 5px; margin-bottom: 4px; }
.hero-slogan { font-size: 11px; letter-spacing: 3px; color: var(--gdk); margin-bottom: 20px; }
.hero-lote { background: rgba(255,255,255,.06); border: 1px solid rgba(245,184,0,.2); border-radius: 14px; padding: 14px 18px; }
.lote-cod { font-size: 13px; font-weight: 700; color: var(--gdk); margin-bottom: 8px; }
.lote-tags { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.tag { background: rgba(245,184,0,.15); border: 1px solid rgba(245,184,0,.3); border-radius: 20px; padding: 3px 10px; font-size: 11px; color: var(--gd); }

.tabs { display: flex; background: var(--br2); }
.tab { flex: 1; padding: 12px 8px; border: none; background: transparent; color: var(--gdk); cursor: pointer; font-size: 12px; font-weight: 600; transition: all .2s; }
.tab.active { background: var(--gd); color: var(--br); font-weight: 800; }

.section { padding: 24px 20px; }
.eyebrow { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--gdk); margin-bottom: 6px; font-weight: 700; }
.title { font-size: 20px; font-weight: 700; color: var(--br); margin-bottom: 8px; line-height: 1.3; }
.body { font-size: 14px; color: var(--br2); line-height: 1.7; margin-bottom: 16px; }

.info-card { background: var(--wh); border-radius: 14px; padding: 4px 0; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
.info-row { display: flex; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid var(--gyl); font-size: 13px; }
.info-row:last-child { border: none; }
.info-key { color: var(--gy); }
.info-val { font-weight: 700; color: var(--br); }

.laudo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 16px 0; }
.laudo-item { background: var(--wh); border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 1px 6px rgba(0,0,0,.05); }
.laudo-key { font-size: 10px; color: var(--gy); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 5px; }
.laudo-val { font-size: 16px; font-weight: 800; color: var(--br); }
.aprovado { background: var(--gnl); border: 1px solid var(--gn); border-radius: 14px; padding: 20px; text-align: center; }
.reprovado { background: var(--rdl); border: 1px solid var(--rd); border-radius: 14px; padding: 16px; text-align: center; color: var(--rd); font-weight: 700; }
.em-analise { background: #EEF2FF; border-radius: 14px; padding: 16px; text-align: center; color: #3730A3; font-weight: 700; }

.etapas { display: flex; flex-direction: column; }
.etapa { display: flex; gap: 14px; cursor: pointer; }
.etapa-spine { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; width: 44px; }
.etapa-circulo { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; transition: all .3s; border: 2px solid transparent; }
.etapa-circulo.feito { background: var(--gn); }
.etapa-circulo.ativo { background: var(--gd); box-shadow: 0 0 0 5px rgba(245,184,0,.25); }
.etapa-circulo.pend { background: var(--gyl); }
.etapa-linha { width: 2px; flex-grow: 1; min-height: 16px; margin: 3px 0; }
.etapa-linha.feito { background: var(--gn); }
.etapa-linha.pend { background: var(--gyl); }
.etapa-body { flex: 1; padding-bottom: 16px; }
.etapa-card { border-radius: 12px; padding: 12px 14px; border: 1.5px solid transparent; }
.etapa-card.feito { background: var(--gnl); border-color: #c5e0b8; }
.etapa-card.ativo { background: var(--gpl); border-color: var(--gdk); }
.etapa-card.pend { background: var(--gyl); }
.etapa-titulo { font-weight: 700; font-size: 14px; color: var(--br); margin-bottom: 3px; }
.etapa-meta { font-size: 11px; color: var(--gy); margin-bottom: 4px; }
.etapa-detalhe { font-size: 12px; color: var(--br2); line-height: 1.6; }

.impacto { background: var(--gnl); border: 1px solid var(--gn); border-radius: 14px; padding: 20px; text-align: center; margin-top: 16px; }

.footer { background: #1a0d04; padding: 32px 20px; text-align: center; }
.footer-brand { font-size: 20px; font-weight: 800; color: var(--gd); letter-spacing: 4px; margin-bottom: 4px; }
.footer-sub { font-size: 11px; color: var(--br3); letter-spacing: 2px; margin-bottom: 20px; }
.btn-compartilhar { background: var(--gd); color: var(--br); border: none; border-radius: 12px; padding: 13px 32px; font-size: 14px; font-weight: 800; cursor: pointer; width: 100%; margin-bottom: 16px; }
.footer-legal { font-size: 11px; color: rgba(136,135,128,.5); line-height: 1.6; }

@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(74,124,63,.5)}50%{opacity:.7;box-shadow:0 0 0 5px rgba(74,124,63,0)}}
</style>
