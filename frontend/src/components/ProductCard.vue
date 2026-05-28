<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  product: { type: Object, required: true }
})

const router = useRouter()

function formatPrice(cents) {
  return (cents / 100).toFixed(2)
}

function handleClick() {
  router.push(`/product/${props.product.id}`)
}
</script>

<template>
  <div class="product-card" @click="handleClick">
    <div class="card-image">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
      <div v-else class="image-placeholder">
        <span>{{ product.name[0] }}</span>
      </div>
    </div>
    <div class="card-body">
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="product-desc">{{ product.description || '暂无描述' }}</p>
      <div class="product-footer">
        <span class="product-price">¥{{ formatPrice(product.price) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
}

.card-image {
  width: 100%;
  aspect-ratio: 1;
  background: #f0f0f0;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5, #e8e8e8);
}

.image-placeholder span {
  font-size: 48px;
  font-weight: 600;
  color: #d0d0d0;
}

.card-body {
  padding: 16px;
}

.product-name {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  margin: 0 0 10px;
  font-size: 12px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.product-price {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-price);
}
</style>
