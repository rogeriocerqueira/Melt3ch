<template>
  <div id="app">
    <!-- Navbar — visível apenas em rotas autenticadas que NÃO sejam de rastreio público -->
    <nav
      v-if="mostrarNavbar"
      class="navbar"
      aria-label="Navegação principal"
    >
      <div class="nav-brand">
        <span class="nav-ico" aria-hidden="true">🍯</span>
        <span class="nav-name">MEL IGAPÓ</span>
        <span class="nav-sub">· MelT3ch</span>
      </div>

      <div class="nav-links">
        <router-link to="/dashboard" class="nav-link">
          <span aria-hidden="true">📊</span> Painel IoT
        </router-link>
        <router-link to="/lotes" class="nav-link">
          <span aria-hidden="true">📦</span> Lotes
        </router-link>
      </div>

      <div class="nav-actions">
        <span class="live-dot" aria-hidden="true"></span>
        <span class="live-txt">IoT ativo</span>
        <button type="button" class="btn-sair" @click="auth.sair()">Sair</button>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const route = useRoute()

// Login e rastreio público (o consumidor acessa via QR code) não exibem a
// navbar administrativa. Cada rota declara isso com `meta: { hideNav: true }`
// em router/index.js, então o layout não depende do formato das URLs.
const mostrarNavbar = computed(() => auth.logado && !route.meta.hideNav)
</script>

<!-- Estilos GLOBAIS: reset + paleta. Ficam sem `scoped` de propósito,
     pois precisam valer para todo o app (inclusive componentes filhos). -->
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --br: #3B2208; --br2: #5C3610; --br3: #8B5E2E;
  --gd: #F5B800; --gdk: #C8900A; --gpl: #FBF3D9;
  --gn: #4A7C3F; --gnl: #EAF3DE; --gnk: #2D5A24;
  --wh: #FFFFFF; --of: #FBF7F0; --gy: #888780; --gyl: #F4F2EF;
  --rd: #C0392B; --rdl: #FDECEA;
  --am: #F59E0B; --aml: #FFF3CD; --amk: #856404;  /* alerta */
  --in: #6366F1; --inl: #EEF2FF; --ink: #3730A3;  /* em análise */
}

body {
  /* system-ui primeiro garante boa fonte também em macOS/Linux/Android */
  font-family: system-ui, 'Segoe UI', sans-serif;
  background: var(--of);
  color: var(--br);
}

#app { min-height: 100vh; }
</style>

<!-- Estilos da NAVBAR: `scoped` para evitar colisão com classes genéricas
     (.nav-link, .navbar...) que componentes filhos possam usar. -->
<style scoped>
.navbar {
  background: var(--br); height: 56px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; position: sticky; top: 0; z-index: 100;
}

.nav-brand { display: flex; align-items: center; gap: 8px; }
.nav-ico { font-size: 22px; }
.nav-name { color: var(--gd); font-weight: 700; font-size: 16px; letter-spacing: 2px; }
.nav-sub { color: var(--br3); font-size: 12px; }

.nav-links { display: flex; gap: 4px; }
.nav-link {
  color: var(--gdk); text-decoration: none; padding: 8px 16px;
  border-radius: 8px; font-size: 13px;
  /* Evita `transition: all` — só animamos o que realmente muda */
  transition: background-color .2s, color .2s;
}
.nav-link:hover,
.nav-link.router-link-active {
  background: rgba(245, 184, 0, .15); color: var(--gd);
}

.nav-actions { display: flex; align-items: center; gap: 10px; }
.live-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--gn); animation: pulse 1.8s infinite;
}
.live-txt { color: var(--gdk); font-size: 12px; }

.btn-sair {
  background: rgba(255, 255, 255, .08); color: var(--gdk);
  border: 1px solid rgba(245, 184, 0, .2); border-radius: 8px;
  padding: 6px 14px; cursor: pointer; font-size: 12px;
  transition: background-color .2s, color .2s;
}
.btn-sair:hover { background: rgba(192, 57, 43, .2); color: var(--rd); }

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(74, 124, 63, .5); }
  50% { opacity: .7; box-shadow: 0 0 0 5px rgba(74, 124, 63, 0); }
}

/* Celular: esconde textos secundários para caber em uma linha */
@media (max-width: 640px) {
  .navbar { padding: 0 12px; }
  .nav-sub, .live-txt, .live-dot { display: none; }
  .nav-name { font-size: 14px; letter-spacing: 1px; }
  .nav-link { padding: 8px 10px; }
}

/* Acessibilidade: respeita quem prefere menos movimento na tela */
@media (prefers-reduced-motion: reduce) {
  .live-dot { animation: none; }
  .nav-link, .btn-sair { transition: none; }
}
</style>