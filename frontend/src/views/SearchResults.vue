<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProducts } from '../api/product'
import api from '../api/index'
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

// 搜索历史
const searchHistory = ref([])

const sortOptions = [
  { label: '综合排序', value: '' },
  { label: '价格从低到高', value: 'price_asc' },
  { label: '价格从高到低', value: 'price_desc' },
  { label: '最新上架', value: 'newest' },
]

function loadSearchHistory() {
  try {
    searchHistory.value = JSON.parse(localStorage.getItem('search_history') || '[]')
  } catch {
    searchHistory.value = []
  }
}

function saveSearchHistory(kw) {
  try {
    let history = JSON.parse(localStorage.getItem('search_history') || '[]')
    history = history.filter(h => h !== kw)
    history.unshift(kw)
    if (history.length > 10) history = history.slice(0, 10)
    localStorage.setItem('search_history', JSON.stringify(history))
    searchHistory.value = history
  } catch {}
}

function clearSearchHistory() {
  localStorage.removeItem('search_history')
  searchHistory.value = []
}

function searchFromHistory(kw) {
  keyword.value = kw
  handleSearch()
}

async function fetchCategories() {
  try {
    const { data } = await getProducts({ page: 1, page_size: 100 })
    const catSet = new Set()
    data.items.forEach(p => { if (p.category) catSet.add(p.category) })
    categories.value = [...catSet]
  } catch {}
}

// 统一搜索：同时发起关键词 + 语义搜索，合并去重
async function fetchAll() {
  if (!keyword.value.trim()) {
    // 无关键词时走普通列表
    loading.value = true
    try {
      const { data } = await getProducts({ page: page.value, page_size: pageSize.value, sort: sort.value })
      products.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
    return
  }

  loading.value = true

  const kw = keyword.value.trim()
  const params = { keyword: kw, page: 1, page_size: 40 }
  if (category.value) params.category = category.value
  if (minPrice.value) params.min_price = Math.round(Number(minPrice.value) * 100)
  if (maxPrice.value) params.max_price = Math.round(Number(maxPrice.value) * 100)

  const semanticParams = new URLSearchParams({ query: kw, top_k: 40 })
  if (category.value) semanticParams.append('category', category.value)

  try {
    const [kwRes, semRes] = await Promise.allSettled([
      getProducts(params),
      api.post(`/api/vector/semantic?${semanticParams}`),
    ])

    const kwItems = kwRes.status === 'fulfilled' ? kwRes.value.data.items : []
    const semItems = semRes.status === 'fulfilled'
      ? semRes.value.data.results.map(r => ({
          id: r.product_id,
          name: r.name,
          category: r.category,
          price: r.price,
          image_url: r.image_url,
          _score: r.score,
          _source: 'semantic',
        }))
      : []

    // 标记关键词结果来源
    kwItems.forEach(p => { p._source = 'keyword' })

    // 合并去重：语义结果在前，关键词结果补充
    const seen = new Set(semItems.map(p => p.id))
    const merged = [...semItems]
    for (const p of kwItems) {
      if (!seen.has(p.id)) {
        seen.add(p.id)
        merged.push(p)
      }
    }

    allMergedProducts.value = merged
    products.value = merged
    total.value = merged.length
  } catch (e) {
    console.error('搜索失败:', e)
  } finally {
    loading.value = false
  }
}

// 仅关键词搜索（排序/翻页时用）
async function fetchKeywordOnly() {
  allMergedProducts.value = [] // 清空合并结果
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
  fetchAll()
}

function handleCategory(cat) {
  category.value = category.value === cat ? '' : cat
  page.value = 1
  updateQuery()
  fetchAll()
}

function handleSort(val) {
  sort.value = val
  page.value = 1
  fetchKeywordOnly()
}

function handlePriceFilter() {
  page.value = 1
  updateQuery()
  fetchAll()
}

function updateQuery() {
  const q = {}
  if (keyword.value) q.keyword = keyword.value
  if (category.value) q.category = category.value
  router.replace({ query: q })
}

// 语义搜索时，结果已在客户端合并，分页用客户端切片
const allMergedProducts = ref([])

const displayProducts = computed(() => {
  if (keyword.value && allMergedProducts.value.length) {
    // 语义+关键词合并结果，客户端分页
    const start = (page.value - 1) * pageSize.value
    return allMergedProducts.value.slice(start, start + pageSize.value)
  }
  return products.value
})

function handlePageChange(p) {
  page.value = p
  if (!keyword.value || !allMergedProducts.value.length) {
    fetchKeywordOnly()
  }
  // 有合并结果时，displayProducts 会自动切片，无需重新请求
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const resultText = computed(() => {
  if (keyword.value) return `"${keyword.value}" 的搜索结果`
  if (category.value) return `${category.value} 分类`
  return '全部商品'
})

// 统计来源数量
const sourceStats = computed(() => {
  const sem = products.value.filter(p => p._source === 'semantic').length
  const kw = products.value.filter(p => p._source === 'keyword').length
  return { semantic: sem, keyword: kw }
})

onMounted(() => {
  keyword.value = route.query.keyword || ''
  category.value = route.query.category || ''
  loadSearchHistory()
  fetchCategories()
  if (keyword.value) {
    fetchAll()
  } else {
    fetchKeywordOnly()
  }
})

watch(() => route.query, (q) => {
  keyword.value = q.keyword || ''
  category.value = q.category || ''
  page.value = 1
  if (keyword.value) {
    fetchAll()
  } else {
    fetchKeywordOnly()
  }
})
</script>

<template>
  <div class="search-page">
    <div class="container">
      <!-- 搜索来源统计 -->
      <div class="search-stats" v-if="keyword && !loading && total > 0">
        <span class="stats-text">
          共找到 <strong>{{ total }}</strong> 件商品
          <template v-if="sourceStats.semantic > 0">
            · 🧠 语义匹配 {{ sourceStats.semantic }} 件
          </template>
          <template v-if="sourceStats.keyword > 0">
            · 🔍 关键词匹配 {{ sourceStats.keyword }} 件
          </template>
        </span>
      </div>

      <!-- 搜索历史 (无关键词时显示) -->
      <div class="history-section" v-if="!keyword && searchHistory.length">
        <div class="history-header">
          <span class="history-title">🕐 搜索历史</span>
          <span class="history-clear" @click="clearSearchHistory">清空</span>
        </div>
        <div class="history-tags">
          <span
            v-for="h in searchHistory"
            :key="h"
            class="history-tag"
            @click="searchFromHistory(h)"
          >
            {{ h }}
          </span>
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
            <div v-for="p in products" :key="p.id" class="product-card-wrapper">
              <ProductCard :product="p" />
              <!-- 来源标签 -->
              <div class="source-tag" v-if="p._source">
                <span v-if="p._source === 'semantic'" class="tag tag-semantic">
                  🧠 {{ (p._score * 100).toFixed(0) }}%
                </span>
                <span v-else class="tag tag-keyword">🔍</span>
              </div>
            </div>
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 搜索来源统计 */
.search-stats {
  margin-bottom: 16px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #f5f5f5 100%);
  border-radius: 8px;
  text-align: center;
}

.stats-text {
  font-size: 13px;
  color: #666;
}

.stats-text strong {
  color: var(--color-primary);
}

/* 搜索历史 */
.history-section {
  margin-bottom: 16px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.history-clear {
  font-size: 13px;
  color: #999;
  cursor: pointer;
}

.history-clear:hover {
  color: #e4393c;
}

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-tag {
  padding: 6px 14px;
  background: #f5f5f5;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.history-tag:hover {
  background: #e8e8e8;
  color: #333;
}

.search-body {
  display: flex;
  gap: 12px;
}

.filter-sidebar {
  width: 160px;
  flex-shrink: 0;
}

.filter-section {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 16px;
  margin-bottom: 12px;
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

/* 来源标签 */
.product-card-wrapper {
  position: relative;
}

.source-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  backdrop-filter: blur(4px);
}

.tag-semantic {
  background: rgba(76, 175, 80, 0.9);
  color: #fff;
}

.tag-keyword {
  background: rgba(33, 150, 243, 0.85);
  color: #fff;
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
