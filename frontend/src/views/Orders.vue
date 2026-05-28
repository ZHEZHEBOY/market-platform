<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrders, cancelOrder, payOrder, queryPayment } from '../api/order'
import { ElMessage } from 'element-plus'

const router = useRouter()
const orders = ref([])
const total = ref(0)
const page = ref(1)
const status = ref('')
const loading = ref(false)

async function fetchOrders() {
  loading.value = true
  const { data } = await getOrders({ page: page.value, page_size: 10, status: status.value })
  orders.value = data.items
  total.value = data.total
  loading.value = false
}

async function handleCancel(id) {
  await cancelOrder(id)
  ElMessage.success('已取消')
  fetchOrders()
}

async function handlePay(id) {
  const { data } = await payOrder(id)
  window.open(data.pay_url, '_blank')
}

async function handleQuery(id) {
  const { data } = await queryPayment(id)
  if (data.paid) {
    ElMessage.success('支付成功')
    fetchOrders()
  } else {
    ElMessage.info('未支付或支付处理中')
  }
}

function goToDetail(id) {
  router.push(`/order/${id}`)
}

const statusMap = {
  pending_payment: '待支付',
  paid: '已支付',
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

onMounted(fetchOrders)
</script>

<template>
  <div class="orders-page">
    <div class="container">
      <h2>我的订单</h2>
      <el-radio-group v-model="status" @change="page=1;fetchOrders()">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="pending_payment">待支付</el-radio-button>
        <el-radio-button value="paid">已支付</el-radio-button>
        <el-radio-button value="shipped">已发货</el-radio-button>
      </el-radio-group>

      <div class="orders-list" v-loading="loading">
        <div v-for="order in orders" :key="order.id" class="order-card" @click="goToDetail(order.id)">
          <div class="order-header">
            <span class="order-no">{{ order.order_no }}</span>
            <span class="order-status" :style="{ color: statusColorMap[order.status] }">{{ statusMap[order.status] }}</span>
          </div>
          <div class="order-body">
            <div class="order-items-preview">
              <span v-for="(item, i) in (order.items || []).slice(0, 3)" :key="i" class="item-tag">
                {{ item.product_name }} x{{ item.quantity }}
              </span>
              <span v-if="(order.items || []).length > 3" class="item-more">等 {{ order.items.length }} 件商品</span>
            </div>
            <div class="order-meta">
              <span class="order-time">{{ new Date(order.created_at).toLocaleString('zh-CN') }}</span>
              <span class="order-amount">¥{{ (order.total_amount / 100).toFixed(2) }}</span>
            </div>
          </div>
          <div class="order-actions" @click.stop>
            <el-button v-if="order.status==='pending_payment'" size="small" type="primary" @click="handlePay(order.id)">去支付</el-button>
            <el-button v-if="order.status==='pending_payment'" size="small" type="danger" plain @click="handleCancel(order.id)">取消</el-button>
            <el-button size="small" plain @click="goToDetail(order.id)">查看详情</el-button>
          </div>
        </div>

        <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
      </div>

      <div class="pagination" v-if="total > 10">
        <el-pagination v-model:current-page="page" :page-size="10" :total="total" layout="prev, pager, next" background @current-change="fetchOrders" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-page {
  padding: 24px 0;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

h2 {
  margin: 0 0 20px;
  font-size: 22px;
  font-weight: 600;
}

.orders-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 20px 24px;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.order-card:hover {
  box-shadow: var(--shadow-card-hover);
}

.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.order-no {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.order-status {
  font-size: 14px;
  font-weight: 600;
}

.order-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.order-items-preview {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.item-tag {
  padding: 2px 10px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.item-more {
  font-size: 12px;
  color: var(--color-text-light);
}

.order-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.order-time {
  font-size: 12px;
  color: var(--color-text-light);
}

.order-amount {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-price);
}

.order-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
