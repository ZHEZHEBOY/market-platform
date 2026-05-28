<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { placeOrder } from '../api/order'
import { getMyCoupons } from '../api/coupon'
import api from '../api/index'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const addresses = ref([])
const selectedAddrId = ref(null)
const coupons = ref([])
const selectedCouponId = ref(null)

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

// 计算优惠金额
const discountAmount = computed(() => {
  if (!selectedCouponId.value) return 0
  const coupon = coupons.value.find(c => c.id === selectedCouponId.value)
  if (!coupon) return 0
  return calculateDiscount(coupon, totalAmount.value)
})

// 实付金额
const payAmount = computed(() => {
  return Math.max(0, totalAmount.value - discountAmount.value)
})

function calculateDiscount(coupon, amount) {
  if (amount < coupon.coupon.min_amount) return 0
  if (coupon.coupon.coupon_type === 'fixed') {
    return Math.min(coupon.coupon.value, amount)
  } else {
    let discount = Math.floor(amount * coupon.coupon.value / 100)
    if (coupon.coupon.max_discount) {
      discount = Math.min(discount, coupon.coupon.max_discount)
    }
    return discount
  }
}

async function fetchAddresses() {
  const { data } = await api.get('/api/addresses')
  addresses.value = data
  const def = data.find(a => a.is_default)
  if (def) selectedAddrId.value = def.id
  else if (data.length) selectedAddrId.value = data[0].id
}

async function fetchCoupons() {
  try {
    const { data } = await getMyCoupons('active')
    // 过滤满足条件的优惠券
    coupons.value = data.filter(c => {
      return totalAmount.value >= c.coupon.min_amount
    })
  } catch {}
}

async function submitOrder() {
  if (!selectedAddrId.value) {
    ElMessage.error('请选择收货地址')
    return
  }
  try {
    const payload = {
      address_id: selectedAddrId.value,
      cart_item_ids: cartItemIds.value,
    }
    if (selectedCouponId.value) {
      payload.coupon_id = selectedCouponId.value
    }
    const { data } = await placeOrder(payload)
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
  fetchCoupons()
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
    </el-card>

    <el-card class="section" v-if="coupons.length">
      <template #header>优惠券</template>
      <el-radio-group v-model="selectedCouponId">
        <div class="coupon-option">
          <el-radio :value="null">不使用优惠券</el-radio>
        </div>
        <div v-for="c in coupons" :key="c.id" class="coupon-option">
          <el-radio :value="c.id">
            <span class="coupon-name">{{ c.coupon.name }}</span>
            <span class="coupon-desc">
              {{ c.coupon.coupon_type === 'fixed' ? '减¥' + (c.coupon.value / 100).toFixed(0) : c.coupon.value + '折' }}
              {{ c.coupon.min_amount > 0 ? '（满' + (c.coupon.min_amount / 100).toFixed(0) + '可用）' : '' }}
            </span>
          </el-radio>
        </div>
      </el-radio-group>
    </el-card>

    <el-card class="section">
      <template #header>订单金额</template>
      <div class="amount-row">
        <span>商品金额</span>
        <span>¥{{ (totalAmount / 100).toFixed(2) }}</span>
      </div>
      <div class="amount-row discount" v-if="discountAmount > 0">
        <span>优惠券抵扣</span>
        <span>-¥{{ (discountAmount / 100).toFixed(2) }}</span>
      </div>
      <div class="amount-row total">
        <span>实付金额</span>
        <span class="pay-amount">¥{{ (payAmount / 100).toFixed(2) }}</span>
      </div>
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

.coupon-option { padding: 8px 0; }
.coupon-name { font-weight: bold; margin-right: 8px; }
.coupon-desc { color: #666; font-size: 13px; }

.amount-row { display: flex; justify-content: space-between; padding: 8px 0; }
.amount-row.discount { color: #67c23a; }
.amount-row.total { border-top: 1px solid #eee; margin-top: 8px; padding-top: 12px; font-size: 16px; font-weight: bold; }
.pay-amount { color: #e4393c; font-size: 20px; }

.actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
</style>
