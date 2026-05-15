<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '../../api/admin'

const data = ref({})
onMounted(async () => {
  const { data: d } = await getDashboard()
  data.value = d
})
</script>
<template>
  <div class="dashboard">
    <h2>后台管理</h2>
    <el-row :gutter="20">
      <el-col :span="6"><el-card><div class="stat-label">今日订单</div><div class="stat-num">{{ data.today_orders }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat-label">今日销售额</div><div class="stat-num">¥{{ ((data.today_revenue||0)/100).toFixed(2) }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat-label">待处理</div><div class="stat-num">{{ data.pending_orders }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat-label">商品数</div><div class="stat-num">{{ data.total_products }}</div></el-card></el-col>
    </el-row>
    <el-button type="primary" style="margin:20px 0 10px" @click="$router.push('/admin/products')">商品管理</el-button>
    <el-button type="primary" style="margin:20px 0 10px" @click="$router.push('/admin/orders')">订单管理</el-button>
  </div>
</template>
<style scoped>
.dashboard { padding: 20px; max-width: 1000px; margin: 0 auto; }
.stat-label { color: #999; font-size: 14px; }
.stat-num { font-size: 28px; font-weight: bold; color: #409eff; margin-top: 8px; }
</style>
