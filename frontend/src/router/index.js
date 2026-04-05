import { createRouter, createWebHistory } from 'vue-router'
import ClientDashboard from '../views/ClientDashboard.vue'
import ComparativeView from '../views/ComparativeView.vue' // 👈 Importando o comparativo

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: ClientDashboard
    },
    {
      path: '/comparative',
      name: 'comparative',
      component: ComparativeView // 👈 Registrando a rota do comparativo
    },
    {
      path: '/neuro-socio',
      name: 'neuro-socio',
      // Carregamento dinâmico (lazy-loading) para o cérebro
      component: () => import('../views/CelebroBunker.vue') 
    }
  ]
})

export default router