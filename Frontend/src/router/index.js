import { createRouter, createWebHistory } from 'vue-router'
import MainComponent from '../components/MainComponent.vue'
import LoginComponent from '../components/LoginComponent.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginComponent,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: MainComponent,
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../components/StatisticsComponent.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/files',
    name: 'Files',
    component: () => import('../components/FilesComponent.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../components/AdminComponent.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // If route requires auth and user is not logged in
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // If route requires admin and user is not admin
  if (to.meta.requiresAdmin && user.role !== 'admin') {
    next('/')
    return
  }

  // If user is logged in and tries to access login page
  if (to.path === '/login' && token) {
    next(user.role === 'admin' ? '/admin' : '/')
    return
  }

  next()
})

export default router 