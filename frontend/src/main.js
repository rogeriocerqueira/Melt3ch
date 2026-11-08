import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { onSessaoExpirada } from './api'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// Token expirado ou inválido → sai e volta para o login
onSessaoExpirada(() => useAuthStore().sair())

app.mount('#app')