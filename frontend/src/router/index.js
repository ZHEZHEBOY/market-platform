import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/product/:id',
    component: () => import('../views/ProductDetail.vue'),
  },
  {
    path: '/login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/cart',
    component: () => import('../views/Cart.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/checkout',
    component: () => import('../views/Checkout.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/orders',
    component: () => import('../views/Orders.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/pay-result',
    component: () => import('../views/PayResult.vue'),
  },
  {
    path: '/address',
    component: () => import('../views/Address.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/admin',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
  {
    path: '/admin/products',
    component: () => import('../views/admin/ProductManage.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
  {
    path: '/admin/orders',
    component: () => import('../views/admin/OrderManage.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.meta.requireAuth && !token) {
    return next('/login')
  }
  if (to.meta.requireAdmin && user.role !== 'admin') {
    return next('/')
  }
  next()
})

export default router
