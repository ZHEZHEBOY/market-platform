<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts } from '../api/product'
import ProductCard from '../components/ProductCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'

const router = useRouter()

const hotProducts = ref([])
const newProducts = ref([])
const recommendProducts = ref([])
const categories = ref([])
const loading = ref(true)

// 品牌专区数据
const brandZones = [
  {
    name: 'Apple',
    color: '#1A1A1A',
    gradient: 'linear-gradient(135deg, #1a1a1a, #333)',
    slogan: '创新无止境',
    keywords: ['iPhone', 'MacBook', 'iPad', 'AirPods', 'Apple Watch'],
  },
  {
    name: '小米',
    color: '#FF6900',
    gradient: 'linear-gradient(135deg, #FF6900, #FF8C00)',
    slogan: '让每个人都能享受科技的乐趣',
    keywords: ['小米', 'Redmi'],
  },
  {
    name: '华为',
    color: '#CF0A2C',
    gradient: 'linear-gradient(135deg, #CF0A2C, #E8384F)',
    slogan: '构建万物互联的智能世界',
    keywords: ['华为', 'Mate'],
  },
  {
    name: '三星',
    color: '#1428A0',
    gradient: 'linear-gradient(135deg, #1428A0, #1E3FCC)',
    slogan: 'Do what you can\'t',
    keywords: ['三星', 'Galaxy'],
  },
]

const brandProducts = ref({})

async function fetchBrandProducts() {
  for (const brand of brandZones) {
    try {
      const { data } = await getProducts({ keyword: brand.keywords[0], page: 1, page_size: 4 })
      brandProducts.value[brand.name] = data.items
    } catch {
      brandProducts.value[brand.name] = []
    }
  }
}

function goBrand(brand) {
  router.push({ path: '/search', query: { keyword: brand.keywords[0] } })
}

const banners = [
  { title: '新品首发', subtitle: '探索最新好物', image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&h=480&fit=crop' },
  { title: '限时特惠', subtitle: '品质好物 超值价格', image: 'https://images.unsplash.com/photo-1607082349566-187342175e2f?w=1200&h=480&fit=crop' },
  { title: '品质生活', subtitle: '精选好物 品质之选', image: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&h=480&fit=crop' },
]

const categoryIcons = {
  '手机通讯': '/images/categories/phone.svg',
  '电脑办公': '/images/categories/laptop.svg',
  '数码配件': '/images/categories/headphone.svg',
  '智能设备': '/images/categories/watch.svg',
  '家用电器': '/images/categories/appliance.svg',
  '厨房电器': '/images/categories/kitchen.svg',
  '个护美妆': '/images/categories/beauty.svg',
  '服饰鞋包': '/images/categories/clothing.svg',
  '食品饮料': '/images/categories/food.svg',
  '生鲜果蔬': '/images/categories/fruit.svg',
  '运动户外': '/images/categories/sport.svg',
  '家居日用': '/images/categories/home.svg',
  '图书文具': '/images/categories/book.svg',
  '母婴玩具': '/images/categories/baby.svg',
}

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

    // 获取品牌专区商品
    await fetchBrandProducts()
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
  <div class="home">
    <!-- Banner -->
    <section class="banner-section">
      <el-carousel height="480px" :interval="5000" arrow="hover">
        <el-carousel-item v-for="(b, i) in banners" :key="i">
          <div class="banner-slide" :style="{ backgroundImage: `url(${b.image})` }">
            <div class="banner-overlay">
              <div class="banner-content">
                <h1>{{ b.title }}</h1>
                <p>{{ b.subtitle }}</p>
                <el-button round size="large" class="banner-btn" @click="goSearch('')">立即选购</el-button>
              </div>
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
              <img v-if="categoryIcons[cat]" :src="categoryIcons[cat]" :alt="cat" />
              <el-icon v-else :size="28"><Grid /></el-icon>
            </div>
            <span>{{ cat }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Brand Zones -->
    <section class="section brand-section">
      <div class="container">
        <div class="section-header">
          <h2>品牌专区</h2>
          <span class="section-more">大牌正品 品质保障</span>
        </div>
        <div class="brand-grid">
          <div
            v-for="brand in brandZones"
            :key="brand.name"
            class="brand-card"
            :style="{ background: brand.gradient }"
            @click="goBrand(brand)"
          >
            <div class="brand-info">
              <h3 class="brand-name">{{ brand.name }}</h3>
              <p class="brand-slogan">{{ brand.slogan }}</p>
              <el-button round size="small" class="brand-btn">进入专区</el-button>
            </div>
            <div class="brand-products">
              <div
                v-for="p in (brandProducts[brand.name] || []).slice(0, 2)"
                :key="p.id"
                class="brand-product-mini"
              >
                <el-image :src="p.image_url" fit="cover" class="brand-product-img" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Hot Products -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <h2>热销推荐</h2>
          <span class="section-more" @click="goSearch('')">查看更多 &gt;</span>
        </div>
        <div class="products-grid">
          <template v-if="loading">
            <SkeletonCard v-for="i in 8" :key="i" />
          </template>
          <template v-else>
            <ProductCard v-for="p in hotProducts" :key="p.id" :product="p" />
          </template>
        </div>
      </div>
    </section>

    <!-- New Products -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <h2>新品上架</h2>
          <span class="section-more" @click="goSearch('')">查看更多 &gt;</span>
        </div>
        <div class="products-grid">
          <template v-if="loading">
            <SkeletonCard v-for="i in 8" :key="i" />
          </template>
          <template v-else>
            <ProductCard v-for="p in newProducts" :key="p.id" :product="p" />
          </template>
        </div>
      </div>
    </section>

    <!-- Recommended -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <h2>为你推荐</h2>
          <span class="section-more" @click="goSearch('')">查看更多 &gt;</span>
        </div>
        <div class="products-grid">
          <template v-if="loading">
            <SkeletonCard v-for="i in 8" :key="i" />
          </template>
          <template v-else>
            <ProductCard v-for="p in recommendProducts" :key="p.id" :product="p" />
          </template>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-brand">
            <span class="footer-logo">MallHub</span>
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
          <p>&copy; 2026 MallHub. All rights reserved.</p>
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
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
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

/* Brand Section */
.brand-section {
  background: #f8f9fa;
  padding: 48px 0;
}

.brand-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.brand-card {
  border-radius: 16px;
  padding: 28px;
  color: #fff;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.3s, box-shadow 0.3s;
  min-height: 160px;
}

.brand-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.brand-info {
  flex: 1;
}

.brand-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
}

.brand-slogan {
  font-size: 14px;
  opacity: 0.85;
  margin: 0 0 16px;
}

.brand-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: #fff;
}

.brand-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.brand-products {
  display: flex;
  gap: 12px;
  margin-left: 20px;
}

.brand-product-mini {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.15);
}

.brand-product-img {
  width: 100%;
  height: 100%;
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
  overflow: hidden;
}

.category-icon img {
  width: 40px;
  height: 40px;
  object-fit: contain;
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
