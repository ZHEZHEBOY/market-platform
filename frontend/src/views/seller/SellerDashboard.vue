<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSellerDashboard, getLowStockProducts } from '../../api/seller'

const router = useRouter()
const stats = ref(null)
const loading = ref(true)
const lowStockProducts = ref([])
const stockThreshold = ref(10)

async function fetchStats() {
  loading.value = true
  try {
    const { data } = await getSellerDashboard()
    stats.value = data
  } finally {
    loading.value = false
  }
}

async function fetchLowStock() {
  try {
    const { data } = await getLowStockProducts(stockThreshold.value)
    lowStockProducts.value = data
  } catch {}
}

function formatMoney(cents) {
  return (cents / 100).toFixed(2)
}

onMounted(() => {
  fetchStats()
  fetchLowStock()
})
</script>

<template>
  <div class="seller-dashboard" v-loading="loading">
    <h2>数据概览</h2>

    <div v-if="stats?.shop_status === 'pending'" class="shop-alert">
      <el-alert title="您的店铺正在审核中" description="店铺审核通过后即可上架商品，请耐心等待。" type="warning" show-icon :closable="false" />
    </div>
    <div v-if="stats?.shop_status === 'rejected'" class="shop-alert">
      <el-alert title="店铺审核未通过" description="请联系管理员了解详情。" type="error" show-icon :closable="false" />
    </div>

    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-icon" style="background: #fff3e0"><el-icon :size="28" color="#FF6700"><Goods /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_products }}</span>
          <span class="stat-label">在售商品</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #e3f2fd"><el-icon :size="28" color="#409EFF"><List /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_orders }}</span>
          <span class="stat-label">累计订单</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8f5e9"><el-icon :size="28" color="#67C23A"><Wallet /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">¥{{ formatMoney(stats.total_revenue) }}</span>
          <span class="stat-label">累计收入</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fce4ec"><el-icon :size="28" color="#F56C6C"><Bell /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.pending_orders }}</span>
          <span class="stat-label">待发货</span>
        </div>
      </div>
    </div>

    <div class="today-section" v-if="stats">
      <h3>今日数据</h3>
      <div class="today-grid">
        <div class="today-item">
          <span class="today-value">{{ stats.today_orders }}</span>
          <span class="today-label">今日订单</span>
        </div>
        <div class="today-item">
          <span class="today-value">¥{{ formatMoney(stats.today_revenue) }}</span>
          <span class="today-label">今日收入</span>
        </div>
      </div>
    </div>

    <!-- 库存预警 -->
    <div class="low-stock-section" v-if="lowStockProducts.length">
      <div class="section-header">
        <h3>
          <el-icon><Warning /></el-icon>
          库存预警（≤{{ stockThreshold }}件）
        </h3>
        <el-button size="small" @click="router.push('/seller/products')">查看全部商品</el-button>
      </div>
      <el-table :data="lowStockProducts" border size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="商品名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock <= 3 ? 'danger' : 'warning'" size="small">
              {{ row.stock }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="100">
          <template #default="{ row }">
            ¥{{ formatMoney(row.price) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h3>快速操作</h3>
      <div class="actions-grid">
        <el-button @click="router.push('/seller/products')">商品管理</el-button>
        <el-button @click="router.push('/seller/orders')">订单管理</el-button>
        <el-button @click="router.push('/seller/shop')">店铺设置</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.seller-dashboard h2 { margin: 0 0 24px; font-size: 20px; }
.shop-alert { margin-bottom: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-card { background: var(--color-bg-white); border-radius: var(--radius-card); padding: 24px; box-shadow: var(--shadow-card); display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--color-text); }
.stat-label { font-size: 13px; color: var(--color-text-secondary); margin-top: 2px; }

.today-section { background: var(--color-bg-white); border-radius: var(--radius-card); padding: 24px; box-shadow: var(--shadow-card); margin-bottom: 24px; }
.today-section h3 { margin: 0 0 20px; font-size: 16px; }
.today-grid { display: flex; gap: 48px; }
.today-item { display: flex; flex-direction: column; }
.today-value { font-size: 28px; font-weight: 700; color: var(--color-primary); }
.today-label { font-size: 13px; color: var(--color-text-secondary); margin-top: 4px; }

.low-stock-section { background: var(--color-bg-white); border-radius: var(--radius-card); padding: 24px; box-shadow: var(--shadow-card); margin-bottom: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px; color: #e6a23c; }

.quick-actions { background: var(--color-bg-white); border-radius: var(--radius-card); padding: 24px; box-shadow: var(--shadow-card); }
.quick-actions h3 { margin: 0 0 16px; font-size: 16px; }
.actions-grid { display: flex; gap: 12px; }
</style>
