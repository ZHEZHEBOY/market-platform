<script setup>
import { ref, onMounted, computed } from 'vue'
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

async function fetchProduct() {
  const { data } = await getProduct(route.params.id)
  product.value = data
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
  cartStore.add(product.value.id, quantity.value)
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
      <img :src="product.image_url || '/vite.svg'" class="detail-img" />
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
        <p class="price">¥{{ (product.price / 100).toFixed(2) }}</p>
        <div class="rating-summary" v-if="reviewTotal > 0">
          <el-rate :model-value="avgRating" disabled show-score score-template="{value}" />
          <span class="review-count">{{ reviewTotal }} 条评价</span>
        </div>
        <p class="stock">库存: {{ product.stock }}</p>
        <p class="category">分类: {{ product.category || '未分类' }}</p>
        <div class="desc">{{ product.description }}</div>
        <div class="actions">
          <el-input-number v-model="quantity" :min="1" :max="product.stock" />
          <el-button type="primary" size="large" @click="addCart" :disabled="product.stock === 0">
            {{ product.stock === 0 ? '已售罄' : '加入购物车' }}
          </el-button>
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
          </div>

          <div class="review-list" v-if="reviews.length">
            <div class="review-item" v-for="r in reviews" :key="r.id">
              <div class="review-user">
                <el-avatar :size="36" :src="r.avatar || ''">{{ r.username?.[0]?.toUpperCase() }}</el-avatar>
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
  </div>
</template>

<style scoped>
.detail { padding: 40px; max-width: 1000px; margin: 0 auto; }
.detail-grid { display: flex; gap: 40px; }
.detail-img { width: 400px; height: 400px; object-fit: cover; border-radius: 8px; }
.detail-info { flex: 1; }
.title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.title-row h1 { margin: 0; flex: 1; }
.fav-btn { flex-shrink: 0; }
.price { color: #e4393c; font-size: 28px; font-weight: bold; margin: 12px 0 8px; }
.rating-summary { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.review-count { color: #999; font-size: 13px; }
.stock, .category { color: #666; margin: 0 0 8px; }
.desc { margin: 16px 0; color: #333; line-height: 1.6; }
.actions { display: flex; gap: 12px; align-items: center; margin-top: 20px; }

.review-section { margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; }
.reviews-header { padding: 16px 0; }
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
