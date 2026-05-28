<template>
  <div class="refund-manage">
    <h2>退款审核</h2>

    <el-tabs v-model="activeTab" @tab-change="fetchRefunds">
      <el-tab-pane label="待审核" name="pending" />
      <el-tab-pane label="已通过" name="approved" />
      <el-tab-pane label="已拒绝" name="rejected" />
      <el-tab-pane label="全部" name="" />
    </el-tabs>

    <el-table :data="refunds" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_id" label="订单ID" width="80" />
      <el-table-column label="退款原因" width="120">
        <template #default="{ row }">
          {{ getReasonText(row.reason) }}
        </template>
      </el-table-column>
      <el-table-column label="退款金额" width="100">
        <template #default="{ row }">
          <span class="amount">¥{{ (row.amount / 100).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="申请时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="admin_note" label="审核备注" width="150" show-overflow-tooltip />
      <el-table-column label="操作" width="160" v-if="activeTab === 'pending'">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="handleReview(row, 'approved')">通过</el-button>
          <el-button size="small" type="danger" @click="handleReview(row, 'rejected')">拒绝</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 审核对话框 -->
    <el-dialog v-model="showReviewDialog" :title="reviewAction === 'approved' ? '通过退款' : '拒绝退款'" width="400px">
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="审核备注">
          <el-input v-model="reviewForm.admin_note" type="textarea" placeholder="请输入备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button :type="reviewAction === 'approved' ? 'success' : 'danger'" :loading="reviewing" @click="submitReview">
          {{ reviewAction === 'approved' ? '确认通过' : '确认拒绝' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listRefunds, reviewRefund } from '@/api/refund'

const activeTab = ref('pending')
const refunds = ref([])
const loading = ref(true)
const showReviewDialog = ref(false)
const reviewAction = ref('approved')
const reviewing = ref(false)
const currentRefund = ref(null)

const reviewForm = ref({
  admin_note: ''
})

const fetchRefunds = async () => {
  loading.value = true
  try {
    const res = await listRefunds(activeTab.value || undefined)
    refunds.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleReview = (refund, action) => {
  currentRefund.value = refund
  reviewAction.value = action
  reviewForm.value.admin_note = ''
  showReviewDialog.value = true
}

const submitReview = async () => {
  reviewing.value = true
  try {
    await reviewRefund(currentRefund.value.id, {
      status: reviewAction.value,
      admin_note: reviewForm.value.admin_note
    })
    ElMessage.success(reviewAction.value === 'approved' ? '已通过' : '已拒绝')
    showReviewDialog.value = false
    fetchRefunds()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    reviewing.value = false
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
.refund-manage {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.amount {
  color: #ff4d4f;
  font-weight: bold;
}
</style>
