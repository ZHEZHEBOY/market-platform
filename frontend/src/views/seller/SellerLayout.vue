<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => {
  if (route.path === '/seller') return 'dashboard'
  if (route.path.startsWith('/seller/products')) return 'products'
  if (route.path.startsWith('/seller/orders')) return 'orders'
  if (route.path.startsWith('/seller/shop')) return 'shop'
  return 'dashboard'
})

function handleMenu(key) {
  const map = {
    dashboard: '/seller',
    products: '/seller/products',
    orders: '/seller/orders',
    shop: '/seller/shop',
  }
  router.push(map[key])
}
</script>

<template>
  <div class="seller-layout">
    <aside class="seller-sidebar">
      <div class="sidebar-header">
        <h3>卖家中心</h3>
        <p>{{ userStore.user?.username }}</p>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenu">
        <el-menu-item index="dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item index="products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="shop">
          <el-icon><Shop /></el-icon>
          <span>店铺设置</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <el-button text @click="router.push('/')">返回买家端</el-button>
      </div>
    </aside>
    <main class="seller-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.seller-layout {
  display: flex;
  min-height: calc(100vh - var(--header-height));
}

.seller-sidebar {
  width: 220px;
  background: var(--color-bg-white);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-header h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: var(--color-text);
}

.sidebar-header p {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.seller-sidebar .el-menu {
  border-right: none;
  flex: 1;
}

.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--color-border);
}

.seller-main {
  flex: 1;
  padding: 24px;
  background: var(--color-bg);
  overflow-y: auto;
}
</style>
