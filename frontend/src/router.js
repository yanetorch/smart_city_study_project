import { createRouter, createWebHistory } from 'vue-router'
import { auth } from './store'

const routes = [
  { path: '/', redirect: '/vehicles' },
  { path: '/login', component: () => import('./views/LoginView.vue'), meta: { public: true } },
  { path: '/register', component: () => import('./views/RegisterView.vue'), meta: { public: true } },
  { path: '/profile', component: () => import('./views/ProfileView.vue') },
  { path: '/users/:id', component: () => import('./views/UserDetailView.vue') },
  { path: '/vehicles', component: () => import('./views/VehiclesView.vue') },
  { path: '/parking', component: () => import('./views/ParkingView.vue') },
  { path: '/issues', component: () => import('./views/IssuesView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
  if (to.meta.public && auth.isAuthenticated) return '/profile'
})

export default router