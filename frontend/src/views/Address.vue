<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index'
import { ElMessage } from 'element-plus'

const addresses = ref([])
const dialogVisible = ref(false)
const form = ref({ receiver_name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false })
const editId = ref(null)

async function fetchAddresses() {
  const { data } = await api.get('/api/addresses')
  addresses.value = data
}

function openDialog(addr) {
  if (addr) {
    editId.value = addr.id
    form.value = { ...addr }
  } else {
    editId.value = null
    form.value = { receiver_name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false }
  }
  dialogVisible.value = true
}

async function save() {
  if (editId.value) {
    await api.put(`/api/addresses/${editId.value}`, form.value)
  } else {
    await api.post('/api/addresses', form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  fetchAddresses()
}

async function remove(id) {
  await api.delete(`/api/addresses/${id}`)
  ElMessage.success('已删除')
  fetchAddresses()
}

onMounted(fetchAddresses)
</script>

<template>
  <div class="address-page">
    <h2>收货地址 <el-button type="primary" size="small" @click="openDialog(null)">新增地址</el-button></h2>
    <div v-for="a in addresses" :key="a.id" class="addr-card">
      <el-tag v-if="a.is_default" type="danger" size="small">默认</el-tag>
      <span class="addr-name">{{ a.receiver_name }} {{ a.phone }}</span>
      <span class="addr-detail">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</span>
      <div class="addr-actions">
        <el-button size="small" @click="openDialog(a)">编辑</el-button>
        <el-button size="small" type="danger" @click="remove(a.id)">删除</el-button>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="地址信息" width="500px">
      <el-form :model="form">
        <el-form-item label="收货人"><el-input v-model="form.receiver_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="省"><el-input v-model="form.province" /></el-form-item>
        <el-form-item label="市"><el-input v-model="form.city" /></el-form-item>
        <el-form-item label="区"><el-input v-model="form.district" /></el-form-item>
        <el-form-item label="详细地址"><el-input v-model="form.detail" /></el-form-item>
        <el-form-item><el-checkbox v-model="form.is_default">设为默认地址</el-checkbox></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.address-page { padding: 20px; max-width: 700px; margin: 0 auto; }
.addr-card { border: 1px solid #eee; padding: 12px; margin: 8px 0; border-radius: 4px; display: flex; align-items: center; gap: 12px; }
.addr-name { font-weight: bold; }
.addr-detail { color: #666; flex: 1; }
.addr-actions { display: flex; gap: 8px; }
</style>
