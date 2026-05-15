<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProduct } from '../api/product'
import { useCartStore } from '../stores/cart'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

const product = ref(null)
const quantity = ref(1)

async function fetchProduct() {
  const { data } = await getProduct(route.params.id)
  product.value = data
}

async function addCart() {
  if (!userStore.token) {
    router.push('/login')
    return
  }
  await cartStore.add(product.value.id, quantity.value)
}

onMounted(fetchProduct)
</script>

<template>
  <div class="detail" v-if="product">
    <div class="detail-grid">
      <img :src="product.image_url || '/vite.svg'" class="detail-img" />
      <div class="detail-info">
        <h1>{{ product.name }}</h1>
        <p class="price">¥{{ (product.price / 100).toFixed(2) }}</p>
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
  </div>
</template>

<style scoped>
.detail { padding: 40px; max-width: 1000px; margin: 0 auto; }
.detail-grid { display: flex; gap: 40px; }
.detail-img { width: 400px; height: 400px; object-fit: cover; border-radius: 8px; }
.detail-info h1 { margin: 0 0 12px; }
.price { color: #e4393c; font-size: 28px; font-weight: bold; margin: 0 0 8px; }
.stock, .category { color: #666; margin: 0 0 8px; }
.desc { margin: 16px 0; color: #333; line-height: 1.6; }
.actions { display: flex; gap: 12px; align-items: center; margin-top: 20px; }
</style>
