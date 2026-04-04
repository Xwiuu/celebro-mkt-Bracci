import { createRouter, createWebHistory } from 'vue-router'
import ClientDashboard from '../views/ClientDashboard.vue'
import CelebroBunker from '../views/CelebroBunker.vue'
import ComparativeView from '../views/ComparativeView.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: ClientDashboard },
  { path: '/celebro', component: CelebroBunker },
  { path: '/comparativo', component: ComparativeView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
