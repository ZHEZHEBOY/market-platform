<script setup>
import { ref, onMounted } from 'vue'
import { getMyProducts, createMyProduct, updateMyProduct, deleteMyProduct, batchToggleProducts, batchDeleteProducts } from '../../api/seller'
import { ElMessage, ElMessageBox } from 'element-plus'

const products = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const dialogVisible = ref(false)
const editId = ref(null)
const form = ref({ name: '', description: '', price: 0, stock: 0, category: '', image_url: '' })

// 批量选择
const selectedIds = ref([])

async function fetchProducts() {
  loading.value = true
  try {
    const { data } = await getMyProducts({ page: page.value, page_size: 20 })
    products.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editId.value = null
  form.value = { name: '', description: '', price: 0, stock: 0, category: '', image_url: '' }
  dialogVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.value = {
    name: row.name,
    description: row.description,
    price: row.price / 100,
    stock: row.stock,
    category: row.category,
    image_url: row.image_url,
  }
  dialogVisible.value = true
}

async function handleSave() {
  const payload = {
    ...form.value,
    price: Math.round(form.value.price * 100),
  }
  if (editId.value) {
    await updateMyProduct(editId.value, payload)
    ElMessage.success('已更新')
  } else {
    await createMyProduct(payload)
    ElMessage.success('已上架')
  }
  dialogVisible.value = false
  fetchProducts()
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定下架该商品？', '提示', { type: 'warning' })
  await deleteMyProduct(id)
  ElMessage.success('已下架')
  fetchProducts()
}

// 批量上架
async function handleBatchEnable() {
  if (!selectedIds.value.length) {
    ElMessage.warning('请选择商品')
    return
  }
  await batchToggleProducts(selectedIds.value, true)
  ElMessage.success('批量上架成功')
  selectedIds.value = []
  fetchProducts()
}

// 批量下架
async function handleBatchDisable() {
  if (!selectedIds.value.length) {
    ElMessage.warning('请选择商品')
    return
  }
  await ElMessageBox.confirm(`确定下架选中的 ${selectedIds.value.length} 个商品？`, '提示', { type: 'warning' })
  await batchToggleProducts(selectedIds.value, false)
  ElMessage.success('批量下架成功')
  selectedIds.value = []
  fetchProducts()
}

// 批量删除
async function handleBatchDelete() {
  if (!selectedIds.value.length) {
    ElMessage.warning('请选择商品')
    return
  }
  await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个商品？`, '提示', { type: 'warning' })
  await batchDeleteProducts(selectedIds.value)
  ElMessage.success('批量删除成功')
  selectedIds.value = []
  fetchProducts()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(s => s.id)
}

onMounted(fetchProducts)
</script>

<template>
  <div class="seller-products">
    <div class="page-header">
      <h2>商品管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>上架商品
        </el-button>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <div class="batch-actions" v-if="selectedIds.length">
      <span class="selected-count">已选 {{ selectedIds.length }} 项</span>
      <el-button size="small" @click="handleBatchEnable">批量上架</el-button>
      <el-button size="small" @click="handleBatchDisable">批量下架</el-button>
      <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
    </div>

    <el-table :data="products" v-loading="loading" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="商品" min-width="200">
        <template #default="{row}">
          <div class="product-cell">
            <img v-if="row.image_url" :src="row.image_url" class="product-thumb" />
            <div class="img-placeholder-sm" v-else>{{ row.name[0] }}</div>
            <span>{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="100">
        <template #default="{row}">¥{{ (row.price / 100).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="80">
        <template #default="{row}">
          <el-tag :type="row.stock <= 10 ? 'danger' : row.stock <= 30 ? 'warning' : 'success'" size="small">
            {{ row.stock }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="80" />
      <el-table-column label="状态" width="80">
        <template #default="{row}">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '在售' : '已下架' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{row}">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="handleDelete(row.id)" v-if="row.is_active">下架</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination" v-if="total > 20">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchProducts" />
    </div>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑商品' : '上架商品'" width="520px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="商品名称">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入商品描述" />
        </el-form-item>
        <el-form-item label="价格(元)">
          <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="form.stock" :min="0" :step="1" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="form.category" placeholder="如：数码、办公、生活" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="form.image_url" placeholder="商品图片链接" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.seller-products h2 { margin: 0; font-size: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-actions { display: flex; gap: 12px; }
.batch-actions { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #fff3e0; border-radius: 8px; margin-bottom: 16px; }
.selected-count { font-size: 14px; color: #e6a23c; font-weight: 500; }
.product-cell { display: flex; align-items: center; gap: 10px; }
.product-thumb { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; }
.img-placeholder-sm { width: 40px; height: 40px; border-radius: 6px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #ccc; font-size: 16px; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }
</style>
