<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNotifications, markAsRead, markAllAsRead, deleteNotification } from '../api/notification'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const notifications = ref([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)

const typeMap = {
  system: { label: '系统通知', color: '#909399' },
  order: { label: '订单通知', color: '#409EFF' },
  promotion: { label: '促销活动', color: '#E6A23C' },
}

async function fetchNotifications() {
  loading.value = true
  try {
    const { data } = await getNotifications({ page: page.value, page_size: 20 })
    notifications.value = data
  } finally {
    loading.value = false
  }
}

async function handleMarkAsRead(id) {
  await markAsRead(id)
  const item = notifications.value.find(n => n.id === id)
  if (item) item.is_read = true
}

async function handleMarkAllAsRead() {
  await markAllAsRead()
  notifications.value.forEach(n => n.is_read = true)
  ElMessage.success('已全部标记为已读')
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定要删除这条消息吗？', '提示')
  await deleteNotification(id)
  notifications.value = notifications.value.filter(n => n.id !== id)
  ElMessage.success('已删除')
}

function handleClick(item) {
  if (!item.is_read) {
    handleMarkAsRead(item.id)
  }
  if (item.link) {
    router.push(item.link)
  }
}

function formatTime(isoStr) {
  if (!isoStr) return ''
  const date = new Date(isoStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(fetchNotifications)
</script>

<template>
  <div class="notifications-page">
    <div class="container">
      <div class="page-header">
        <h2>消息中心</h2>
        <el-button size="small" @click="handleMarkAllAsRead">全部已读</el-button>
      </div>

      <div class="notification-list" v-loading="loading">
        <template v-if="notifications.length">
          <div
            v-for="item in notifications"
            :key="item.id"
            :class="['notification-item', { unread: !item.is_read }]"
            @click="handleClick(item)"
          >
            <div class="notification-dot" v-if="!item.is_read"></div>
            <div class="notification-content">
              <div class="notification-header">
                <el-tag :color="typeMap[item.type]?.color" size="small" effect="dark">
                  {{ typeMap[item.type]?.label || '通知' }}
                </el-tag>
                <span class="notification-time">{{ formatTime(item.created_at) }}</span>
              </div>
              <div class="notification-title">{{ item.title }}</div>
              <div class="notification-text">{{ item.content }}</div>
            </div>
            <el-button
              size="small"
              type="danger"
              text
              @click.stop="handleDelete(item.id)"
            >
              删除
            </el-button>
          </div>
        </template>

        <el-empty v-else-if="!loading" description="暂无消息" />
      </div>

      <div class="pagination" v-if="total > 20">
        <el-pagination
          v-model:current-page="page"
          :page-size="20"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="fetchNotifications"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications-page {
  padding: 24px 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.notification-item:hover {
  box-shadow: var(--shadow-card-hover);
}

.notification-item.unread {
  background: #f0f7ff;
}

.notification-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  flex-shrink: 0;
  margin-top: 6px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.notification-time {
  font-size: 12px;
  color: var(--color-text-light);
}

.notification-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.notification-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
