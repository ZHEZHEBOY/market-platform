<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { placeOrder } from '../api/order'
import api from '../api/index'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const addresses = ref([])
const selectedAddrId = ref(null)

const cartItemIds = computed(() => {
  const ids = route.query.ids
  return ids ? ids.split(',').map(Number) : []
})

const selectedItems = computed(() =>
  cartStore.items.filter(i => cartItemIds.value.includes(i.id))
)

const totalAmount = computed(() =>
  selectedItems.value.reduce((s, i) => s + i.price * i.quantity, 0)
)

async function fetchAddresses() {
  const { data } = await api.get('/api/addresses')
  addresses.value = data
  const def = data.find(a => a.is_default)
  if (def) selectedAddrId.value = def.id
  else if (data.length) selectedAddrId.value = data[0].id
}

async function submitOrder() {
  if (!selectedAddrId.value) {
    ElMessage.error('请选择收货地址')
    return
  }
  try {
    const { data } = await placeOrder({
      address_id: selectedAddrId.value,
      cart_item_ids: cartItemIds.value,
    })
    ElMessage.success('下单成功')
    cartStore.fetchCart()
    router.push(`/orders`)
  } catch {
    // error handled by interceptor
  }
}

onMounted(() => {
  cartStore.fetchCart()
  fetchAddresses()
})
</script>

<template>
  <div class="checkout">
    <h2>确认订单</h2>

    <el-card class="section">
      <template #header>收货地址</template>
      <el-radio-group v-model="selectedAddrId">
        <div v-for="a in addresses" :key="a.id" class="addr-option">
          <el-radio :value="a.id">
            <span class="addr-name">{{ a.receiver_name }}</span>
            <span class="addr-phone">{{ a.phone }}</span>
            <span class="addr-detail">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</span>
            <el-tag v-if="a.is_default" size="small" type="danger">默认</el-tag>
          </el-radio>
        </div>
      </el-radio-group>
    </el-card>

    <el-card class="section">
      <template #header>商品清单</template>
      <div v-for="item in selectedItems" :key="item.id" class="order-item">
        <span>{{ item.product_name }} x{{ item.quantity }}</span>
        <span class="price">¥{{ ((item.price * item.quantity) / 100).toFixed(2) }}</span>
      </div>
      <div class="total">合计: ¥{{ (totalAmount / 100).toFixed(2) }}</div>
    </el-card>

    <div class="actions">
      <el-button @click="router.back()">返回</el-button>
      <el-button type="primary" size="large" @click="submitOrder" :disabled="!cartItemIds.length">
        提交订单
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.checkout { padding: 20px; max-width: 700px; margin: 0 auto; }
.section { margin-bottom: 16px; }
.addr-option { padding: 8px 0; }
.addr-name { font-weight: bold; margin-right: 12px; }
.addr-phone { color: #666; margin-right: 12px; }
.addr-detail { color: #999; }
.order-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
.price { color: #e4393c; font-weight: bold; }
.total { text-align: right; font-size: 20px; font-weight: bold; margin-top: 12px; }
.actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
</style>
