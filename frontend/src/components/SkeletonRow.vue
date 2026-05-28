<template>
  <div class="skeleton-row">
    <div class="skeleton-cell" v-for="i in columns" :key="i" :style="{ width: widths[i-1] || 'auto' }">
      <div class="skeleton-bar" :style="{ height: height + 'px' }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Number, default: 4 },
  widths: { type: Array, default: () => [] },
  height: { type: Number, default: 16 }
})
</script>

<style scoped>
.skeleton-row {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.skeleton-cell {
  flex-shrink: 0;
}

.skeleton-bar {
  width: 100%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
