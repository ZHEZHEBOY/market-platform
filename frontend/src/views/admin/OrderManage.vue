<script setup>
import { ref, onMounted } from 'vue'
import { adminListOrders, shipOrder } from '../../api/admin'
import { ElMessage } from 'element-plus'

const orders = ref([])
const total = ref(0)
const page = ref(1)
const status = ref('')

async function fetchOrders() {
  const { data } = await adminListOrders({ page: page.value, page_size: 10, status: status.value })
  orders.value = data.items; total.value = data.total
}

async function ship(id) {
  await shipOrder(id)
  ElMessage.success('已发货')
  fetchOrders()
}

const statusMap = { pending_payment: '待支付', paid: '已支付', shipped: '已发货', signed: '已签收', cancelled: '已取消' }

onMounted(fetchOrders)
</script>
<template>
  <div class="order-manage">
    <h2>订单管理</h2>
    <el-radio-group v-model="status" @change="page=1;fetchOrders()">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="paid">已支付</el-radio-button>
      <el-radio-button value="shipped">已发货</el-radio-button>
    </el-radio-group>

    <el-table :data="orders" style="margin-top:20px">
      <el-table-column prop="order_no" label="订单号" width="200" />
      <el-table-column label="金额"><template #default="{row}">¥{{ (row.total_amount/100).toFixed(2) }}</template></el-table-column>
      <el-table-column label="状态"><template #default="{row}">{{ statusMap[row.status] }}</template></el-table-column>
      <el-table-column label="收货人"><template #default="{row}">{{ row.address_snapshot?.receiver_name }}</template></el-table-column>
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{row}">
          <el-button v-if="row.status==='paid'" size="small" type="success" @click="ship(row.id)">发货</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
<style scoped>
.order-manage { padding: 20px; max-width: 1100px; margin: 0 auto; }
</style>
