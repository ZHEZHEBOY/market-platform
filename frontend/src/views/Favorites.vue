<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listFavorites, removeFavorite } from '../api/favorite'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const favorites = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

async function fetchFavorites() {
  loading.value = true
  try {
    const { data } = await listFavorites({ page: page.value, page_size: pageSize })
    favorites.value = data.items
    total.value = data.total
  } finally {
  loading.value = false
  }
}

async function handleRemove(item) {
  try {
    await ElMessageBox.confirm(`确定取消收藏「${item.product_name}」？`, '提示', { type: 'warning' })
    await removeFavorite(item.product_id)
    ElMessage.success('已取消收藏')
    fetchFavorites()
  } catch {}
}

function goProduct(id) {
  router.push(`/product/${id}`)
}

function handlePageChange(p) {
  page.value = p
  fetchFavorites()
}

onMounted(fetchFavorites)
</script>

<template>
  <div class="favorites-page">
    <h2>我的收藏</h2>

    <div class="fav-list" v-if="favorites.length" v-loading="loading">
      <div class="fav-item" v-for="item in favorites" :key="item.id">
        <img
          :src="item.product_image || '/vite.svg'"
          class="fav-img"
          @click="goProduct(item.product_id)"
        />
        <div class="fav-info" @click="goProduct(item.product_id)">
          <h3 class="fav-name">{{ item.product_name }}</h3>
          <p class="fav-desc">{{ item.product_desc }}</p>
          <p class="fav-price">¥{{ (item.product_price / 100).toFixed(2) }}</p>
        </div>
        <div class="fav-actions">
          <el-button type="danger" text @click="handleRemove(item)">取消收藏</el-button>
        </div>
      </div>
    </div>
    <el-empty v-else-if="!loading" description="还没有收藏商品" />

    <el-pagination
      v-if="total > pageSize"
      :current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      @current-change="handlePageChange"
      class="pagination"
    />
  </div>
</template>

<style scoped>
.favorites-page { max-width: 900px; margin: 0 auto; padding: 30px 20px; }
.favorites-page h2 { margin: 0 0 24px; }
.fav-list { display: flex; flex-direction: column; gap: 0; }
.fav-item { display: flex; align-items: center; gap: 16px; padding: 16px 0; border-bottom: 1px solid #f0f0f0; }
.fav-img { width: 100px; height: 100px; object-fit: cover; border-radius: 6px; cursor: pointer; }
.fav-info { flex: 1; cursor: pointer; }
.fav-name { margin: 0 0 6px; font-size: 15px; }
.fav-desc { margin: 0 0 6px; color: #999; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 400px; }
.fav-price { margin: 0; color: #e4393c; font-size: 16px; font-weight: bold; }
.fav-actions { flex-shrink: 0; }
.pagination { margin-top: 24px; display: flex; justify-content: center; }
</style>
