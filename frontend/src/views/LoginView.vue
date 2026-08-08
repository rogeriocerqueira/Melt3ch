<template>
  <div class="login-bg">
    <div class="login-card">
      <div class="login-header">
        <div class="login-ico">🍯</div>
        <div class="login-brand">MEL IGAPÓ</div>
        <div class="login-sub">MelT3ch Platform</div>
      </div>

      <form @submit.prevent="entrar" class="login-form">
        <div class="field">
          <label>E-mail</label>
          <input v-model="email" type="email" placeholder="daiane@melt3ch.com" required />
        </div>
        <div class="field">
          <label>Senha</label>
          <input v-model="senha" type="password" placeholder="••••••••" required />
        </div>
        <div v-if="erro" class="erro">{{ erro }}</div>
        <button type="submit" :disabled="carregando" class="btn-login">
          {{ carregando ? 'Entrando...' : 'Entrar na plataforma' }}
        </button>
      </form>

      <div class="login-hint">
        <span>MVP Demo: </span>
        <code>daiane@melt3ch.com / melt3ch2026</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const email = ref('daiane@melt3ch.com')
const senha = ref('melt3ch2026')
const erro = ref('')
const carregando = ref(false)

async function entrar() {
  erro.value = ''
  carregando.value = true
  try {
    await auth.entrar(email.value, senha.value)
  } catch (e) {
    erro.value = 'E-mail ou senha incorretos'
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
  outline: none; transition: border .2s;
}
.field input:focus { border-color: var(--gd); }
.erro { background: var(--rdl); color: var(--rd); border-radius: 8px; padding: 10px 12px; font-size: 13px; }
.btn-login {
  background: var(--gd); color: var(--br); border: none;
  border-radius: 12px; padding: 14px; font-size: 15px;
  font-weight: 800; cursor: pointer; transition: all .2s;
  margin-top: 4px;
}
.btn-login:hover { background: var(--gdk); }
.btn-login:disabled { opacity: .6; cursor: not-allowed; }
.login-hint {
  margin-top: 20px; text-align: center;
  font-size: 12px; color: var(--gy);
}
.login-hint code {
  background: var(--gyl); border-radius: 4px;
  padding: 2px 6px; color: var(--br2); display: block;
  margin-top: 4px;
}
</style>
