<script setup>
import { ref, onMounted } from 'vue'
import { getMyOrders, shipMyOrder } from '../../api/seller'
import { ElMessage } from 'element-plus'

const orders = ref([])
const total = ref(0)
const page = ref(1)
const status = ref('')
const loading = ref(false)

const statusMap = {
  pending_payment: '待支付',
  paid: '待发货',
  shipped: '已发货',
  signed: '已签收',
  cancelled: '已取消',
}
const statusColorMap = {
  pending_payment: '#E6A23C',
  paid: '#409EFF',
  shipped: '#67C23A',
  signed: '#909399',
  cancelled: '#F56C6C',
}

async function fetchOrders() {
  loading.value = true
  try {
    const { data } = await getMyOrders({ page: page.value, page_size: 20, status: status.value })
    orders.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function handleShip(orderId) {
  await shipMyOrder(orderId)
  ElMessage.success('已发货')
  fetchOrders()
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(fetchOrders)
</script>

<template>
  <div class="seller-orders">
    <h2>订单管理</h2>

    <el-radio-group v-model="status" @change="page=1;fetchOrders()">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="paid">待发货</el-radio-button>
      <el-radio-button value="shipped">已发货</el-radio-button>
    </el-radio-group>

    <div class="orders-list" v-loading="loading">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="order-no">订单号：{{ order.order_no }}</span>
          <span class="order-status" :style="{ color: statusColorMap[order.status] }">{{ statusMap[order.status] }}</span>
        </div>
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <span class="item-name">{{ item.product_name }}</span>
            <span class="item-qty">x{{ item.quantity }}</span>
            <span class="item-price">¥{{ (item.price_at_time / 100).toFixed(2) }}</span>
          </div>
        </div>
        <div class="order-footer">
          <span class="order-time">{{ formatTime(order.created_at) }}</span>
          <div class="order-actions">
            <span class="order-amount">合计：¥{{ (order.total_amount / 100).toFixed(2) }}</span>
            <el-button v-if="order.status === 'paid'" type="primary" size="small" @click="handleShip(order.id)">发货</el-button>
          </div>
        </div>
        <div v-if="order.address_snapshot" class="order-address">
          <el-icon><Location /></el-icon>
          {{ order.address_snapshot.receiver_name }} {{ order.address_snapshot.phone }}，
          {{ order.address_snapshot.province }}{{ order.address_snapshot.city }}{{ order.address_snapshot.district }}{{ order.address_snapshot.detail }}
        </div>
      </div>

      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
    </div>

    <div class="pagination" v-if="total > 20">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchOrders" />
    </div>
  </div>
</template>

<style scoped>
.seller-orders h2 { margin: 0 0 20px; font-size: 20px; }
.orders-list { margin-top: 20px; display: flex; flex-direction: column; gap: 12px; }
.order-card { background: var(--color-bg-white); border-radius: var(--radius-card); padding: 20px; box-shadow: var(--shadow-card); }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.order-no { font-size: 13px; color: var(--color-text-secondary); }
.order-status { font-size: 14px; font-weight: 600; }
.order-items { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.order-item { display: flex; align-items: center; gap: 12px; font-size: 14px; }
.item-name { flex: 1; }
.item-qty { color: var(--color-text-secondary); }
.item-price { font-weight: 500; }
.order-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f5f5f5; }
.order-time { font-size: 12px; color: var(--color-text-light); }
.order-actions { display: flex; align-items: center; gap: 12px; }
.order-amount { font-size: 16px; font-weight: 600; color: var(--color-price); }
.order-address { margin-top: 12px; padding: 10px 14px; background: #fafafa; border-radius: 8px; font-size: 13px; color: var(--color-text-secondary); display: flex; align-items: center; gap: 6px; }
.pagination { display: flex; justify-content: center; margin-top: 24px; }
</style>
