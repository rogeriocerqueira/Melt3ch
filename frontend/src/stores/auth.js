import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { TOKEN_KEY, login as apiLogin } from '../api'
import router from '../router'

function lerToken() {
  try { return localStorage.getItem(TOKEN_KEY) || '' } catch { return '' }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(lerToken())
  const logado = computed(() => !!token.value)

  /** Faz login e leva para a página pedida antes (ou o painel). Lança erro se falhar. */
  async function entrar(email, senha, destino = '/dashboard') {
    const { data } = await apiLogin(email, senha)
    token.value = data.access_token
    localStorage.setItem(TOKEN_KEY, data.access_token)
    await router.push(destino)
  }

  function sair() {
    token.value = ''
    localStorage.removeItem(TOKEN_KEY)
    if (router.currentRoute.value.meta.auth) router.push('/login')
  }

  return { token, logado, entrar, sair }
})