<template>
  <div class="login-bg">
    <div class="login-card">
      <div class="login-header">
        <div class="login-ico" aria-hidden="true">🍯</div>
        <h1 class="login-brand">MEL IGAPÓ</h1>
        <div class="login-sub">MelT3ch Platform</div>
      </div>

      <form class="login-form" @submit.prevent="entrar">
        <div class="field">
          <label for="login-email">E-mail</label>
          <input id="login-email" v-model.trim="email" type="email" autocomplete="username" required />
        </div>
        <div class="field">
          <label for="login-senha">Senha</label>
          <input id="login-senha" v-model="senha" type="password" autocomplete="current-password" required />
        </div>
        <div v-if="erro" class="erro" role="alert">{{ erro }}</div>
        <button type="submit" :disabled="carregando" class="btn-login">
          {{ carregando ? 'Entrando...' : 'Entrar na plataforma' }}
        </button>
      </form>

      <!-- Credenciais de demonstração: só aparecem em desenvolvimento -->
      <div v-if="DEMO" class="login-hint">
        <span>MVP Demo:</span>
        <code>daiane@melt3ch.com / melt3ch2026</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const DEMO = import.meta.env.DEV

const auth = useAuthStore()
const route = useRoute()

const email = ref(DEMO ? 'daiane@melt3ch.com' : '')
const senha = ref(DEMO ? 'melt3ch2026' : '')
const erro = ref('')
const carregando = ref(false)

// Só aceita redirecionar para caminhos internos
function destino() {
  const r = route.query.redirect
  return typeof r === 'string' && r.startsWith('/') && !r.startsWith('//') ? r : '/dashboard'
}

async function entrar() {
  erro.value = ''
  carregando.value = true
  try {
    await auth.entrar(email.value, senha.value, destino())
  } catch (e) {
    erro.value = e.response?.status === 401
      ? 'E-mail ou senha incorretos'
      : 'Não foi possível conectar ao servidor. Tente novamente.'
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.login-bg {
  min-height: 100vh; background: var(--br);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.login-card {
  background: var(--wh); border-radius: 20px;
  padding: 40px 36px; width: 100%; max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,.3);
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-ico { font-size: 52px; margin-bottom: 10px; }
.login-brand { font-size: 24px; font-weight: 800; color: var(--br); letter-spacing: 4px; }
.login-sub { font-size: 12px; color: var(--gy); letter-spacing: 2px; margin-top: 4px; }
.login-form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12px; font-weight: 700; color: var(--gy); text-transform: uppercase; letter-spacing: 1px; }
.field input {
  border: 1.5px solid var(--gyl); border-radius: 10px;
  padding: 12px 14px; font-size: 14px; color: var(--br);
  outline: none; transition: border-color .2s;
}
.field input:focus { border-color: var(--gd); }
.erro { background: var(--rdl); color: var(--rd); border-radius: 8px; padding: 10px 12px; font-size: 13px; }
.btn-login {
  background: var(--gd); color: var(--br); border: none;
  border-radius: 12px; padding: 14px; font-size: 15px;
  font-weight: 800; cursor: pointer; transition: background-color .2s;
  margin-top: 4px;
}
.btn-login:hover:not(:disabled) { background: var(--gdk); }
.btn-login:focus-visible { outline: 3px solid var(--br3); outline-offset: 2px; }
.btn-login:disabled { opacity: .6; cursor: not-allowed; }
.login-hint { margin-top: 20px; text-align: center; font-size: 12px; color: var(--gy); }
.login-hint code {
  background: var(--gyl); border-radius: 4px;
  padding: 2px 6px; color: var(--br2); display: block;
  margin-top: 4px;
}
@media (max-width: 420px) {
  .login-card { padding: 32px 22px; }
}
</style>