<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProducts } from '../api/product'
import { debounce } from '../api/index'
import ProductCard from '../components/ProductCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'

const route = useRoute()
const router = useRouter()

const products = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const keyword = ref('')
const category = ref('')
const minPrice = ref('')
const maxPrice = ref('')
const sort = ref('')
const categories = ref([])

// 搜索建议
const suggestions = ref([])
const showSuggestions = ref(false)

const sortOptions = [
  { label: '综合排序', value: '' },
  { label: '价格从低到高', value: 'price_asc' },
  { label: '价格从高到低', value: 'price_desc' },
  { label: '最新上架', value: 'newest' },
]

// 获取搜索建议
const fetchSuggestions = debounce(async (query) => {
  if (!query || query.length < 1) {
    suggestions.value = []
    return
  }
  try {
    const { data } = await getProducts({ keyword: query, page: 1, page_size: 5 })
    suggestions.value = data.items.map(p => p.name)
  } catch {
    suggestions.value = []
  }
}, 200)

function handleInput(val) {
  fetchSuggestions(val)
  showSuggestions.value = true
}

function selectSuggestion(suggestion) {
  keyword.value = suggestion
  showSuggestions.value = false
  handleSearch()
}

async function fetchCategories() {
  try {
    const { data } = await getProducts({ page: 1, page_size: 200 })
    const catSet = new Set()
    data.items.forEach(p => { if (p.category) catSet.add(p.category) })
    categories.value = [...catSet]
  } catch {}
}

async function fetchProducts() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      sort: sort.value,
    }
    if (keyword.value) params.keyword = keyword.value
    if (category.value) params.category = category.value
    if (minPrice.value) params.min_price = Math.round(Number(minPrice.value) * 100)
    if (maxPrice.value) params.max_price = Math.round(Number(maxPrice.value) * 100)

    const { data } = await getProducts(params)
    products.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  showSuggestions.value = false
  updateQuery()
  fetchProducts()
}

function handleCategory(cat) {
  category.value = category.value === cat ? '' : cat
  page.value = 1
  updateQuery()
  fetchProducts()
}

function handleSort(val) {
  sort.value = val
  page.value = 1
  fetchProducts()
}

function handlePriceFilter() {
  page.value = 1
  updateQuery()
  fetchProducts()
}

function updateQuery() {
  const q = {}
  if (keyword.value) q.keyword = keyword.value
  if (category.value) q.category = category.value
  router.replace({ query: q })
}

function handlePageChange(p) {
  page.value = p
  fetchProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const resultText = computed(() => {
  if (keyword.value) return `"${keyword.value}" 的搜索结果`
  if (category.value) return `${category.value} 分类`
  return '全部商品'
})

onMounted(() => {
  keyword.value = route.query.keyword || ''
  category.value = route.query.category || ''
  fetchCategories()
  fetchProducts()
})

watch(() => route.query, (q) => {
  keyword.value = q.keyword || ''
  category.value = q.category || ''
  page.value = 1
  fetchProducts()
})
</script>

<template>
  <div class="search-page">
    <div class="container">
      <!-- Search Bar -->
      <div class="search-header">
        <div class="search-wrapper">
          <el-input
            v-model="keyword"
            placeholder="搜索商品"
            size="large"
            @input="handleInput"
            @keyup.enter="handleSearch"
            @focus="showSuggestions = true"
            @blur="setTimeout(() => showSuggestions = false, 200)"
            clearable
            class="search-input-lg"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
          <!-- 搜索建议下拉 -->
          <div class="suggestions" v-if="showSuggestions && suggestions.length">
            <div
              v-for="s in suggestions"
              :key="s"
              class="suggestion-item"
              @mousedown="selectSuggestion(s)"
            >
              <el-icon><Search /></el-icon>
              <span>{{ s }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="search-body">
        <!-- Sidebar Filters -->
        <aside class="filter-sidebar">
          <div class="filter-section">
            <h3>商品分类</h3>
            <div class="filter-list">
              <div
                v-for="cat in categories"
                :key="cat"
                :class="['filter-item', { active: category === cat }]"
                @click="handleCategory(cat)"
              >
                {{ cat }}
              </div>
            </div>
          </div>

          <div class="filter-section">
            <h3>价格区间</h3>
            <div class="price-filter">
              <el-input v-model="minPrice" placeholder="最低" size="small" />
              <span class="price-sep">-</span>
              <el-input v-model="maxPrice" placeholder="最高" size="small" />
              <el-button size="small" type="primary" @click="handlePriceFilter">筛选</el-button>
            </div>
          </div>
        </aside>

        <!-- Results -->
        <main class="results-main">
          <div class="results-bar">
            <span class="result-count">{{ resultText }}（{{ total }} 件商品）</span>
            <div class="sort-tabs">
              <span
                v-for="opt in sortOptions"
                :key="opt.value"
                :class="['sort-tab', { active: sort === opt.value }]"
                @click="handleSort(opt.value)"
              >
                {{ opt.label }}
              </span>
            </div>
          </div>

          <div v-if="loading" class="products-grid">
            <SkeletonCard v-for="i in pageSize" :key="i" />
          </div>

          <div v-else-if="products.length" class="products-grid">
            <ProductCard v-for="p in products" :key="p.id" :product="p" />
          </div>

          <el-empty v-else description="暂无相关商品" />

          <div class="pagination" v-if="total > pageSize">
            <el-pagination
              v-model:current-page="page"
              :page-size="pageSize"
              :total="total"
              layout="prev, pager, next"
              background
              @current-change="handlePageChange"
            />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-page {
  padding: 24px 0;
}

.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 20px;
}

.search-header {
  margin-bottom: 24px;
}

.search-wrapper {
  position: relative;
}

.search-input-lg :deep(.el-input__wrapper) {
  border-radius: var(--radius-input);
  box-shadow: 0 0 0 1px var(--color-border);
}

.search-input-lg :deep(.el-input-group__append) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  border-radius: 0 var(--radius-input) var(--radius-input) 0;
}

.search-input-lg :deep(.el-input-group__append .el-button) {
  color: #fff;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.suggestion-item:hover {
  background: #f5f7fa;
}

.suggestion-item .el-icon {
  color: #999;
}

.search-body {
  display: flex;
  gap: 24px;
}

.filter-sidebar {
  width: 200px;
  flex-shrink: 0;
}

.filter-section {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-card);
}

.filter-section h3 {
  margin: 0 0 14px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.filter-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-item {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-item:hover {
  background: #f5f5f5;
  color: var(--color-text);
}

.filter-item.active {
  background: var(--color-primary);
  color: #fff;
}

.price-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.price-filter .el-input {
  width: 70px;
}

.price-sep {
  color: var(--color-text-light);
}

.results-main {
  flex: 1;
  min-width: 0;
}

.results-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.result-count {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.sort-tabs {
  display: flex;
  gap: 4px;
}

.sort-tab {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.sort-tab:hover {
  background: #f5f5f5;
}

.sort-tab.active {
  background: var(--color-primary);
  color: #fff;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 960px) {
  .filter-sidebar {
    display: none;
  }

  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
