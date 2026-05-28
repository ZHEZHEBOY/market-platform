<template>
  <div class="my-refunds">
    <h2>退款/售后</h2>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="refunds.length === 0" class="empty">暂无退款申请</div>
    <div v-else class="refund-list">
      <div v-for="refund in refunds" :key="refund.id" class="refund-card">
        <div class="refund-header">
          <span class="refund-id">退款单号: {{ refund.id }}</span>
          <el-tag :type="getStatusType(refund.status)">{{ getStatusText(refund.status) }}</el-tag>
        </div>
        <div class="refund-info">
          <div class="info-item">
            <span class="label">退款原因:</span>
            <span>{{ getReasonText(refund.reason) }}</span>
          </div>
          <div class="info-item">
            <span class="label">退款金额:</span>
            <span class="amount">¥{{ (refund.amount / 100).toFixed(2) }}</span>
          </div>
          <div class="info-item" v-if="refund.description">
            <span class="label">详细说明:</span>
            <span>{{ refund.description }}</span>
          </div>
          <div class="info-item">
            <span class="label">申请时间:</span>
            <span>{{ formatDate(refund.created_at) }}</span>
          </div>
          <div class="info-item" v-if="refund.admin_note">
            <span class="label">管理员备注:</span>
            <span>{{ refund.admin_note }}</span>
          </div>
        </div>
        <div class="refund-actions" v-if="refund.status === 'pending'">
          <el-button size="small" @click="handleCancel(refund)">取消申请</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyRefunds, cancelRefund } from '@/api/refund'

const refunds = ref([])
const loading = ref(true)

const fetchRefunds = async () => {
  loading.value = true
  try {
    const res = await getMyRefunds()
    refunds.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleCancel = async (refund) => {
  try {
    await ElMessageBox.confirm('确定取消该退款申请吗？', '提示', { type: 'warning' })
    await cancelRefund(refund.id)
    ElMessage.success('已取消')
    fetchRefunds()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    refunded: 'success',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    refunded: '已退款',
    cancelled: '已取消'
  }
  return map[status] || status
}

const getReasonText = (reason) => {
  const map = {
    quality: '质量问题',
    wrong_item: '发错商品',
    not_as_described: '与描述不符',
    change_mind: '不想要了',
    size_issue: '尺码不合适',
    other: '其他'
  }
  return map[reason] || reason
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(fetchRefunds)
</script>

<style scoped>
.my-refunds {
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

.refund-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.refund-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

.refund-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.refund-id {
  font-size: 14px;
  color: #666;
}

.refund-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.info-item .label {
  color: #999;
  min-width: 80px;
}

.info-item .amount {
  color: #ff4d4f;
  font-weight: bold;
}

.refund-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}
</style>
