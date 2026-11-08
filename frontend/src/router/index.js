import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// meta.auth   → exige login
// meta.hideNav → página sem a navbar administrativa (login e rastreio público)
const routes = [
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { hideNav: true, title: 'Entrar' } },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue'), meta: { auth: true, title: 'Painel IoT' } },
  { path: '/lotes', component: () => import('../views/LotesView.vue'), meta: { auth: true, title: 'Lotes' } },
  { path: '/rastreio/:codigo', component: () => import('../views/RastreioView.vue'), meta: { hideNav: true, title: 'Rastreio' } },
  { path: '/', redirect: '/dashboard' },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.logado) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && auth.logado) return '/dashboard'
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · MelT3ch` : 'MelT3ch — Mel Igapó'
})

export default router