<script setup>
import { ref, onMounted, watch } from 'vue'
import { getProducts, createProduct, updateProduct, deleteProduct } from '../../api/product'
import { ElMessage } from 'element-plus'

const products = ref([])
const total = ref(0)
const page = ref(1)
const dialogVisible = ref(false)
const form = ref({ name: '', description: '', price: 0, stock: 0, category: '', image_url: '' })
const editId = ref(null)

async function fetchProducts() {
  const { data } = await getProducts({ page: page.value, page_size: 20 })
  products.value = data.items; total.value = data.total
}
function openDialog(p) {
  form.value = p ? { ...p, price: (p.price / 100), stock: p.stock } : { name: '', description: '', price: 0, stock: 0, category: '', image_url: '' }
  editId.value = p?.id || null
  dialogVisible.value = true
}
async function save() {
  const payload = { ...form.value, price: Math.round(form.value.price * 100) }
  if (editId.value) { await updateProduct(editId.value, payload) } else { await createProduct(payload) }
  ElMessage.success('保存成功'); dialogVisible.value = false; fetchProducts()
}
async function remove(id) { await deleteProduct(id); fetchProducts() }

onMounted(fetchProducts)
watch(page, fetchProducts)
</script>
<template>
  <div class="product-manage">
    <h2>商品管理 <el-button type="primary" @click="openDialog(null)">新增商品</el-button></h2>
    <el-table :data="products">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" />
      <el-table-column label="价格"><template #default="{row}">¥{{ (row.price/100).toFixed(2) }}</template></el-table-column>
      <el-table-column prop="stock" label="库存" width="80" />
      <el-table-column prop="category" label="分类" />
      <el-table-column label="操作" width="200">
        <template #default="{row}">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">下架</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editId?'编辑商品':'新增商品'" width="500px">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="价格(元)"><el-input-number v-model="form.price" :min="0.01" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.image_url" /></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<style scoped>
.product-manage { padding: 20px; max-width: 1100px; margin: 0 auto; }
</style>
