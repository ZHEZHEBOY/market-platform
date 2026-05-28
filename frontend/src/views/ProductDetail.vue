<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProduct } from '../api/product'
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
  const { data } = await getProduct(route.params.id)
  product.value = data
  currentImage.value = data.image_url
  initSpecs()
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
  // 检查是否需要选择规格
  if (product.value?.specs && Object.keys(product.value.specs).length > 0) {
    const unselected = Object.keys(product.value.specs).find(key => !selectedSpecs.value[key])
    if (unselected) {
      ElMessage.warning(`请选择${unselected}`)
      return
    }
  }
  cartStore.add(product.value.id, quantity.value, selectedSku.value ? { sku: selectedSku.value } : null)
}

onMounted(() => {
  fetchProduct()
  fetchFavoriteStatus()
  fetchReviews()
})
</script>

<template>
  <div class="detail" v-if="product">
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

    <!-- 评价区域 -->
    <div class="review-section">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商品详情" name="detail">
          <div class="detail-content">
            <p>{{ product.description }}</p>
          </div>
        </el-tab-pane>
        <el-tab-pane :label="`商品评价(${reviewTotal})`" name="reviews">
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
                <el-avatar :size="36" :src="r.avatar || '/images/misc/default-avatar.svg'">
                  {{ r.username?.[0]?.toUpperCase() }}
                </el-avatar>
                <span class="review-username">{{ r.username }}</span>
              </div>
              <div class="review-body">
                <el-rate :model-value="r.rating" disabled size="small" />
                <p class="review-content">{{ r.content }}</p>
                <span class="review-time">{{ new Date(r.created_at).toLocaleDateString() }}</span>
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
        </el-tab-pane>
      </el-tabs>
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
.detail { padding: 40px; max-width: 1200px; margin: 0 auto; }
.detail-grid { display: flex; gap: 40px; }

/* 图片区域 */
.image-section { width: 450px; flex-shrink: 0; }
.main-image { width: 450px; height: 450px; border-radius: 8px; overflow: hidden; background: #f5f5f5; }
.detail-img { width: 100%; height: 100%; }
.image-error { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #c0c4cc; font-size: 48px; }
.image-list { display: flex; gap: 8px; margin-top: 12px; }
.image-thumb { width: 60px; height: 60px; border: 2px solid transparent; border-radius: 4px; overflow: hidden; cursor: pointer; transition: border-color 0.2s; }
.image-thumb.active { border-color: var(--color-primary); }
.image-thumb:hover { border-color: var(--color-primary); }
.image-thumb .el-image { width: 100%; height: 100%; }

/* 信息区域 */
.detail-info { flex: 1; }
.title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.title-row h1 { margin: 0; font-size: 22px; line-height: 1.4; }
.fav-btn { flex-shrink: 0; }

.price-row { display: flex; align-items: baseline; gap: 12px; margin: 16px 0 12px; }
.price { color: #e4393c; font-size: 28px; font-weight: bold; }
.original-price { color: #999; font-size: 16px; text-decoration: line-through; }

.rating-summary { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.review-count { color: #999; font-size: 13px; }

.sales-info { display: flex; gap: 24px; color: #666; font-size: 14px; margin-bottom: 20px; }

/* 规格选择 */
.specs-section { margin: 20px 0; padding: 16px; background: #f9f9f9; border-radius: 8px; }
.spec-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.spec-row:last-child { margin-bottom: 0; }
.spec-label { color: #666; min-width: 60px; }
.spec-values { display: flex; flex-wrap: wrap; gap: 8px; }

.desc { margin: 16px 0; color: #333; line-height: 1.6; }
.actions { display: flex; gap: 12px; align-items: center; margin-top: 24px; }

/* 评价区域 */
.review-section { margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; }
.reviews-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 0; }
.rating-overview { display: flex; align-items: center; gap: 12px; }
.rating-big { font-size: 36px; font-weight: bold; color: #f7ba2a; }
.review-total { color: #999; font-size: 14px; }
.review-list { margin-top: 16px; }
.review-item { display: flex; gap: 12px; padding: 16px 0; border-bottom: 1px solid #f0f0f0; }
.review-user { display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 60px; }
.review-username { font-size: 12px; color: #666; }
.review-body { flex: 1; }
.review-content { margin: 8px 0 4px; color: #333; line-height: 1.6; }
.review-time { font-size: 12px; color: #999; }
.review-pagination { margin-top: 16px; justify-content: center; display: flex; }
.detail-content { padding: 20px 0; color: #333; line-height: 1.8; }
</style>
