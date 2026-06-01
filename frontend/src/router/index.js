import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ── 买家端 ──
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
    path: '/register/seller',
    component: () => import('../views/RegisterSeller.vue'),
  },
  {
    path: '/search',
    component: () => import('../views/SearchResults.vue'),
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
    path: '/order/:id',
    component: () => import('../views/OrderDetail.vue'),
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
    path: '/profile',
    component: () => import('../views/Profile.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/favorites',
    component: () => import('../views/Favorites.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/coupons',
    component: () => import('../views/CouponCenter.vue'),
  },
  {
    path: '/my-coupons',
    component: () => import('../views/MyCoupons.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/my-refunds',
    component: () => import('../views/MyRefunds.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/notifications',
    component: () => import('../views/Notifications.vue'),
    meta: { requireAuth: true },
  },

  // ── 卖家端 ──
  {
    path: '/seller',
    component: () => import('../views/seller/SellerLayout.vue'),
    meta: { requireAuth: true, requireSeller: true },
    children: [
      { path: '', component: () => import('../views/seller/SellerDashboard.vue') },
      { path: 'products', component: () => import('../views/seller/SellerProducts.vue') },
      { path: 'orders', component: () => import('../views/seller/SellerOrders.vue') },
      { path: 'shop', component: () => import('../views/seller/SellerShop.vue') },
    ],
  },

  // ── 管理端 ──
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
  {
    path: '/admin/shops',
    component: () => import('../views/admin/ShopManage.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
  {
    path: '/admin/categories',
    component: () => import('../views/admin/CategoryManage.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
  {
    path: '/admin/coupons',
    component: () => import('../views/admin/CouponManage.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
  {
    path: '/admin/refunds',
    component: () => import('../views/admin/RefundManage.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },
  {
    path: '/admin/analytics',
    component: () => import('../views/admin/Analytics.vue'),
    meta: { requireAuth: true, requireAdmin: true },
  },

  // ── 404 兜底 ──
  {
    path: '/:pathMatch(.*)*',
    component: () => import('../views/NotFound.vue'),
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
  if (to.meta.requireSeller && user.role !== 'seller') {
    return next('/')
  }
  next()
})

export default router
