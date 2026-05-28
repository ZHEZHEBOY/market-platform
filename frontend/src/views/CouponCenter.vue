<template>
  <div class="coupon-center">
    <h2>领券中心</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="coupons.length === 0" class="empty">暂无可领取的优惠券</div>
    <div v-else class="coupon-list">
      <div v-for="coupon in coupons" :key="coupon.id" class="coupon-card">
        <div class="coupon-left">
          <div class="coupon-value">
            <span v-if="coupon.coupon_type === 'fixed'" class="amount">¥{{ (coupon.value / 100).toFixed(0) }}</span>
            <span v-else class="amount">{{ coupon.value }}%</span>
            <span class="type">{{ coupon.coupon_type === 'fixed' ? '满减券' : '折扣券' }}</span>
          </div>
          <div class="coupon-condition" v-if="coupon.min_amount > 0">
            满{{ (coupon.min_amount / 100).toFixed(0) }}元可用
          </div>
          <div class="coupon-condition" v-else>无门槛</div>
        </div>
        <div class="coupon-right">
          <div class="coupon-name">{{ coupon.name }}</div>
          <div class="coupon-desc">{{ coupon.description || '暂无描述' }}</div>
          <div class="coupon-time">
            {{ formatDate(coupon.start_time) }} - {{ formatDate(coupon.end_time) }}
          </div>
          <el-button
            type="primary"
            size="small"
            :loading="claimingId === coupon.id"
            @click="handleClaim(coupon)"
          >
            立即领取
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAvailableCoupons, claimCoupon } from '@/api/coupon'

const coupons = ref([])
const loading = ref(true)
const claimingId = ref(null)

const fetchCoupons = async () => {
  loading.value = true
  try {
    const res = await getAvailableCoupons()
    coupons.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleClaim = async (coupon) => {
  claimingId.value = coupon.id
  try {
    const res = await claimCoupon(coupon.id)
    if (res.data.success) {
      ElMessage.success('领取成功')
      fetchCoupons()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '领取失败')
  } finally {
    claimingId.value = null
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(fetchCoupons)
</script>

<style scoped>
.coupon-center {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

.coupon-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.coupon-card {
  display: flex;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.coupon-left {
  width: 140px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.coupon-value {
  text-align: center;
}

.coupon-value .amount {
  font-size: 28px;
  font-weight: bold;
}

.coupon-value .type {
  display: block;
  font-size: 12px;
  margin-top: 4px;
}

.coupon-condition {
  font-size: 12px;
  margin-top: 8px;
  opacity: 0.9;
}

.coupon-right {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.coupon-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.coupon-desc {
  font-size: 13px;
  color: #666;
}

.coupon-time {
  font-size: 12px;
  color: #999;
  margin-top: auto;
}
</style>
