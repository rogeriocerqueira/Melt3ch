import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

// Injeta token JWT em todas as requisições autenticadas
api.interceptors.request.use(config => {
  const token = localStorage.getItem('melt3ch_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auth
export const login = (email, senha) =>
  api.post('/api/auth/login', { email, senha })

// Dashboard e colmeias
export const getDashboard = () => api.get('/api/dashboard')
export const getLotes = () => api.get('/api/lotes')
export const getQR = (codigo) => api.get(`/api/lotes/${codigo}/qr`)
export const getHistorico = (codigo) => api.get(`/api/iot/colmeia/${codigo}/historico`)

// Rastreio público (QR code do consumidor)
export const getRastreio = (codigo) => api.get(`/api/rastreio/${codigo}`)

export default api
