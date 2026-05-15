<script setup>
import { ref, onMounted } from 'vue'
import { getOrders, cancelOrder, payOrder, queryPayment } from '../api/order'
import { ElMessage } from 'element-plus'

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

const statusMap = {
  pending_payment: '待支付',
  paid: '已支付',
  shipped: '已发货',
  signed: '已签收',
  cancelled: '已取消',
}

onMounted(fetchOrders)
</script>

<template>
  <div class="orders-page">
    <h2>我的订单</h2>
    <el-radio-group v-model="status" @change="page=1;fetchOrders()">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="pending_payment">待支付</el-radio-button>
      <el-radio-button value="paid">已支付</el-radio-button>
      <el-radio-button value="shipped">已发货</el-radio-button>
    </el-radio-group>

    <el-table :data="orders" v-loading="loading" style="margin-top:20px">
      <el-table-column prop="order_no" label="订单号" width="200" />
      <el-table-column label="金额"><template #default="{row}">¥{{ (row.total_amount / 100).toFixed(2) }}</template></el-table-column>
      <el-table-column label="状态"><template #default="{row}">{{ statusMap[row.status] }}</template></el-table-column>
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column label="操作" width="280">
        <template #default="{row}">
          <el-button v-if="row.status==='pending_payment'" size="small" type="success" @click="handlePay(row.id)">支付</el-button>
          <el-button v-if="row.status==='pending_payment'||row.status==='paid'" size="small" type="primary" @click="handleQuery(row.id)">查询状态</el-button>
          <el-button v-if="row.status==='pending_payment'" size="small" type="danger" @click="handleCancel(row.id)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.orders-page { padding: 20px; max-width: 1000px; margin: 0 auto; }
</style>
