import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login',           component: () => import('../views/LoginView.vue') },
  { path: '/dashboard',       component: () => import('../views/DashboardView.vue'), meta: { auth: true } },
  { path: '/lotes',           component: () => import('../views/LotesView.vue'),     meta: { auth: true } },
  { path: '/rastreio/:codigo',component: () => import('../views/RastreioView.vue') },
  { path: '/',                redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('melt3ch_token')
  if (to.meta.auth && !token) return '/login'
})

export default router
