<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useCartStore } from '../stores/cart'
import { onMounted, computed, ref } from 'vue'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

const cartCount = computed(() => cartStore.items.reduce((s, i) => s + i.quantity, 0))
const searchKeyword = ref('')

onMounted(() => {
  if (userStore.token) {
    cartStore.fetchCart()
  }
})

function handleSearch() {
  const kw = searchKeyword.value.trim()
  if (kw) {
    router.push({ path: '/search', query: { keyword: kw } })
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="logo">Market</router-link>

      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品"
          @keyup.enter="handleSearch"
          clearable
          class="search-input"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>

      <div class="nav-actions">
        <router-link to="/cart" class="action-item cart-link" v-if="!userStore.isSeller || userStore.isAdmin">
          <el-badge :value="cartCount" :hidden="!cartCount" :max="99">
            <el-icon :size="22"><ShoppingCart /></el-icon>
          </el-badge>
          <span class="action-text">购物车</span>
        </router-link>

        <template v-if="userStore.isLoggedIn">
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar || ''">
                {{ userStore.user?.username?.[0]?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="router.push('/orders')" v-if="userStore.isBuyer || userStore.isAdmin">我的订单</el-dropdown-item>
                <el-dropdown-item @click="router.push('/favorites')" v-if="userStore.isBuyer || userStore.isAdmin">我的收藏</el-dropdown-item>
                <el-dropdown-item @click="router.push('/address')" v-if="userStore.isBuyer || userStore.isAdmin">收货地址</el-dropdown-item>
                <el-dropdown-item v-if="userStore.isSeller" @click="router.push('/seller')">卖家中心</el-dropdown-item>
                <el-dropdown-item v-if="userStore.isAdmin" @click="router.push('/admin')">后台管理</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <template v-else>
          <router-link to="/login" class="action-item">
            <span class="action-text">登录</span>
          </router-link>
          <router-link to="/register" class="action-item">
            <span class="action-text">注册</span>
          </router-link>
        </template>
      </div>
    </div>
  </header>
  <div class="navbar-placeholder"></div>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--color-bg-white);
  border-bottom: 1px solid var(--color-border);
  z-index: 1000;
}

.navbar-inner {
  max-width: 1240px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 40px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
  flex-shrink: 0;
}

.search-box {
  flex: 1;
  max-width: 480px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-input);
  box-shadow: 0 0 0 1px var(--color-border);
}

.search-input :deep(.el-input-group__append) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  border-radius: 0 var(--radius-input) var(--radius-input) 0;
}

.search-input :deep(.el-input-group__append .el-button) {
  color: #fff;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-shrink: 0;
  margin-left: auto;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s;
}

.action-item:hover {
  color: var(--color-primary);
}

.action-text {
  font-size: 14px;
}

.cart-link {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: var(--color-text);
}

.navbar-placeholder {
  height: var(--header-height);
}
</style>
