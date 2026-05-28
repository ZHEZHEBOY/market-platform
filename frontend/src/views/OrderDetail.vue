<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrder, cancelOrder, payOrder } from '../api/order'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const order = ref(null)
const loading = ref(true)

const statusMap = {
  pending_payment: { label: '待支付', color: '#E6A23C' },
  paid: { label: '已支付', color: '#409EFF' },
  shipped: { label: '已发货', color: '#67C23A' },
  signed: { label: '已签收', color: '#909399' },
  cancelled: { label: '已取消', color: '#F56C6C' },
}

const stepMap = { pending_payment: 0, paid: 1, shipped: 2, signed: 3 }
const currentStep = computed(() => order.value ? (stepMap[order.value.status] ?? -1) : -1)

async function fetchOrder() {
  loading.value = true
  try {
    const { data } = await getOrder(route.params.id)
    order.value = data
  } catch {
    ElMessage.error('订单不存在')
    router.push('/orders')
  } finally {
    loading.value = false
  }
}

async function handlePay() {
  const { data } = await payOrder(order.value.id)
  window.open(data.pay_url, '_blank')
}

async function handleCancel() {
  await cancelOrder(order.value.id)
  ElMessage.success('已取消')
  fetchOrder()
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="order-detail-page" v-loading="loading">
    <div class="container" v-if="order">
      <!-- Status Header -->
      <div class="status-header" :style="{ borderColor: statusMap[order.status]?.color }">
        <div class="status-info">
          <span class="status-badge" :style="{ background: statusMap[order.status]?.color }">
            {{ statusMap[order.status]?.label }}
          </span>
          <span class="order-no">订单号：{{ order.order_no }}</span>
        </div>
        <div class="status-actions">
          <el-button v-if="order.status === 'pending_payment'" type="primary" @click="handlePay">去支付</el-button>
          <el-button v-if="order.status === 'pending_payment'" type="danger" plain @click="handleCancel">取消订单</el-button>
          <el-button @click="router.push('/orders')">返回订单列表</el-button>
        </div>
      </div>

      <!-- Timeline -->
      <div class="timeline-card">
        <h3>订单状态</h3>
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="提交订单" :description="formatTime(order.created_at)" />
          <el-step title="付款成功" :description="order.paid_at ? formatTime(order.paid_at) : '等待支付'" />
          <el-step title="已发货" :description="order.status === 'shipped' || order.status === 'signed' ? '商家已发货' : '等待发货'" />
          <el-step title="已签收" :description="order.status === 'signed' ? '已签收' : '等待签收'" />
        </el-steps>
      </div>

      <!-- Products -->
      <div class="products-card">
        <h3>商品信息</h3>
        <div class="product-list">
          <div v-for="item in order.items" :key="item.id" class="product-item">
            <div class="product-img">
              <div class="img-placeholder">{{ item.product_name?.[0] || '?' }}</div>
            </div>
            <div class="product-info">
              <h4>{{ item.product_name }}</h4>
              <p class="product-price">¥{{ (item.price_at_time / 100).toFixed(2) }} x {{ item.quantity }}</p>
            </div>
            <div class="product-subtotal">
              ¥{{ ((item.price_at_time * item.quantity) / 100).toFixed(2) }}
            </div>
          </div>
        </div>
        <div class="total-row">
          <span>共 {{ order.items?.length || 0 }} 件商品</span>
          <span class="total-label">合计：<em>¥{{ (order.total_amount / 100).toFixed(2) }}</em></span>
        </div>
      </div>

      <!-- Address -->
      <div class="info-cards">
        <div class="info-card">
          <h3>收货地址</h3>
          <div v-if="order.address_snapshot" class="info-content">
            <p><strong>{{ order.address_snapshot.receiver_name }}</strong> {{ order.address_snapshot.phone }}</p>
            <p>{{ order.address_snapshot.province }}{{ order.address_snapshot.city }}{{ order.address_snapshot.district }}{{ order.address_snapshot.detail }}</p>
          </div>
        </div>
        <div class="info-card">
          <h3>订单信息</h3>
          <div class="info-content">
            <p>订单号：{{ order.order_no }}</p>
            <p>下单时间：{{ formatTime(order.created_at) }}</p>
            <p v-if="order.paid_at">支付时间：{{ formatTime(order.paid_at) }}</p>
            <p>订单状态：{{ statusMap[order.status]?.label }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-detail-page {
  padding: 24px 0;
  min-height: 80vh;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.status-header {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 24px 28px;
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-left: 4px solid;
  margin-bottom: 20px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-badge {
  padding: 4px 14px;
  border-radius: 20px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
}

.order-no {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.status-actions {
  display: flex;
  gap: 8px;
}

.timeline-card,
.products-card,
.info-card {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 24px 28px;
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.timeline-card h3,
.products-card h3,
.info-card h3 {
  margin: 0 0 20px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.product-item:last-child {
  border-bottom: none;
}

.product-img {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.img-placeholder {
  width: 100%;
  height: 100%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #ccc;
}

.product-info {
  flex: 1;
}

.product-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 500;
}

.product-price {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.product-subtotal {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
  font-size: 14px;
  color: var(--color-text-secondary);
}

.total-label em {
  font-style: normal;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-price);
}

.info-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-content p {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.info-content strong {
  color: var(--color-text);
}
</style>
