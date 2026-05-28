<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { updateMe, changePassword } from '../api/auth'
import { ElMessage } from 'element-plus'
import api from '../api/index'

const router = useRouter()
const userStore = useUserStore()

const activeMenu = ref('profile')
const email = ref('')
const avatarUrl = ref('')
const loading = ref(false)

// Password form
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const pwdLoading = ref(false)

const user = computed(() => userStore.user)

onMounted(() => {
  if (user.value) {
    email.value = user.value.email || ''
    avatarUrl.value = user.value.avatar || ''
  }
})

async function handleSaveProfile() {
  loading.value = true
  try {
    const { data } = await updateMe({ email: email.value })
    userStore.user = data
    localStorage.setItem('user', JSON.stringify(data))
    ElMessage.success('资料已更新')
  } finally {
    loading.value = false
  }
}

async function handleAvatarUpload(options) {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const { data } = await api.post('/api/auth/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    avatarUrl.value = data.url
    userStore.user.avatar = data.url
    localStorage.setItem('user', JSON.stringify(userStore.user))
    ElMessage.success('头像已更新')
  } catch {
    ElMessage.error('上传失败')
  }
}

async function handleChangePassword() {
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  if (pwdForm.value.new_password.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  pwdLoading.value = true
  try {
    await changePassword({
      old_password: pwdForm.value.old_password,
      new_password: pwdForm.value.new_password,
    })
    ElMessage.success('密码修改成功')
    pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } finally {
    pwdLoading.value = false
  }
}
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <div class="profile-layout">
        <!-- Sidebar -->
        <aside class="profile-sidebar">
          <div class="user-card">
            <el-avatar :size="64" :src="avatarUrl">
              {{ user?.username?.[0]?.toUpperCase() }}
            </el-avatar>
            <h3>{{ user?.username }}</h3>
            <p>{{ user?.email }}</p>
          </div>
          <nav class="sidebar-menu">
            <div :class="['menu-item', { active: activeMenu === 'profile' }]" @click="activeMenu = 'profile'">
              <el-icon><User /></el-icon>个人资料
            </div>
            <div :class="['menu-item', { active: activeMenu === 'password' }]" @click="activeMenu = 'password'">
              <el-icon><Lock /></el-icon>修改密码
            </div>
            <div class="menu-item" @click="router.push('/orders')">
              <el-icon><List /></el-icon>我的订单
            </div>
            <div class="menu-item" @click="router.push('/address')">
              <el-icon><Location /></el-icon>收货地址
            </div>
          </nav>
        </aside>

        <!-- Content -->
        <main class="profile-content">
          <!-- Profile Form -->
          <div v-if="activeMenu === 'profile'" class="content-card">
            <h2>个人资料</h2>
            <div class="avatar-section">
              <el-avatar :size="80" :src="avatarUrl">
                {{ user?.username?.[0]?.toUpperCase() }}
              </el-avatar>
              <el-upload
                :show-file-list="false"
                :http-request="handleAvatarUpload"
                accept="image/*"
              >
                <el-button size="small">更换头像</el-button>
              </el-upload>
            </div>

            <el-form label-width="80px" class="profile-form">
              <el-form-item label="用户名">
                <el-input :model-value="user?.username" disabled />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="email" placeholder="请输入邮箱" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="loading" @click="handleSaveProfile">保存修改</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- Password Form -->
          <div v-if="activeMenu === 'password'" class="content-card">
            <h2>修改密码</h2>
            <el-form label-width="100px" class="profile-form">
              <el-form-item label="当前密码">
                <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入当前密码" />
              </el-form-item>
              <el-form-item label="新密码">
                <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="请输入新密码（至少6位）" />
              </el-form-item>
              <el-form-item label="确认新密码">
                <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="pwdLoading" @click="handleChangePassword">确认修改</el-button>
              </el-form-item>
            </el-form>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 24px 0;
}

.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 20px;
}

.profile-layout {
  display: flex;
  gap: 24px;
}

.profile-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.user-card {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 32px 20px;
  text-align: center;
  box-shadow: var(--shadow-card);
  margin-bottom: 16px;
}

.user-card h3 {
  margin: 14px 0 4px;
  font-size: 18px;
  color: var(--color-text);
}

.user-card p {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.sidebar-menu {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 8px;
  box-shadow: var(--shadow-card);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item:hover {
  background: #f5f5f5;
  color: var(--color-text);
}

.menu-item.active {
  background: var(--color-primary);
  color: #fff;
}

.profile-content {
  flex: 1;
  min-width: 0;
}

.content-card {
  background: var(--color-bg-white);
  border-radius: var(--radius-card);
  padding: 32px;
  box-shadow: var(--shadow-card);
}

.content-card h2 {
  margin: 0 0 28px;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--color-border);
}

.profile-form {
  max-width: 480px;
}
</style>
