import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin } from '../api'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('melt3ch_token') || '')
  const logado = ref(!!token.value)

  async function entrar(email, senha) {
    const { data } = await apiLogin(email, senha)
    token.value = data.access_token
    logado.value = true
    localStorage.setItem('melt3ch_token', data.access_token)
    router.push('/dashboard')
  }

  function sair() {
    token.value = ''
    logado.value = false
    localStorage.removeItem('melt3ch_token')
    router.push('/login')
  }

  return { token, logado, entrar, sair }
})
