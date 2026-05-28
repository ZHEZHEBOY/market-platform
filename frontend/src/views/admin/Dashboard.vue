<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '../../api/admin'
import { useRouter } from 'vue-router'

const router = useRouter()
const data = ref({})

onMounted(async () => {
  const { data: d } = await getDashboard()
  data.value = d
})
</script>

<template>
  <div class="dashboard">
    <h2>后台管理</h2>

    <div class="stats-grid">
      <el-card>
        <div class="stat-label">今日订单</div>
        <div class="stat-num">{{ data.today_orders || 0 }}</div>
      </el-card>
      <el-card>
        <div class="stat-label">今日销售额</div>
        <div class="stat-num">¥{{ ((data.today_revenue || 0) / 100).toFixed(2) }}</div>
      </el-card>
      <el-card>
        <div class="stat-label">待处理订单</div>
        <div class="stat-num">{{ data.pending_orders || 0 }}</div>
      </el-card>
      <el-card>
        <div class="stat-label">商品总数</div>
        <div class="stat-num">{{ data.total_products || 0 }}</div>
      </el-card>
      <el-card>
        <div class="stat-label">买家数</div>
        <div class="stat-num">{{ data.total_users || 0 }}</div>
      </el-card>
      <el-card>
        <div class="stat-label">卖家数</div>
        <div class="stat-num">{{ data.total_sellers || 0 }}</div>
      </el-card>
      <el-card>
        <div class="stat-label">待审核店铺</div>
        <div class="stat-num" :style="{ color: data.pending_shops > 0 ? '#E6A23C' : undefined }">{{ data.pending_shops || 0 }}</div>
      </el-card>
    </div>

    <div class="quick-links">
      <el-button type="primary" @click="router.push('/admin/products')">商品管理</el-button>
      <el-button type="primary" @click="router.push('/admin/orders')">订单管理</el-button>
      <el-button type="primary" @click="router.push('/admin/shops')">店铺审核</el-button>
      <el-button type="primary" @click="router.push('/admin/categories')">分类管理</el-button>
    </div>
  </div>
</template>

<style scoped>
.dashboard { padding: 20px; max-width: 1200px; margin: 0 auto; }
.dashboard h2 { margin: 0 0 24px; font-size: 22px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-label { color: var(--color-text-secondary); font-size: 14px; }
.stat-num { font-size: 28px; font-weight: bold; color: var(--color-primary); margin-top: 8px; }
.quick-links { display: flex; gap: 12px; }
</style>
