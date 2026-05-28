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
      <el-image
        v-if="product.image_url"
        :src="product.image_url"
        :alt="product.name"
        lazy
        fit="cover"
      >
        <template #error>
          <div class="image-error">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <div v-else class="image-placeholder">
        <span>{{ product.name?.[0] || '?' }}</span>
      </div>
      <div class="card-tags">
        <el-tag v-if="product.is_new" type="success" size="small">新品</el-tag>
        <el-tag v-if="product.is_hot" type="danger" size="small">热销</el-tag>
      </div>
    </div>
    <div class="card-body">
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="product-desc">{{ product.description || '暂无描述' }}</p>
      <div class="product-footer">
        <div class="price-group">
          <span class="product-price">¥{{ formatPrice(product.price) }}</span>
          <span class="product-original-price" v-if="product.original_price">
            ¥{{ formatPrice(product.original_price) }}
          </span>
        </div>
        <span class="product-sales" v-if="product.sales">已售{{ product.sales }}</span>
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
  position: relative;
}

.card-image .el-image {
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
  font-size: 36px;
}

.card-tags {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  gap: 4px;
}

.product-card:hover :deep(.el-image__inner) {
  transform: scale(1.05);
  transition: transform 0.3s ease;
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
  align-items: flex-end;
  justify-content: space-between;
}

.price-group {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.product-price {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-price);
}

.product-original-price {
  font-size: 12px;
  color: #999;
  text-decoration: line-through;
}

.product-sales {
  font-size: 12px;
  color: #999;
}
</style>
