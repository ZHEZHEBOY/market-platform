<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts } from '../api/product'
import { useCartStore } from '../stores/cart'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

const products = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const keyword = ref('')
const loading = ref(false)

async function fetchProducts() {
  loading.value = true
  const { data } = await getProducts({ page: page.value, page_size: pageSize.value, keyword: keyword.value })
  products.value = data.items
  total.value = data.total
  loading.value = false
}

function search() {
  page.value = 1
  fetchProducts()
}

async function addCart(productId) {
  if (!userStore.token) {
    router.push('/login')
    return
  }
  await cartStore.add(productId, 1)
}

onMounted(fetchProducts)
watch(page, fetchProducts)
</script>

<template>
  <div class="home">
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索商品" @keyup.enter="search" clearable class="search-input" />
      <el-button type="primary" @click="search">搜索</el-button>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col v-for="p in products" :key="p.id" :span="6" style="margin-bottom: 20px">
        <el-card :body-style="{ padding: 0 }" class="product-card" @click="router.push(`/product/${p.id}`)">
          <img :src="p.image_url || '/vite.svg'" class="product-img" />
          <div class="product-info">
            <h3>{{ p.name }}</h3>
            <p class="price">¥{{ (p.price / 100).toFixed(2) }}</p>
            <p class="stock">库存: {{ p.stock }}</p>
            <el-button type="primary" size="small" @click.stop="addCart(p.id)" :disabled="p.stock === 0">
              {{ p.stock === 0 ? '已售罄' : '加入购物车' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="pagination" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" background />
    </div>
  </div>
</template>

<style scoped>
.home { padding: 20px; max-width: 1200px; margin: 0 auto; }
.search-bar { display: flex; gap: 10px; margin-bottom: 20px; }
.search-input { max-width: 400px; }
.product-card { cursor: pointer; }
.product-img { width: 100%; height: 180px; object-fit: cover; }
.product-info { padding: 12px; }
.product-info h3 { margin: 0 0 8px; font-size: 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.price { color: #e4393c; font-size: 18px; font-weight: bold; margin: 0 0 4px; }
.stock { color: #999; font-size: 12px; margin: 0 0 8px; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }
</style>
