<template>
  <div class="coupon-manage">
    <div class="header">
      <h2>优惠券管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">创建优惠券</el-button>
    </div>

    <el-table :data="coupons" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="code" label="优惠券码" width="120" />
      <el-table-column prop="name" label="名称" width="150" />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          {{ row.coupon_type === 'fixed' ? '满减券' : '折扣券' }}
        </template>
      </el-table-column>
      <el-table-column label="面值" width="100">
        <template #default="{ row }">
          <span v-if="row.coupon_type === 'fixed'">¥{{ (row.value / 100).toFixed(0) }}</span>
          <span v-else>{{ row.value }}%</span>
        </template>
      </el-table-column>
      <el-table-column label="最低消费" width="100">
        <template #default="{ row }">
          {{ row.min_amount > 0 ? '¥' + (row.min_amount / 100).toFixed(0) : '无门槛' }}
        </template>
      </el-table-column>
      <el-table-column label="发放/总量" width="100">
        <template #default="{ row }">
          {{ row.used_count }} / {{ row.total_count || '不限' }}
        </template>
      </el-table-column>
      <el-table-column label="有效期" width="200">
        <template #default="{ row }">
          {{ formatDate(row.start_time) }} - {{ formatDate(row.end_time) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" @click="handleToggle(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建优惠券" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="优惠券码" required>
          <el-input v-model="form.code" placeholder="如 SAVE20" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="如 新人专享券" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-radio-group v-model="form.coupon_type">
            <el-radio value="fixed">满减券</el-radio>
            <el-radio value="percent">折扣券</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="form.coupon_type === 'fixed' ? '减免金额(分)' : '折扣比例(%)'" required>
          <el-input-number v-model="form.value" :min="1" />
        </el-form-item>
        <el-form-item label="最低消费(分)">
          <el-input-number v-model="form.min_amount" :min="0" />
        </el-form-item>
        <el-form-item label="最大优惠(分)" v-if="form.coupon_type === 'percent'">
          <el-input-number v-model="form.max_discount" :min="0" />
        </el-form-item>
        <el-form-item label="发放总量">
          <el-input-number v-model="form.total_count" :min="0" />
          <span class="hint">0 表示不限量</span>
        </el-form-item>
        <el-form-item label="有效期" required>
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listCoupons, createCoupon, toggleCoupon } from '@/api/coupon'

const coupons = ref([])
const loading = ref(true)
const showCreateDialog = ref(false)
const creating = ref(false)

const form = ref({
  code: '',
  name: '',
  description: '',
  coupon_type: 'fixed',
  value: 1000,
  min_amount: 0,
  max_discount: null,
  total_count: 100,
  dateRange: []
})

const fetchCoupons = async () => {
  loading.value = true
  try {
    const res = await listCoupons()
    coupons.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!form.value.code || !form.value.name || !form.value.dateRange?.length) {
    ElMessage.warning('请填写必填项')
    return
  }

  creating.value = true
  try {
    await createCoupon({
      ...form.value,
      start_time: form.value.dateRange[0].toISOString(),
      end_time: form.value.dateRange[1].toISOString()
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    form.value = {
      code: '',
      name: '',
      description: '',
      coupon_type: 'fixed',
      value: 1000,
      min_amount: 0,
      max_discount: null,
      total_count: 100,
      dateRange: []
    }
    fetchCoupons()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

const handleToggle = async (coupon) => {
  try {
    await toggleCoupon(coupon.id)
    ElMessage.success(coupon.is_active ? '已禁用' : '已启用')
    fetchCoupons()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(fetchCoupons)
</script>

<style scoped>
.coupon-manage {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.hint {
  margin-left: 10px;
  color: #999;
  font-size: 12px;
}
</style>
