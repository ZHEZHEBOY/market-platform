<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProduct, getProducts } from '../api/product'
import { useCartStore } from '../stores/cart'
import { useUserStore } from '../stores/user'
import { addFavorite, removeFavorite, checkFavorite } from '../api/favorite'
import { getProductReviews, createReview } from '../api/review'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

const product = ref(null)
const loading = ref(true)
const error = ref(null)
const quantity = ref(1)
const favorited = ref(false)
const currentImage = ref('')
const selectedSpecs = ref({})
const selectedSku = ref(null)

// 评价相关
const reviews = ref([])
const reviewTotal = ref(0)
const avgRating = ref(0)
const reviewPage = ref(1)
const reviewPageSize = 10
const activeTab = ref('detail')

// 评价表单
const showReviewForm = ref(false)
const reviewForm = ref({ rating: 5, content: '' })
const reviewSubmitting = ref(false)

// 本店推荐
const shopProducts = ref([])

// 计算所有图片
const allImages = computed(() => {
  if (!product.value) return []
  const imgs = []
  if (product.value.image_url) imgs.push(product.value.image_url)
  if (product.value.images?.length) {
    product.value.images.forEach(img => {
      if (img && !imgs.includes(img)) imgs.push(img)
    })
  }
  return imgs.length ? imgs : ['/images/misc/not-found.svg']
})

// 计算当前价格和库存
const currentPrice = computed(() => {
  if (selectedSku.value) return selectedSku.value.price
  return product.value?.price || 0
})

const currentStock = computed(() => {
  if (selectedSku.value) return selectedSku.value.stock
  return product.value?.stock || 0
})

// 解析规格参数
const productSpecs = computed(() => {
  if (!product.value?.description) return []
  return product.value.description.split(/[,，、]/).map(s => s.trim()).filter(Boolean)
})

// 详情图列表 (多张)
const detailImages = computed(() => {
  if (!product.value) return []
  const name = product.value.name
  const clean = name.replace(/[^\w一-鿿]/g, '_').replace(/_+/g, '_').toLowerCase()
  return [
    `/static/products/details/${clean}_hero.jpg`,
    `/static/products/details/${clean}_features.jpg`,
    `/static/products/details/${clean}_specs.jpg`,
    `/static/products/details/${clean}_trust.jpg`,
  ]
})

// 查找匹配的 SKU
function findSku() {
  if (!product.value?.skus?.length) {
    selectedSku.value = null
    return
  }
  const specs = selectedSpecs.value
  const sku = product.value.skus.find(s => {
    return Object.keys(specs).every(key => s.specs[key] === specs[key])
  })
  selectedSku.value = sku || null
}

// 选择规格
function selectSpec(specName, value) {
  selectedSpecs.value[specName] = value
  selectedSpecs.value = { ...selectedSpecs.value }
  findSku()
}

// 检查规格值是否可选
function isSpecValueAvailable(specName, value) {
  if (!product.value?.skus?.length) return true
  const otherSpecs = { ...selectedSpecs.value }
  delete otherSpecs[specName]
  return product.value.skus.some(sku => {
    if (sku.specs[specName] !== value) return false
    return Object.keys(otherSpecs).every(key => !otherSpecs[key] || sku.specs[key] === otherSpecs[key])
  })
}

// 初始化规格选择
function initSpecs() {
  if (product.value?.specs) {
    Object.keys(product.value.specs).forEach(key => {
      selectedSpecs.value[key] = ''
    })
  }
}

async function fetchProduct() {
  loading.value = true
  error.value = null
  try {
    const { data } = await getProduct(route.params.id)
    product.value = data
    currentImage.value = data.image_url
    initSpecs()
    fetchShopProducts()
  } catch (e) {
    error.value = e.response?.status === 404 ? '商品不存在' : '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function fetchShopProducts() {
  if (!product.value) return
  const currentId = product.value.id
  const currentShop = product.value.shop_id
  const currentCat = product.value.category

  try {
    // 1. 先取同店铺商品
    let items = []
    if (currentShop) {
      const { data } = await getProducts({ page: 1, page_size: 12, shop_id: currentShop })
      items = data.items.filter(p => p.id !== currentId)
    }

    // 2. 不足 8 个，补充同分类商品
    if (items.length < 8 && currentCat) {
      const { data } = await getProducts({ page: 1, page_size: 12, category: currentCat })
      const extras = data.items.filter(p => p.id !== currentId && !items.some(i => i.id === p.id))
      items = [...items, ...extras]
    }

    // 3. 还不足，补充其他商品
    if (items.length < 8) {
      const { data } = await getProducts({ page: 2, page_size: 12 })
      const extras = data.items.filter(p => p.id !== currentId && !items.some(i => i.id === p.id))
      items = [...items, ...extras]
    }

    shopProducts.value = items.slice(0, 8)
  } catch {}
}

async function fetchFavoriteStatus() {
  if (!userStore.token) return
  try {
    const { data } = await checkFavorite(route.params.id)
    favorited.value = data.favorited
  } catch {}
}

async function toggleFavorite() {
  if (!userStore.token) {
    router.push('/login')
    return
  }
  try {
    if (favorited.value) {
      await removeFavorite(route.params.id)
      favorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(route.params.id)
      favorited.value = true
      ElMessage.success('已收藏')
    }
  } catch {}
}

async function fetchReviews() {
  try {
    const { data } = await getProductReviews(route.params.id, {
      page: reviewPage.value,
      page_size: reviewPageSize,
    })
    reviews.value = data.items
    reviewTotal.value = data.total
    avgRating.value = data.avg_rating
  } catch {}
}

async function submitReview() {
  if (!reviewForm.value.content.trim()) {
    ElMessage.warning('请填写评价内容')
    return
  }
  reviewSubmitting.value = true
  try {
    await createReview({
      order_item_id: 0,
      rating: reviewForm.value.rating,
      content: reviewForm.value.content,
    })
    ElMessage.success('评价成功')
    showReviewForm.value = false
    reviewForm.value = { rating: 5, content: '' }
    fetchReviews()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '评价失败')
  } finally {
    reviewSubmitting.value = false
  }
}

function handleReviewPageChange(page) {
  reviewPage.value = page
  fetchReviews()
}

function addCart() {
  if (!userStore.token) {
    router.push('/login')
    return
  }
  if (product.value?.specs && Object.keys(product.value.specs).length > 0) {
    const unselected = Object.keys(product.value.specs).find(key => !selectedSpecs.value[key])
    if (unselected) {
      ElMessage.warning(`请选择${unselected}`)
      return
    }
  }
  cartStore.add(product.value.id, quantity.value, selectedSku.value ? { sku: selectedSku.value } : null)
}

function goToProduct(id) {
  router.push(`/product/${id}`)
}

onMounted(() => {
  fetchProduct()
  fetchFavoriteStatus()
  fetchReviews()
})
</script>

<template>
  <!-- 加载状态 -->
  <div v-if="loading" class="detail-loading">
    <el-skeleton :rows="10" animated />
  </div>

  <!-- 错误状态 -->
  <div v-else-if="error" class="detail-error">
    <el-icon :size="48" color="#c0c4cc"><CircleCloseFilled /></el-icon>
    <p>{{ error }}</p>
    <el-button type="primary" @click="router.push('/')">返回首页</el-button>
  </div>

  <div class="detail" v-else-if="product">
    <!-- 顶部商品信息区 -->
    <div class="detail-grid">
      <!-- 图片区域 -->
      <div class="image-section">
        <div class="main-image">
          <el-image :src="currentImage" fit="contain" class="detail-img">
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </div>
        <div class="image-list" v-if="allImages.length > 1">
          <div
            v-for="(img, idx) in allImages"
            :key="idx"
            class="image-thumb"
            :class="{ active: currentImage === img }"
            @click="currentImage = img"
          >
            <el-image :src="img" fit="cover" />
          </div>
        </div>
      </div>

      <!-- 信息区域 -->
      <div class="detail-info">
        <div class="title-row">
          <h1>{{ product.name }}</h1>
          <el-button
            :type="favorited ? 'danger' : 'default'"
            :icon="favorited ? 'StarFilled' : 'Star'"
            circle
            size="large"
            @click="toggleFavorite"
            class="fav-btn"
          />
        </div>

        <div class="price-row">
          <span class="price">¥{{ (currentPrice / 100).toFixed(2) }}</span>
          <span class="original-price" v-if="product.original_price">
            ¥{{ (product.original_price / 100).toFixed(2) }}
          </span>
          <el-tag v-if="product.is_new" type="success" size="small">新品</el-tag>
          <el-tag v-if="product.is_hot" type="danger" size="small">热销</el-tag>
        </div>

        <div class="rating-summary" v-if="reviewTotal > 0">
          <el-rate :model-value="avgRating" disabled show-score score-template="{value}" />
          <span class="review-count">{{ reviewTotal }} 条评价</span>
        </div>

        <div class="sales-info">
          <span>销量: {{ product.sales || 0 }}</span>
          <span>库存: {{ currentStock }}</span>
          <span>分类: {{ product.category || '未分类' }}</span>
        </div>

        <!-- 规格选择 -->
        <div class="specs-section" v-if="product.specs">
          <div class="spec-row" v-for="(values, specName) in product.specs" :key="specName">
            <span class="spec-label">{{ specName }}:</span>
            <div class="spec-values">
              <el-button
                v-for="value in values"
                :key="value"
                :type="selectedSpecs[specName] === value ? 'primary' : 'default'"
                :disabled="!isSpecValueAvailable(specName, value)"
                size="small"
                @click="selectSpec(specName, value)"
              >
                {{ value }}
              </el-button>
            </div>
          </div>
        </div>

        <div class="desc">{{ product.description }}</div>

        <div class="actions">
          <el-input-number v-model="quantity" :min="1" :max="currentStock" />
          <el-button type="primary" size="large" @click="addCart" :disabled="currentStock === 0">
            {{ currentStock === 0 ? '已售罄' : '加入购物车' }}
          </el-button>
          <el-button size="large" @click="router.push('/cart')">立即购买</el-button>
        </div>
      </div>
    </div>

    <!-- Tab 导航 -->
    <div class="detail-tabs-wrapper">
      <div class="detail-tabs">
        <div
          v-for="tab in [
            { key: 'detail', label: '商品详情' },
            { key: 'params', label: '规格参数' },
            { key: 'reviews', label: `用户评价(${reviewTotal})` },
            { key: 'recommend', label: '本店推荐' }
          ]"
          :key="tab.key"
          :class="['tab-item', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </div>
      </div>
    </div>

    <!-- Tab 内容 -->
    <div class="tab-content">
      <!-- 商品详情 (图文详情) -->
      <div v-show="activeTab === 'detail'" class="tab-panel">
        <div class="detail-gallery">
          <!-- 多张详情图 -->
          <div v-for="(img, idx) in detailImages" :key="idx" class="detail-image-item">
            <el-image :src="img" fit="contain" class="detail-gallery-img">
              <template #error>
                <div class="detail-img-fallback" v-if="idx === 0">
                  <p>{{ product.description }}</p>
                </div>
              </template>
            </el-image>
          </div>
        </div>
      </div>

      <!-- 规格参数 -->
      <div v-show="activeTab === 'params'" class="tab-panel">
        <div class="params-table">
          <div class="params-header">
            <span class="params-key">参数名</span>
            <span class="params-val">详情</span>
          </div>
          <div
            v-for="(spec, idx) in productSpecs"
            :key="idx"
            :class="['params-row', { even: idx % 2 === 0 }]"
          >
            <span class="params-key">{{ spec.split(/[:：]/)[0] || '参数' }}</span>
            <span class="params-val">{{ spec.split(/[:：]/)[1] || spec }}</span>
          </div>
          <div class="params-row" v-if="product.category">
            <span class="params-key">商品分类</span>
            <span class="params-val">{{ product.category }}</span>
          </div>
          <div class="params-row even" v-if="product.shop_id">
            <span class="params-key">店铺</span>
            <span class="params-val">MallHub 旗舰店</span>
          </div>
        </div>
      </div>

      <!-- 用户评价 -->
      <div v-show="activeTab === 'reviews'" class="tab-panel">
        <div class="reviews-header">
          <div class="rating-overview">
            <div class="rating-big">{{ avgRating }}</div>
            <el-rate :model-value="avgRating" disabled />
            <div class="review-total">{{ reviewTotal }} 条评价</div>
          </div>
          <el-button v-if="userStore.token" @click="showReviewForm = true">写评价</el-button>
        </div>

        <div class="review-list" v-if="reviews.length">
          <div class="review-item" v-for="r in reviews" :key="r.id">
            <div class="review-user">
              <el-avatar :size="40" :src="r.avatar || '/images/misc/default-avatar.svg'">
                {{ r.username?.[0]?.toUpperCase() }}
              </el-avatar>
              <span class="review-username">{{ r.username }}</span>
            </div>
            <div class="review-body">
              <div class="review-meta">
                <el-rate :model-value="r.rating" disabled size="small" />
                <span class="review-time">{{ new Date(r.created_at).toLocaleDateString() }}</span>
              </div>
              <p class="review-content">{{ r.content }}</p>
            </div>
          </div>
          <el-pagination
            v-if="reviewTotal > reviewPageSize"
            :current-page="reviewPage"
            :page-size="reviewPageSize"
            :total="reviewTotal"
            layout="prev, pager, next"
            @current-change="handleReviewPageChange"
            class="review-pagination"
          />
        </div>
        <el-empty v-else description="暂无评价" />
      </div>

      <!-- 本店推荐 -->
      <div v-show="activeTab === 'recommend'" class="tab-panel">
        <div class="recommend-grid" v-if="shopProducts.length">
          <div
            v-for="p in shopProducts"
            :key="p.id"
            class="recommend-card"
            @click="goToProduct(p.id)"
          >
            <el-image :src="p.image_url" fit="cover" class="recommend-img" />
            <div class="recommend-info">
              <div class="recommend-name">{{ p.name }}</div>
              <div class="recommend-price">¥{{ (p.price / 100).toFixed(2) }}</div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无推荐" />
      </div>
    </div>

    <!-- 评价对话框 -->
    <el-dialog v-model="showReviewForm" title="写评价" width="500px">
      <el-form :model="reviewForm" label-width="60px">
        <el-form-item label="评分">
          <el-rate v-model="reviewForm.rating" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="reviewForm.content" type="textarea" :rows="4" placeholder="分享你的使用体验..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewForm = false">取消</el-button>
        <el-button type="primary" :loading="reviewSubmitting" @click="submitReview">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.detail {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f5f5;
  min-height: 100vh;
}

.detail-grid {
  display: flex;
  gap: 24px;
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 16px;
}

/* 图片区域 */
.image-section {
  width: 400px;
  flex-shrink: 0;
}

.main-image {
  width: 400px;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  background: #f9f9f9;
  border: 1px solid #eee;
}

.detail-img {
  width: 100%;
  height: 100%;
}

.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 48px;
}

.image-list {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.image-thumb {
  width: 60px;
  height: 60px;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
}

.image-thumb.active {
  border-color: #e4393c;
}

.image-thumb:hover {
  border-color: #e4393c;
}

.image-thumb .el-image {
  width: 100%;
  height: 100%;
}

/* 信息区域 */
.detail-info {
  flex: 1;
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.title-row h1 {
  margin: 0;
  font-size: 20px;
  line-height: 1.5;
  color: #333;
  font-weight: 600;
}

.fav-btn {
  flex-shrink: 0;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 16px 0 12px;
  padding: 12px 16px;
  background: #fef0f0;
  border-radius: 6px;
}

.price {
  color: #e4393c;
  font-size: 28px;
  font-weight: bold;
}

.original-price {
  color: #999;
  font-size: 14px;
  text-decoration: line-through;
}

.rating-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.review-count {
  color: #999;
  font-size: 13px;
}

.sales-info {
  display: flex;
  gap: 24px;
  color: #666;
  font-size: 13px;
  margin-bottom: 16px;
}

/* 规格选择 */
.specs-section {
  margin: 16px 0;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.spec-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.spec-row:last-child {
  margin-bottom: 0;
}

.spec-label {
  color: #666;
  min-width: 60px;
  font-size: 14px;
}

.spec-values {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.desc {
  margin: 12px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

/* Tab 导航 */
.detail-tabs-wrapper {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.detail-tabs {
  display: flex;
  border-bottom: 2px solid #e4393c;
}

.tab-item {
  padding: 14px 28px;
  font-size: 15px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.tab-item:hover {
  color: #e4393c;
}

.tab-item.active {
  color: #fff;
  background: #e4393c;
  font-weight: 600;
}

/* Tab 内容 */
.tab-content {
  background: #fff;
  border-radius: 8px;
  min-height: 400px;
}

.tab-panel {
  padding: 24px;
}

/* 图文详情 */
.detail-gallery {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.detail-image-item {
  width: 100%;
  max-width: 800px;
  margin-bottom: 16px;
}

.detail-gallery-img {
  width: 100%;
}

.detail-img-fallback {
  padding: 40px;
  text-align: center;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
}

/* 规格参数表 */
.params-table {
  max-width: 800px;
}

.params-header {
  display: flex;
  background: #f5f5f5;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 14px;
  color: #333;
  border-radius: 4px 4px 0 0;
}

.params-row {
  display: flex;
  padding: 12px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f0f0f0;
}

.params-row.even {
  background: #fafafa;
}

.params-key {
  width: 200px;
  color: #999;
  flex-shrink: 0;
}

.params-val {
  flex: 1;
  color: #333;
}

/* 用户评价 */
.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.rating-overview {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rating-big {
  font-size: 36px;
  font-weight: bold;
  color: #f7ba2a;
}

.review-total {
  color: #999;
  font-size: 14px;
}

.review-list {
  margin-top: 16px;
}

.review-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.review-user {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 70px;
}

.review-username {
  font-size: 12px;
  color: #666;
}

.review-body {
  flex: 1;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.review-content {
  margin: 0;
  color: #333;
  line-height: 1.6;
  font-size: 14px;
}

.review-time {
  font-size: 12px;
  color: #999;
}

.review-pagination {
  margin-top: 20px;
  justify-content: center;
  display: flex;
}

/* 本店推荐 */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.recommend-card {
  cursor: pointer;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.recommend-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.recommend-img {
  width: 100%;
  height: 200px;
}

.recommend-info {
  padding: 12px;
}

.recommend-name {
  font-size: 13px;
  color: #333;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recommend-price {
  color: #e4393c;
  font-size: 16px;
  font-weight: bold;
}

/* 加载和错误状态 */
.detail-loading {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
  background: #fff;
  border-radius: 8px;
}

.detail-error {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 24px;
  text-align: center;
  background: #fff;
  border-radius: 8px;
}

.detail-error p {
  margin: 16px 0;
  color: #666;
  font-size: 16px;
}

@media (max-width: 768px) {
  .detail-grid {
    flex-direction: column;
  }

  .image-section {
    width: 100%;
  }

  .main-image {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
  }

  .recommend-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
