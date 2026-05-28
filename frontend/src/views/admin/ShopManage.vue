<script setup>
import { ref, onMounted } from 'vue'
import { listShops, approveShop, rejectShop } from '../../api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const shops = ref([])
const total = ref(0)
const page = ref(1)
const status = ref('')
const loading = ref(false)

const statusMap = {
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
}

async function fetchShops() {
  loading.value = true
  try {
    const { data } = await listShops({ page: page.value, page_size: 20, status: status.value })
    shops.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function handleApprove(id) {
  await approveShop(id)
  ElMessage.success('已通过审核')
  fetchShops()
}

async function handleReject(id) {
  await ElMessageBox.confirm('确定拒绝该店铺的入驻申请？', '提示', { type: 'warning' })
  await rejectShop(id)
  ElMessage.success('已拒绝')
  fetchShops()
}

onMounted(fetchShops)
</script>

<template>
  <div class="shop-manage">
    <h2>店铺审核</h2>

    <el-radio-group v-model="status" @change="page=1;fetchShops()">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="pending">待审核</el-radio-button>
      <el-radio-button value="approved">已通过</el-radio-button>
      <el-radio-button value="rejected">已拒绝</el-radio-button>
    </el-radio-group>

    <el-table :data="shops" v-loading="loading" style="margin-top: 20px" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="店铺名称" min-width="150" />
      <el-table-column prop="owner_name" label="店主" width="120" />
      <el-table-column prop="owner_email" label="邮箱" min-width="180" />
      <el-table-column label="状态" width="100">
        <template #default="{row}">
          <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="申请时间" width="180">
        <template #default="{row}">{{ row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{row}">
          <el-button v-if="row.status === 'pending'" size="small" type="success" @click="handleApprove(row.id)">通过</el-button>
          <el-button v-if="row.status === 'pending'" size="small" type="danger" plain @click="handleReject(row.id)">拒绝</el-button>
          <span v-if="row.status !== 'pending'">-</span>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination" v-if="total > 20">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchShops" />
    </div>
  </div>
</template>

<style scoped>
.shop-manage { padding: 20px; max-width: 1200px; margin: 0 auto; }
.shop-manage h2 { margin: 0 0 20px; font-size: 22px; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }
</style>
