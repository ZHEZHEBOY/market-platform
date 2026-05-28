<script setup>
import { ref, onMounted } from 'vue'
import { getMyShop, updateMyShop } from '../../api/seller'
import { ElMessage } from 'element-plus'

const shop = ref(null)
const loading = ref(true)
const saving = ref(false)
const form = ref({ name: '', description: '' })

async function fetchShop() {
  loading.value = true
  try {
    const { data } = await getMyShop()
    shop.value = data
    form.value = { name: data.name, description: data.description }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const { data } = await updateMyShop(form.value)
    shop.value = data
    ElMessage.success('店铺信息已更新')
  } finally {
    saving.value = false
  }
}

const statusMap = {
  pending: { label: '审核中', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
}

onMounted(fetchShop)
</script>

<template>
  <div class="seller-shop" v-loading="loading">
    <h2>店铺设置</h2>

    <div class="shop-card" v-if="shop">
      <div class="shop-status">
        <span>店铺状态：</span>
        <el-tag :type="statusMap[shop.status]?.type">{{ statusMap[shop.status]?.label }}</el-tag>
      </div>

      <el-form :model="form" label-width="80px" class="shop-form" @submit.prevent="handleSave">
        <el-form-item label="店铺名称">
          <el-input v-model="form.name" placeholder="请输入店铺名称" />
        </el-form-item>
        <el-form-item label="店铺简介">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="介绍一下您的店铺" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
        </el-form-item>
      </el-form>

      <div class="shop-meta">
        <p>店铺ID：{{ shop.id }}</p>
        <p>创建时间：{{ new Date(shop.created_at).toLocaleString('zh-CN') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.seller-shop h2 { margin: 0 0 24px; font-size: 20px; }
.shop-card { background: var(--color-bg-white); border-radius: var(--radius-card); padding: 32px; box-shadow: var(--shadow-card); }
.shop-status { display: flex; align-items: center; gap: 10px; margin-bottom: 28px; font-size: 15px; }
.shop-form { max-width: 500px; }
.shop-meta { margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--color-border); }
.shop-meta p { margin: 0 0 6px; font-size: 13px; color: var(--color-text-secondary); }
</style>
