<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const cartStore = useCartStore()
const checkedIds = ref([])

onMounted(() => cartStore.fetchCart())

function goCheckout() {
  if (!checkedIds.value.length) {
    ElMessageBox.alert('请选择要结算的商品')
    return
  }
  router.push({ path: '/checkout', query: { ids: checkedIds.value.join(',') } })
}
</script>

<template>
  <div class="cart-page">
    <h2>购物车</h2>
    <el-empty v-if="!cartStore.items.length" description="购物车是空的" />
    <template v-else>
      <el-checkbox-group v-model="checkedIds">
        <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <el-checkbox :value="item.id" />
          <span>{{ item.product_name }}</span>
          <span class="price">¥{{ (item.price / 100).toFixed(2) }}</span>
          <el-input-number :model-value="item.quantity" :min="1" :max="item.stock" size="small" @update:model-value="cartStore.update(item.id, $event)" />
          <span>小计: ¥{{ ((item.price * item.quantity) / 100).toFixed(2) }}</span>
          <el-button size="small" type="danger" @click="cartStore.remove(item.id)">删除</el-button>
        </div>
      </el-checkbox-group>
      <div class="cart-footer">
        <span>合计: ¥{{ (cartStore.totalAmount / 100).toFixed(2) }}</span>
        <el-button type="primary" size="large" @click="goCheckout">去结算</el-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cart-page { padding: 20px; max-width: 800px; margin: 0 auto; }
.cart-item { display: flex; align-items: center; gap: 16px; padding: 12px 0; border-bottom: 1px solid #eee; }
.price { color: #e4393c; font-weight: bold; }
.cart-footer { display: flex; justify-content: flex-end; align-items: center; gap: 20px; margin-top: 20px; font-size: 18px; }
</style>
