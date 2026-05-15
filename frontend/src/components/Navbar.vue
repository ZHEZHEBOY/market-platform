<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useCartStore } from '../stores/cart'
import { onMounted, computed } from 'vue'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

const cartCount = computed(() => cartStore.items.reduce((s, i) => s + i.quantity, 0))

onMounted(() => {
  if (userStore.token) {
    cartStore.fetchCart()
  }
})
</script>

<template>
  <el-menu mode="horizontal" router :ellipsis="false" class="navbar">
    <el-menu-item index="/">
      <span class="logo">Market Platform</span>
    </el-menu-item>
    <div class="flex-grow" />
    <el-menu-item index="/cart">
      🛒 购物车
      <el-badge v-if="cartCount" :value="cartCount" class="cart-badge" />
    </el-menu-item>
    <el-menu-item v-if="!userStore.token" index="/login">登录</el-menu-item>
    <el-menu-item v-if="!userStore.token" index="/register">注册</el-menu-item>
    <el-sub-menu v-if="userStore.token" index="user">
      <template #title>{{ userStore.user?.username }}</template>
      <el-menu-item index="/orders">我的订单</el-menu-item>
      <el-menu-item index="/address">收货地址</el-menu-item>
      <el-menu-item v-if="userStore.isAdmin()" index="/admin">后台管理</el-menu-item>
      <el-menu-item @click="userStore.logout(); router.push('/')">退出</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<style>
.navbar { padding: 0 20px; }
.flex-grow { flex: 1; }
.logo { font-weight: bold; font-size: 18px; color: #409eff; }
.cart-badge { margin-left: 4px; }
</style>
