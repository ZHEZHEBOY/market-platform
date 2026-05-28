<template>
  <div class="my-coupons">
    <h2>我的优惠券</h2>
    <el-tabs v-model="activeTab" @tab-change="fetchCoupons">
      <el-tab-pane label="可使用" name="active" />
      <el-tab-pane label="已使用" name="used" />
      <el-tab-pane label="已过期" name="expired" />
    </el-tabs>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="coupons.length === 0" class="empty">暂无优惠券</div>
    <div v-else class="coupon-list">
      <div
        v-for="item in coupons"
        :key="item.id"
        class="coupon-card"
        :class="{ disabled: item.status !== 'active' }"
      >
        <div class="coupon-left">
          <div class="coupon-value">
            <span v-if="item.coupon.coupon_type === 'fixed'" class="amount">
              ¥{{ (item.coupon.value / 100).toFixed(0) }}
            </span>
            <span v-else class="amount">{{ item.coupon.value }}%</span>
            <span class="type">{{ item.coupon.coupon_type === 'fixed' ? '满减券' : '折扣券' }}</span>
          </div>
          <div class="coupon-condition" v-if="item.coupon.min_amount > 0">
            满{{ (item.coupon.min_amount / 100).toFixed(0) }}元可用
          </div>
          <div class="coupon-condition" v-else>无门槛</div>
        </div>
        <div class="coupon-right">
          <div class="coupon-name">{{ item.coupon.name }}</div>
          <div class="coupon-desc">{{ item.coupon.description || '暂无描述' }}</div>
          <div class="coupon-time">
            有效期至 {{ formatDate(item.coupon.end_time) }}
          </div>
          <div class="coupon-status">
            <el-tag v-if="item.status === 'active'" type="success">可使用</el-tag>
            <el-tag v-else-if="item.status === 'used'" type="info">已使用</el-tag>
            <el-tag v-else type="danger">已过期</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyCoupons } from '@/api/coupon'

const activeTab = ref('active')
const coupons = ref([])
const loading = ref(true)

const fetchCoupons = async () => {
  loading.value = true
  try {
    const res = await getMyCoupons(activeTab.value)
    coupons.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(fetchCoupons)
</script>

<style scoped>
.my-coupons {
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
  margin-top: 16px;
}

.coupon-card {
  display: flex;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.coupon-card.disabled {
  opacity: 0.6;
}

.coupon-left {
  width: 140px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.coupon-card.disabled .coupon-left {
  background: linear-gradient(135deg, #999, #bbb);
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
}

.coupon-status {
  margin-top: auto;
}
</style>
