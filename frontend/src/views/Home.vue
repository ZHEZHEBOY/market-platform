<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts } from '../api/product'
import ProductCard from '../components/ProductCard.vue'

const router = useRouter()

const hotProducts = ref([])
const newProducts = ref([])
const recommendProducts = ref([])
const categories = ref([])
const loading = ref(true)

const banners = [
  { title: '新品首发', subtitle: '探索最新好物', gradient: 'linear-gradient(135deg, #FF6700, #FF8533)' },
  { title: '限时特惠', subtitle: '品质好物 超值价格', gradient: 'linear-gradient(135deg, #1a1a2e, #16213e)' },
  { title: '品质生活', subtitle: '精选好物 品质之选', gradient: 'linear-gradient(135deg, #2d6a4f, #40916c)' },
]

async function fetchData() {
  loading.value = true
  try {
    const [hotRes, newRes, recRes, catRes] = await Promise.all([
      getProducts({ page: 1, page_size: 8, sort: 'sales' }),
      getProducts({ page: 1, page_size: 8, sort: 'newest' }),
      getProducts({ page: 1, page_size: 8, sort: 'newest' }),
      getProducts({ page: 1, page_size: 100 }),
    ])
    hotProducts.value = hotRes.data.items
    newProducts.value = newRes.data.items
    recommendProducts.value = recRes.data.items
    // extract unique categories
    const catSet = new Set()
    catRes.data.items.forEach(p => { if (p.category) catSet.add(p.category) })
    categories.value = [...catSet]
  } finally {
    loading.value = false
  }
}

function goSearch(keyword) {
  router.push({ path: '/search', query: { keyword } })
}

function goCategory(cat) {
  router.push({ path: '/search', query: { category: cat } })
}

onMounted(fetchData)
</script>

<template>
  <div class="home" v-loading="loading">
    <!-- Banner -->
    <section class="banner-section">
      <el-carousel height="480px" :interval="5000" arrow="hover">
        <el-carousel-item v-for="(b, i) in banners" :key="i">
          <div class="banner-slide" :style="{ background: b.gradient }">
            <div class="banner-content">
              <h1>{{ b.title }}</h1>
              <p>{{ b.subtitle }}</p>
              <el-button round size="large" class="banner-btn" @click="goSearch('')">立即选购</el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <!-- Categories -->
    <section class="section categories-section" v-if="categories.length">
      <div class="container">
        <div class="categories-grid">
          <div
            v-for="cat in categories"
            :key="cat"
            class="category-item"
            @click="goCategory(cat)"
          >
            <div class="category-icon">
              <el-icon :size="28"><Grid /></el-icon>
            </div>
            <span>{{ cat }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Hot Products -->
    <section class="section" v-if="hotProducts.length">
      <div class="container">
        <div class="section-header">
          <h2>热销推荐</h2>
          <span class="section-more" @click="goSearch('')">查看更多 &gt;</span>
        </div>
        <div class="products-grid">
          <ProductCard v-for="p in hotProducts" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <!-- New Products -->
    <section class="section" v-if="newProducts.length">
      <div class="container">
        <div class="section-header">
          <h2>新品上架</h2>
          <span class="section-more" @click="goSearch('')">查看更多 &gt;</span>
        </div>
        <div class="products-grid">
          <ProductCard v-for="p in newProducts" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <!-- Recommended -->
    <section class="section" v-if="recommendProducts.length">
      <div class="container">
        <div class="section-header">
          <h2>为你推荐</h2>
          <span class="section-more" @click="goSearch('')">查看更多 &gt;</span>
        </div>
        <div class="products-grid">
          <ProductCard v-for="p in recommendProducts" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-brand">
            <span class="footer-logo">Market</span>
            <p>品质好物，美好生活</p>
          </div>
          <div class="footer-links">
            <div class="footer-col">
              <h4>购物指南</h4>
              <p>注册登录</p>
              <p>购物流程</p>
              <p>支付方式</p>
            </div>
            <div class="footer-col">
              <h4>售后服务</h4>
              <p>退换货政策</p>
              <p>物流配送</p>
              <p>常见问题</p>
            </div>
            <div class="footer-col">
              <h4>关于我们</h4>
              <p>公司介绍</p>
              <p>联系我们</p>
              <p>加入我们</p>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 Market Platform. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
}

.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 20px;
}

.section {
  padding: 40px 0;
}

/* Banner */
.banner-section {
  margin-bottom: 0;
}

.banner-slide {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-content {
  text-align: center;
  color: #fff;
}

.banner-content h1 {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 16px;
  letter-spacing: 2px;
}

.banner-content p {
  font-size: 20px;
  margin: 0 0 32px;
  opacity: 0.9;
}

.banner-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 2px solid #fff !important;
  color: #fff !important;
  padding: 12px 40px !important;
  font-size: 16px !important;
  backdrop-filter: blur(4px);
}

.banner-btn:hover {
  background: rgba(255, 255, 255, 0.35) !important;
}

/* Categories */
.categories-section {
  padding: 32px 0;
  background: var(--color-bg-white);
}

.categories-grid {
  display: flex;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.2s;
}

.category-item:hover {
  transform: translateY(-2px);
}

.category-item:hover .category-icon {
  background: var(--color-primary);
  color: #fff;
}

.category-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.category-item span {
  font-size: 14px;
  color: var(--color-text);
}

/* Section Header */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
}

.section-more {
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s;
}

.section-more:hover {
  color: var(--color-primary);
}

/* Products Grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

/* Footer */
.footer {
  background: #2a2a2a;
  color: #ccc;
  padding: 48px 0 0;
  margin-top: 40px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  gap: 60px;
  padding-bottom: 40px;
}

.footer-brand {
  flex-shrink: 0;
}

.footer-logo {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
}

.footer-brand p {
  margin: 12px 0 0;
  font-size: 14px;
  color: #999;
}

.footer-links {
  display: flex;
  gap: 80px;
}

.footer-col h4 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #fff;
}

.footer-col p {
  margin: 0 0 10px;
  font-size: 13px;
  color: #999;
  cursor: pointer;
}

.footer-col p:hover {
  color: #fff;
}

.footer-bottom {
  border-top: 1px solid #3a3a3a;
  padding: 20px 0;
  text-align: center;
}

.footer-bottom p {
  margin: 0;
  font-size: 13px;
  color: #666;
}

@media (max-width: 960px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
