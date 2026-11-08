import axios from 'axios'

export const TOKEN_KEY = 'melt3ch_token'

// Sem VITE_API_URL, as chamadas vão para o mesmo endereço do site (/api/...),
// que o Vite (dev) ou o nginx (produção) repassam para o backend.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 10000,
})

// Injeta o token JWT nas requisições
api.interceptors.request.use(config => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Chamado quando a API responde 401 (token expirado/inválido). Registrado em main.js.
let aoExpirarSessao = () => {}
export function onSessaoExpirada(fn) { aoExpirarSessao = fn }

api.interceptors.response.use(
  res => res,
  err => {
    const ehLogin = err.config?.url?.includes('/api/auth/login')
    if (err.response?.status === 401 && !ehLogin) aoExpirarSessao()
    return Promise.reject(err)
  },
)

// Auth
export const login = (email, senha) => api.post('/api/auth/login', { email, senha })

// Painel e colmeias
export const getDashboard = () => api.get('/api/dashboard')
export const getHistorico = (codigo, limite = 48) =>
  api.get(`/api/iot/colmeia/${encodeURIComponent(codigo)}/historico`, { params: { limite } })

// Lotes
export const getLotes = () => api.get('/api/lotes')
export const getQR = (codigo) => api.get(`/api/lotes/${encodeURIComponent(codigo)}/qr`)

// Rastreio público (QR code do consumidor)
export const getRastreio = (codigo) => api.get(`/api/rastreio/${encodeURIComponent(codigo)}`)

export default api