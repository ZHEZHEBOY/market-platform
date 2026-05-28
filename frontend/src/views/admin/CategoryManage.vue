<script setup>
import { ref, onMounted } from 'vue'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../../api/category'
import { ElMessage, ElMessageBox } from 'element-plus'

const categories = ref([])
const loading = ref(false)
const showDialog = false
const dialogVisible = ref(false)
const editingId = ref(null)

const form = ref({ name: '', parent_id: null, sort_order: 0 })
const flatCategories = ref([])

async function fetchCategories() {
  loading.value = true
  try {
    const { data } = await getCategories({ tree: true })
    categories.value = data.items
    const { data: flat } = await getCategories({ tree: false })
    flatCategories.value = flat.items
  } finally {
    loading.value = false
  }
}

function openAdd(parentId = null) {
  editingId.value = null
  form.value = { name: '', parent_id: parentId, sort_order: 0 }
  dialogVisible.value = true
}

function openEdit(cat) {
  editingId.value = cat.id
  form.value = { name: cat.name, parent_id: cat.parent_id, sort_order: cat.sort_order }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, form.value)
      ElMessage.success('已更新')
    } else {
      await createCategory(form.value)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    fetchCategories()
  } catch {}
}

async function handleDelete(cat) {
  try {
    await ElMessageBox.confirm(`确定删除分类「${cat.name}」？子分类也会被删除。`, '警告', { type: 'warning' })
    await deleteCategory(cat.id)
    ElMessage.success('已删除')
    fetchCategories()
  } catch {}
}

function getParentName(parentId) {
  if (!parentId) return '—'
  const parent = flatCategories.value.find(c => c.id === parentId)
  return parent ? parent.name : '—'
}

onMounted(fetchCategories)
</script>

<template>
  <div class="category-manage">
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="openAdd()">新增分类</el-button>
    </div>

    <el-table :data="categories" v-loading="loading" row-key="id" default-expand-all>
      <el-table-column prop="name" label="分类名称" min-width="200" />
      <el-table-column label="父分类" width="150">
        <template #default="{ row }">{{ getParentName(row.parent_id) }}</template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openAdd(row.id)">添加子分类</el-button>
          <el-button type="primary" text size="small" @click="openEdit(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新增分类'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="分类名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="form.parent_id" placeholder="无（顶级分类）" clearable style="width: 100%">
            <el-option
              v-for="c in flatCategories"
              :key="c.id"
              :label="c.name"
              :value="c.id"
              :disabled="c.id === editingId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.category-manage { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
